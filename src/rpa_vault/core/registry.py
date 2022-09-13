"""
Registry for Vault Providers.
Separated from the factory to avoid circular imports.
"""

from typing import Type

from .protocol import VaultProtocol


class ProviderRegistry:
    """
    Maintains a registry of available vault providers.
    """

    _providers: dict[str, Type[VaultProtocol]] = {}

    @classmethod
    def register(cls, name: str, provider_cls: Type[VaultProtocol]) -> None:
        """
        Registers a new vault provider class.

        Args:
            name (str): The unique identifier for the provider (e.g., 'azure', 'aws').
            provider_cls (Type[VaultProtocol]): The class implementing the VaultProtocol interface.
        """
        cls._providers[name] = provider_cls

    @classmethod
    def get(cls, name: str) -> Type[VaultProtocol] | None:
        """
        Gets a registered provider by name.
        """
        return cls._providers.get(name)
