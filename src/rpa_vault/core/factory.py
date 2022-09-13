"""
Provides a factory for registering and instantiating Vault Providers dynamically.
"""

from typing import Type

from .protocol import VaultProtocol
from .registry import ProviderRegistry
from .sync import SyncVault


class VaultFactory:
    """
    Factory class responsible for maintaining a registry of available vault providers
    and instantiating them on demand.
    """

    @classmethod
    def register(cls, name: str, provider_cls: Type[VaultProtocol]) -> None:
        """
        Registers a new vault provider class in the factory.

        Args:
            name (str): The unique identifier for the provider (e.g., 'azure', 'aws').
            provider_cls (Type[VaultProtocol]): The class implementing the VaultProtocol interface.
        """
        ProviderRegistry.register(name, provider_cls)

    @classmethod
    def get_provider(cls, name: str | None = None, **kwargs) -> VaultProtocol:
        """
        Instantiates and returns a vault provider by its registered name.

        Args:
            name (str | None): The unique identifier of the registered provider.
                Defaults to the DEFAULT_VAULT_PROVIDER environment variable, or "azure".
            **kwargs: Arbitrary keyword arguments passed to the provider's constructor
                (e.g., vault_url, tenant_id).

        Returns:
            VaultProtocol: An instance of the requested vault provider.

        Raises:
            ValueError: If the requested provider name has not been registered.
        """
        import os

        name = name or os.environ.get("DEFAULT_VAULT_PROVIDER", "azure")
        provider_cls = ProviderRegistry.get(name)

        # Lazy-load built-in providers if not found
        if not provider_cls:
            try:
                from ..providers import setup_providers

                setup_providers()
                provider_cls = ProviderRegistry.get(name)
            except ImportError as e:
                import logging

                logging.getLogger(__name__).warning(f"Failed to lazy-load providers: {e}")

        if not provider_cls:
            raise ValueError(f"Vault provider '{name}' is not registered.")
        return provider_cls(**kwargs)

    @classmethod
    def get_sync_provider(cls, name: str | None = None, **kwargs) -> SyncVault:
        """
        Instantiates and returns a synchronous wrapper for the requested vault provider.

        Args:
            name (str): The unique identifier of the registered provider. Defaults to "azure".
            **kwargs: Arbitrary keyword arguments passed to the provider's constructor.

        Returns:
            SyncVault: A synchronous wrapper exposing the provider's functionality.
        """
        async_provider = cls.get_provider(name, **kwargs)
        return SyncVault(async_provider)
