"""
Domain-specific exceptions for the rpa-vault library.
These custom exceptions allow downstream consumers to handle vault-related errors predictably.
"""


class VaultError(Exception):
    """
    Base exception for all Vault operations.
    Catch this to handle any error raised specifically by the rpa-vault library.
    """

    pass


class SecretNotFoundError(VaultError):
    """
    Raised when a requested secret is not found in the vault.
    This can occur during retrieval, property updates, or backups.
    """

    pass


class VaultAuthenticationError(VaultError):
    """
    Raised when authentication with the underlying vault provider fails.
    Usually indicates missing or invalid credentials (e.g., bad client_secret).
    """

    pass
