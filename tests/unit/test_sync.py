from unittest.mock import AsyncMock

import pytest

from rpa_vault.core.models import Secret
from rpa_vault.core.protocol import VaultProtocol
from rpa_vault.core.sync import SyncVault


@pytest.fixture
def mock_provider():
    provider = AsyncMock(spec=VaultProtocol)
    return provider


def test_sync_vault_context_manager(mock_provider):
    with SyncVault(mock_provider) as vault:
        assert not vault._is_closed
    assert vault._is_closed
    mock_provider.close.assert_called_once()


def test_sync_vault_get_secrets(mock_provider):
    async def mock_generator():
        yield Secret(name="test1", value="val1")
        yield Secret(name="test2", value="val2")

    mock_provider.get_secrets.return_value = mock_generator()

    with SyncVault(mock_provider) as vault:
        secrets = list(vault.get_secrets())
        
    assert len(secrets) == 2
    assert secrets[0].name == "test1"
    assert secrets[1].name == "test2"


def test_sync_vault_get_secret(mock_provider):
    mock_provider.get_secret.return_value = Secret(name="test", value="val")
    with SyncVault(mock_provider) as vault:
        secret = vault.get_secret("test")
    assert secret.name == "test"
    mock_provider.get_secret.assert_called_once_with("test")


def test_sync_vault_set_secret(mock_provider):
    with SyncVault(mock_provider) as vault:
        vault.set_secret("test", "val", "text/plain")
    mock_provider.set_secret.assert_called_once_with("test", "val", "text/plain")


def test_sync_vault_update_secret_property(mock_provider):
    with SyncVault(mock_provider) as vault:
        vault.update_secret_property("test", "key", "val")
    mock_provider.update_secret_property.assert_called_once_with("test", "key", "val")



