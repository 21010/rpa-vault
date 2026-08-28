import asyncio
import logging

from rpa_vault.core.exceptions import VaultAuthenticationError
from rpa_vault.core.factory import VaultFactory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def bulk_migration():
    """
    Demonstrates how to use the high-performance async generator
    to fetch all secrets in bulk and migrate them.
    """
    logger.info("Initializing Azure Vault Provider...")
    provider = VaultFactory.get_provider("azure")

    try:
        # get_secrets() is an asynchronous generator that streams secrets
        # in memory-efficient chunks.
        async for secret in provider.get_secrets():
            logger.info(f"Processing secret: {secret.name}")

            # The value is safely masked in memory!
            # It will print as ********** if accidentally logged
            logger.info(f"Safely wrapped value: {secret.value}")

            # To actually access the payload for the migration target:
            real_payload = secret.get_value()  # noqa: F841

            # TODO: Add your logic here to insert `real_payload` into your destination vault!
            logger.info(f"Successfully migrated: {secret.name}")

    except VaultAuthenticationError as e:
        logger.error(f"Authentication failed: {e}")
    finally:
        # Always close the provider to release underlying HTTP connections
        await provider.close()
        logger.info("Closed Vault Provider.")


if __name__ == "__main__":
    # Example usage: uv run python examples/bulk_migration.py
    asyncio.run(bulk_migration())
