"""
Azure Key Vault provider implementation.
This module provides the AzureVaultProvider which interacts with the Azure Key Vault API
to manage secrets asynchronously.
"""

import json
import logging
from typing import Any, AsyncIterable, Literal

from azure.core.exceptions import ResourceNotFoundError
from azure.identity.aio import ClientSecretCredential, DefaultAzureCredential
from azure.keyvault.secrets import KeyVaultSecret
from azure.keyvault.secrets.aio import SecretClient

from ..core.exceptions import SecretNotFoundError, VaultAuthenticationError
from ..core.models import Secret
from ..core.protocol import VaultProtocol

logger = logging.getLogger(__name__)


class AzureVaultProvider(VaultProtocol):
    """
    Azure Key Vault implementation of the VaultProtocol (Asynchronous).
    Uses the azure-keyvault-secrets and azure-identity SDKs.
    """

    def __init__(
        self,
        vault_url: str | None = None,
        tenant_id: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
    ) -> None:
        """
        Initializes the AzureVaultProvider and authenticates with Azure.

        Args:
            vault_url (str | None): The URL of the Azure Key Vault. If not provided, it is read from AZURE_VAULT_URL.
            tenant_id (str | None): Azure Tenant ID. If provided alongside client_id/secret,
                it uses ClientSecretCredential.
            client_id (str | None): Azure Client ID (Service Principal).
            client_secret (str | None): Azure Client Secret.

        Raises:
            VaultAuthenticationError: If authentication with the Vault fails.
            ValueError: If vault_url is not provided and AZURE_VAULT_URL is not set.
        """
        import os

        self.vault_url = vault_url or os.environ.get("AZURE_VAULT_URL")
        if not self.vault_url:
            raise ValueError("vault_url must be provided or set via the AZURE_VAULT_URL environment variable.")

        try:
            from typing import Any, cast

            self.credential = cast(Any, self._authenticate(tenant_id, client_id, client_secret))
            debug_mode = os.environ.get("AZURE_SDK_DEBUG", "false").lower() == "true"
            if debug_mode:
                logger.warning("AZURE_SDK_DEBUG is enabled. Sensitive request metadata may be logged.")
            client_kwargs: dict[str, Any] = {"logging_enabled": debug_mode}
            self.client = SecretClient(
                vault_url=self.vault_url,
                credential=self.credential,
                **client_kwargs,
            )
        except Exception as e:
            raise VaultAuthenticationError(f"Failed to authenticate with Azure Key Vault: {e}")

    def _authenticate(
        self,
        tenant_id: str | None,
        client_id: str | None,
        client_secret: str | None,
    ):
        if tenant_id and client_id and client_secret:
            return ClientSecretCredential(tenant_id, client_id, client_secret)
        return DefaultAzureCredential()

    async def get_secrets(self) -> AsyncIterable[Secret]:
        """
        Retrieves all secrets from the Azure Key Vault.

        Returns:
            AsyncIterable[Secret]: An async generator yielding Secret objects.
        """
        import asyncio
        import os

        chunk = []
        chunk_size = int(os.environ.get("AZURE_VAULT_CONCURRENCY", "10"))
        async for p in self.client.list_properties_of_secrets():
            if p.name:
                chunk.append(p.name)

            if len(chunk) >= chunk_size:
                tasks = [self.get_secret(name) for name in chunk]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                for res in results:
                    if isinstance(res, BaseException):
                        logger.error(f"Failed to fetch a secret: {res}")
                    else:
                        yield res
                chunk = []

        if chunk:
            tasks = [self.get_secret(name) for name in chunk]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for res in results:
                if isinstance(res, BaseException):
                    logger.error(f"Failed to fetch a secret: {res}")
                else:
                    yield res

    async def get_secret(self, secret_name: str) -> Secret:
        """
        Retrieves a single secret by name. Automatically parses JSON strings into dicts.

        Args:
            secret_name (str): The name of the secret.

        Returns:
            Secret: The secret object containing the name, secured value, and content type.

        Raises:
            SecretNotFoundError: If the secret is not found.
        """
        try:
            from pydantic import SecretStr

            secret: KeyVaultSecret = await self.client.get_secret(secret_name)
            is_json = secret.properties.content_type in ("json", "application/json")

            value = secret.value if secret.value is not None else ""

            return Secret(
                name=secret_name, value=SecretStr(value), content_type="application/json" if is_json else "text/plain"
            )
        except ResourceNotFoundError:
            raise SecretNotFoundError(f"Secret '{secret_name}' not found in Azure Key Vault.")

    async def set_secret(
        self,
        secret_name: str,
        secret_value: Any,
        content_type: Literal["text/plain", "application/json"] | None = None,
    ) -> None:
        """
        Sets a new secret or updates an existing one. Serializes dicts into JSON strings.

        Args:
            secret_name (str): The name of the secret.
            secret_value (Any): The value to store.
            content_type (Literal["text/plain", "application/json"] | None):
                The content type. Defaults to 'application/json' if secret_value is a dict, else 'text/plain'.
        """
        if content_type is None:
            content_type = "application/json" if isinstance(secret_value, dict) else "text/plain"

        from pydantic import SecretStr

        if isinstance(secret_value, SecretStr):
            value_str = secret_value.get_secret_value()
        elif content_type == "application/json":
            value_str = json.dumps(secret_value)
        else:
            value_str = str(secret_value)

        await self.client.set_secret(name=secret_name, value=value_str, content_type=content_type)

    async def update_secret_property(
        self,
        secret_name: str,
        property_name: str,
        property_value: Any,
    ) -> None:
        """
        Updates a specific property within a JSON-based secret.

        Args:
            secret_name (str): The name of the JSON secret.
            property_name (str): The specific JSON key to update.
            property_value (Any): The new value for the key.

        Raises:
            SecretNotFoundError: If the secret is not found.
            ValueError: If the secret is not of type application/json.
        """
        try:
            secret: KeyVaultSecret = await self.client.get_secret(secret_name)
        except ResourceNotFoundError:
            raise SecretNotFoundError(f"Secret '{secret_name}' not found.")

        if secret.properties.content_type in ("json", "application/json") and secret.value is not None:
            value: dict = json.loads(secret.value)
            value[property_name] = property_value
            await self.set_secret(secret_name, value, content_type="application/json")
        else:
            raise ValueError(f"Cannot update property for secret '{secret_name}' as its content type is not JSON.")

    async def delete_secret(self, secret_name: str) -> None:
        """
        Deletes a secret from the Azure Key Vault.

        Args:
            secret_name (str): The name of the secret to delete.

        Raises:
            SecretNotFoundError: If the secret does not exist.
        """
        try:
            await self.client.delete_secret(secret_name)
        except ResourceNotFoundError:
            raise SecretNotFoundError(f"Secret '{secret_name}' not found.")

    async def close(self) -> None:
        """
        Closes the underlying Azure client session and credentials.
        """
        await self.client.close()
        if hasattr(self, "credential") and hasattr(self.credential, "close"):
            await self.credential.close()
