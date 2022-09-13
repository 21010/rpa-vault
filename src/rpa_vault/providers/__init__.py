from ..core.registry import ProviderRegistry
from .azure import AzureVaultProvider


def setup_providers() -> None:
    """Registers all known vault providers with the ProviderRegistry."""
    ProviderRegistry.register("azure", AzureVaultProvider)


# Call it by default to maintain existing behavior for any other importers
setup_providers()
