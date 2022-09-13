import logging

# Just an example, you can use any RPA framework
# pyrefly: ignore [missing-import]
from robocorp.tasks import task

# Import RPA Vault components
from rpa_vault.core.factory import VaultFactory

# Optional: configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fetch_credentials_and_process() -> None:
    """
    Helper to interact with RPA Vault synchronously.
    RPA Vault natively handles async calls securely under the hood,
    but exposes a simple synchronous wrapper via get_sync_provider.
    """
    # 1. The vault factory dynamically lazy-loads built-in providers!

    # 2. Configure the Vault Provider
    # By default, it will instantiate the 'azure' provider.
    # It will automatically pick up AZURE_VAULT_URL from the environment.
    # It also automatically falls back to Managed Identity/DefaultAzureCredential
    # if AZURE_TENANT_ID, AZURE_CLIENT_ID, and AZURE_CLIENT_SECRET are not provided.

    logger.info("Connecting to Azure Key Vault...")
    with VaultFactory.get_sync_provider() as vault:
        # 3. Retrieve a secret (e.g., JSON credentials)
        # The library automatically parses JSON strings into Python dictionaries for you.
        secret_name = "robot-erp-credentials"  # nosec B105
        logger.info(f"Fetching secret: '{secret_name}'")

        try:
            secret = vault.get_secret(secret_name)

            # 4. Use the secret in your automation
            credentials = secret.get_value()
            if isinstance(credentials, dict):
                username = credentials.get("username")
                password = credentials.get("password")  # noqa: F841

                logger.info(f"Successfully retrieved credentials for user: {username}")

                # --- Place your core automation logic here ---
                # e.g., browser.goto("https://erp.example.com")
                #       browser.fill("input[name='user']", username)
                #       browser.fill("input[name='pass']", password)

            else:
                logger.warning(
                    f"Expected a JSON dictionary, but got a plain string. Content type: {secret.content_type}"
                )

        except Exception as e:
            logger.error(f"Failed to fetch or use secret '{secret_name}': {e}")
            raise


@task
def run_robot_with_vault() -> None:
    """
    Robocorp task entry point.
    Demonstrates how to fetch and use secrets securely from RPA Vault.
    """
    logger.info("Starting Robocorp automation task using RPA Vault...")

    # We can now just call the synchronous helper directly!
    fetch_credentials_and_process()

    logger.info("Task completed successfully!")
