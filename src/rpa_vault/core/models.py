import json
from typing import Any, Literal

from pydantic import BaseModel, SecretStr


class SecretDict(dict):
    def __repr__(self) -> str:
        return "SecretDict(**********)"

    def __str__(self) -> str:
        return "**********"


class SecretList(list):
    def __repr__(self) -> str:
        return "SecretList(**********)"

    def __str__(self) -> str:
        return "**********"


class Secret(BaseModel):
    """
    Represents a vault secret.

    Attributes:
        name: The unique identifier/name of the secret.
        value: The decrypted value of the secret, securely wrapped in SecretStr.
        content_type: The format of the secret's value ('text/plain' or 'application/json'). Defaults to 'text/plain'.
    """

    name: str
    value: SecretStr
    content_type: Literal["text/plain", "application/json"] = "text/plain"

    def get_value(self) -> Any:
        """
        Retrieves the unwrapped value. Automatically parses JSON if the content type is 'application/json'.
        """
        val_str = self.value.get_secret_value()
        if self.content_type == "application/json":
            try:
                parsed = json.loads(val_str)
                if isinstance(parsed, dict):
                    return SecretDict(parsed)
                elif isinstance(parsed, list):
                    return SecretList(parsed)
                return parsed
            except json.JSONDecodeError:
                pass
        return val_str
