from typing import AsyncIterable

import pytest

from rpa_vault.core.factory import VaultFactory
from rpa_vault.core.models import Secret
from rpa_vault.core.protocol import VaultProtocol


class DummyProvider(VaultProtocol):
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    async def get_secrets(self) -> AsyncIterable[Secret]:
        yield Secret(name="dummy", value="val", content_type="text/plain")


def test_factory_register_and_get():
    VaultFactory.register("dummy", DummyProvider)
    provider = VaultFactory.get_provider("dummy", test_arg="value")
    assert isinstance(provider, DummyProvider)
    assert provider.kwargs["test_arg"] == "value"


def test_factory_get_unregistered():
    with pytest.raises(ValueError, match="Vault provider 'missing' is not registered."):
        VaultFactory.get_provider("missing")
