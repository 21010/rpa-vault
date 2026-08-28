import logging

from rpa_vault.core.exceptions import SecretNotFoundError
from rpa_vault.core.factory import VaultFactory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """
    Demonstrates how to use the `SyncVault` context manager.
    This is perfect for traditional, synchronous Python scripts where
    you don't want to deal with `asyncio` loops manually.
    """
    logger.info("Starting synchronous script...")

    # The context manager automatically initializes the loop and handles teardown
    with VaultFactory.get_sync_provider("azure") as vault:
        try:
            logger.info("Fetching secret 'app-config'...")
            secret = vault.get_secret("app-config")

            # Use the config here
            logger.info(f"Successfully retrieved config. Type: {type(secret.get_value())}")

        except SecretNotFoundError:
            logger.warning("The secret 'app-config' was not found.")

    logger.info("Script finished. Vault connection safely closed.")


if __name__ == "__main__":
    # Example usage: uv run python examples/sync_script.py
    main()
