from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from azure.core.exceptions import ResourceNotFoundError

from rpa_vault.core.exceptions import SecretNotFoundError, VaultAuthenticationError
from rpa_vault.providers.azure import AzureVaultProvider


class MockKeyVaultSecret:
    def __init__(self, name, value, content_type="text/plain"):
        self.name = name
        self.value = value

        class Properties:
            def __init__(self, c_type):
                self.content_type = c_type

        self.properties = Properties(content_type)


class MockSecretProperties:
    def __init__(self, name, content_type="text/plain"):
        self.name = name
        self.content_type = content_type


@pytest.fixture
def mock_store():
    return {
        "secret-str": MockKeyVaultSecret("secret-str", "some text", "text/plain"),
        "secret-json": MockKeyVaultSecret("secret-json", '{"login": "user"}', "application/json"),
    }


@pytest.fixture
def mock_client(mock_store):
    async def get_secret(name):
        if name in mock_store:
            return mock_store[name]
        raise ResourceNotFoundError(f"Secret {name} not found")

    async def set_secret(name, value, content_type):
        mock_store[name] = MockKeyVaultSecret(name, value, content_type)

    async def list_properties():
        props = [MockSecretProperties(k, v.properties.content_type) for k, v in mock_store.items()]
        props.append(MockSecretProperties(None))
        for p in props:
            yield p

    client = MagicMock()
    client.get_secret = AsyncMock(side_effect=get_secret)
    client.set_secret = AsyncMock(side_effect=set_secret)
    client.list_properties_of_secrets = MagicMock(side_effect=list_properties)
    return client


@pytest.fixture
def provider(mock_client):
    with (
        patch("rpa_vault.providers.azure.SecretClient", return_value=mock_client),
        patch("rpa_vault.providers.azure.ClientSecretCredential"),
    ):
        return AzureVaultProvider(
            vault_url="https://dummy.vault.azure.net",
            tenant_id="dummy",
            client_id="dummy",
            client_secret="dummy",
        )


def test_auth_default_credential():
    with (
        patch("rpa_vault.providers.azure.SecretClient"),
        patch("rpa_vault.providers.azure.DefaultAzureCredential") as mock_default,
    ):
        AzureVaultProvider(vault_url="https://dummy.vault.azure.net")
        mock_default.assert_called_once()


def test_auth_failure():
    with patch(
        "rpa_vault.providers.azure.SecretClient",
        side_effect=Exception("Connection Error"),
    ):
        with pytest.raises(
            VaultAuthenticationError,
            match="Failed to authenticate with Azure Key Vault",
        ):
            AzureVaultProvider(vault_url="https://dummy.vault.azure.net")


@pytest.mark.asyncio
async def test_get_secrets(provider):
    secrets = [s async for s in provider.get_secrets()]
    assert len(secrets) == 2


@pytest.mark.asyncio
async def test_get_secret_str(provider):
    secret = await provider.get_secret("secret-str")
    assert secret.get_value() == "some text"


@pytest.mark.asyncio
async def test_get_secret_json(provider):
    secret = await provider.get_secret("secret-json")
    assert secret.get_value() == {"login": "user"}


@pytest.mark.asyncio
async def test_get_secret_not_found(provider):
    with pytest.raises(SecretNotFoundError, match="Secret 'missing' not found"):
        await provider.get_secret("missing")


@pytest.mark.asyncio
async def test_set_secret_str(provider, mock_store):
    await provider.set_secret("new-str", "val")
    assert "new-str" in mock_store


@pytest.mark.asyncio
async def test_set_secret_dict(provider, mock_store):
    await provider.set_secret("new-dict", {"a": 1})
    assert "new-dict" in mock_store


@pytest.mark.asyncio
async def test_update_secret_property(provider):
    await provider.update_secret_property("secret-json", "login", "new_user")
    val = await provider.get_secret("secret-json")
    assert val.get_value()["login"] == "new_user"


@pytest.mark.asyncio
async def test_update_secret_property_not_json(provider):
    with pytest.raises(ValueError, match="content type is not JSON"):
        await provider.update_secret_property("secret-str", "key", "val")


@pytest.mark.asyncio
async def test_update_secret_property_not_found(provider):
    with pytest.raises(SecretNotFoundError):
        await provider.update_secret_property("missing", "k", "v")



