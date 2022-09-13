import json

import pytest
from pydantic import SecretStr

from rpa_vault.core.models import Secret, SecretDict, SecretList


def test_secret_dict_repr():
    sd = SecretDict({"key": "value"})
    assert repr(sd) == "SecretDict(**********)"
    assert str(sd) == "**********"
    assert sd["key"] == "value"


def test_secret_list_repr():
    sl = SecretList(["item1", "item2"])
    assert repr(sl) == "SecretList(**********)"
    assert str(sl) == "**********"
    assert sl[0] == "item1"


def test_secret_get_value_plain_text():
    secret = Secret(name="my_secret", value=SecretStr("plain_text_value"), content_type="text/plain")
    assert secret.get_value() == "plain_text_value"


def test_secret_get_value_json_dict():
    secret = Secret(name="my_json_secret", value=SecretStr('{"foo": "bar"}'), content_type="application/json")
    val = secret.get_value()
    assert isinstance(val, SecretDict)
    assert val["foo"] == "bar"


def test_secret_get_value_json_list():
    secret = Secret(name="my_list_secret", value=SecretStr('["foo", "bar"]'), content_type="application/json")
    val = secret.get_value()
    assert isinstance(val, SecretList)
    assert val[0] == "foo"
    assert val[1] == "bar"


def test_secret_get_value_json_primitive():
    secret = Secret(name="my_prim_secret", value=SecretStr('"string_value"'), content_type="application/json")
    val = secret.get_value()
    assert val == "string_value"
    assert not isinstance(val, (SecretDict, SecretList))


def test_secret_get_value_invalid_json_fallback():
    secret = Secret(name="my_invalid_secret", value=SecretStr('{foo: "bar"}'), content_type="application/json")
    val = secret.get_value()
    # Should fallback to returning the raw string if JSON is invalid
    assert val == '{foo: "bar"}'
