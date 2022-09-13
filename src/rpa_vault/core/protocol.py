"""
Defines the standard VaultProtocol interface.
All custom vault providers must implement this Protocol to be compatible with rpa-vault.

Lifecycle: Providers may require async initialization or cleanup. Consumers should
always call `await vault.close()` when finished with the provider, or use a framework
that manages this lifecycle.
"""

from typing import Any, AsyncIterable, Literal, Protocol

from .models import Secret


class VaultProtocol(Protocol):
    """
    Protocol defining the standard interface for all Vault providers.
    """

    def get_secrets(self) -> AsyncIterable[Secret]:
        """
        Returns all secrets from the vault.

        Returns:
            AsyncIterable[Secret]: An async generator yielding Secret objects.
        """
        ...

    async def get_secret(self, secret_name: str) -> Secret:
        """
        Retrieves a single secret by name.

        Args:
            secret_name (str): The name of the secret to retrieve.

        Returns:
            Secret: The secret object containing the name, secured value, and content type.

        Raises:
            SecretNotFoundError: If the secret does not exist in the vault.
        """
        ...

    async def set_secret(
        self,
        secret_name: str,
        secret_value: Any,
        content_type: Literal["text/plain", "application/json"] | None = None,
    ) -> None:
        """
        Sets a secret's value in the vault.

        Args:
            secret_name (str): The name of the secret to set.
            secret_value (Any): The value to store.
            content_type (Literal["text/plain", "application/json"] | None):
                The content type of the secret. If None, it is inferred from secret_value.
        """
        ...

    async def update_secret_property(
        self,
        secret_name: str,
        property_name: str,
        property_value: Any,
    ) -> None:
        """
        Updates a specific property within a JSON-based secret.

        Args:
            secret_name (str): The name of the JSON secret to update.
            property_name (str): The key in the JSON object to modify or add.
            property_value (Any): The new value for the given key.

        Raises:
            SecretNotFoundError: If the secret does not exist.
            ValueError: If the secret's content_type is not JSON.
        """
        ...

    async def delete_secret(self, secret_name: str) -> None:
        """
        Deletes a secret from the vault.

        Args:
            secret_name (str): The name of the secret to delete.

        Raises:
            SecretNotFoundError: If the secret does not exist.
        """
        ...



    async def close(self) -> None:
        """
        Closes the underlying provider connection and cleans up any resources.
        Must be called when the provider is no longer needed.
        """
        ...
