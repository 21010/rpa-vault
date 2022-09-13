import os
import uuid

import pytest

from rpa_vault.core.factory import VaultFactory

# Mark all tests in this file as integration tests
pytestmark = pytest.mark.integration


@pytest.fixture
def azure_vault_url():
    url = os.environ.get("AZURE_VAULT_URL")
    if not url:
        pytest.skip("AZURE_VAULT_URL environment variable is not set")
    return url


@pytest.fixture
def azure_credentials():
    return {
        "tenant_id": os.environ.get("AZURE_TENANT_ID"),
        "client_id": os.environ.get("AZURE_CLIENT_ID"),
        "client_secret": os.environ.get("AZURE_CLIENT_SECRET"),
    }


@pytest.fixture
def provider(azure_vault_url, azure_credentials):
    return VaultFactory.get_provider(
        "azure",
        vault_url=azure_vault_url,
        tenant_id=azure_credentials["tenant_id"],
        client_id=azure_credentials["client_id"],
        client_secret=azure_credentials["client_secret"],
    )


@pytest.fixture
async def temp_secret(provider):
    """Fixture that generates a unique secret name and cleans it up after the test."""
    secret_name = f"integration-test-secret-{uuid.uuid4().hex[:8]}"
    yield secret_name

    # Teardown: ensure the secret is deleted
    try:
        await provider.delete_secret(secret_name)
    except Exception:
        pass  # If it's already deleted or doesn't exist, ignore


@pytest.fixture
async def temp_json_secret(provider):
    """Fixture that generates a unique JSON secret name and cleans it up after the test."""
    secret_name = f"integration-test-json-{uuid.uuid4().hex[:8]}"
    yield secret_name

    try:
        await provider.delete_secret(secret_name)
    except Exception:
        pass


@pytest.mark.asyncio
async def test_azure_integration_basic_set_get(provider, temp_secret):
    """Test setting and retrieving a plain text secret."""
    await provider.set_secret(temp_secret, "hello integration", content_type="text/plain")
    val = await provider.get_secret(temp_secret)
    assert val == "hello integration"


@pytest.mark.asyncio
async def test_azure_integration_json_set_get(provider, temp_json_secret):
    """Test setting and retrieving a JSON secret."""
    json_value = {"key": "value"}
    await provider.set_secret(temp_json_secret, json_value, content_type="application/json")
    val = await provider.get_secret(temp_json_secret)
    assert val == json_value


@pytest.mark.asyncio
async def test_azure_integration_update_property(provider, temp_secret):
    """Test updating the properties of a secret."""
    await provider.set_secret(temp_secret, "initial value", content_type="text/plain")
    await provider.update_secret_property(temp_secret, "integration-test-secret", "updated")
    val = await provider.get_secret(temp_secret)
    assert val == "updated"


@pytest.mark.asyncio
async def test_azure_integration_backup_restore(provider, temp_secret, tmp_path):
    """Test backing up and restoring a secret."""
    # Setup initial secret
    await provider.set_secret(temp_secret, "backup test", content_type="text/plain")

    # Backup to a safe temporary path
    backup_file = tmp_path / "backup.dat"
    await provider.backup_secret(temp_secret, str(backup_file))

    # Delete it
    await provider.delete_secret(temp_secret)

    # Restore it
    await provider.restore_secret(str(backup_file))

    # Verify restoration
    val = await provider.get_secret(temp_secret)
    assert val == "backup test"
