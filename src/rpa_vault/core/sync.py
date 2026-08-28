"""
Provides a synchronous wrapper around the asynchronous VaultProtocol.
Useful for typical RPA tasks (e.g., Robocorp) where the execution model is synchronous.
"""

import asyncio
from typing import Any, Iterable, Literal

from .models import Secret
from .protocol import VaultProtocol


class SyncVault:
    """
    A synchronous proxy class for any VaultProtocol implementation.
    Automatically manages a persistent event loop and wraps all asynchronous calls.
    Supports usage as a context manager (recommended) and auto-closes resources upon garbage collection.
    """

    def __init__(self, async_provider: VaultProtocol):
        self._provider = async_provider
        self._loop = asyncio.new_event_loop()
        self._is_closed = False

    def __enter__(self) -> "SyncVault":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()

    def close(self) -> None:
        """
        Closes the underlying provider and cleans up the event loop.
        """
        if not self._is_closed:
            if not self._loop.is_closed():
                self._loop.run_until_complete(self._provider.close())
                self._loop.close()
            self._is_closed = True

    def get_secrets(self) -> Iterable[Secret]:
        """
        Returns all secrets from the vault synchronously.

        Returns:
            Iterable[Secret]: A list of Secret objects.
        """

        async def _collect() -> list[Secret]:
            return [s async for s in self._provider.get_secrets()]

        return self._loop.run_until_complete(_collect())

    def get_secret(self, secret_name: str) -> Secret:
        """
        Retrieves a single secret by name.

        Args:
            secret_name (str): The name of the secret to retrieve.

        Returns:
            Secret: The secret object containing the name, secured value, and content type.
        """
        return self._loop.run_until_complete(self._provider.get_secret(secret_name))

    def set_secret(
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
        self._loop.run_until_complete(self._provider.set_secret(secret_name, secret_value, content_type))

    def update_secret_property(
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
        """
        self._loop.run_until_complete(self._provider.update_secret_property(secret_name, property_name, property_value))

    def delete_secret(self, secret_name: str) -> None:
        """
        Deletes a secret from the vault.

        Args:
            secret_name (str): The name of the secret to delete.
        """
        self._loop.run_until_complete(self._provider.delete_secret(secret_name))
