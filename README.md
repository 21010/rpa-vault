# RPA Vault

![RPA Compatible](https://img.shields.io/badge/RPA-Compatible-2ea44f)
![Robocorp Compatible](https://img.shields.io/badge/Robocorp-Compatible-ff4f5e)
![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
[![CI](https://github.com/21010/rpa-vault/actions/workflows/ci.yml/badge.svg)](https://github.com/21010/rpa-vault/actions/workflows/ci.yml)
![Zero Trust](https://img.shields.io/badge/Security-Zero%20Trust-blueviolet)
![ISO 27001 Aligned](https://img.shields.io/badge/Compliance-ISO%2027001%20Aligned-success)
![100% Secret Masking](https://img.shields.io/badge/Protection-100%25%20Secret%20Masking-critical)

**rpa-vault** is an extensible Python library designed to simplify secrets management across cloud vault providers (like Azure Key Vault) within Robotic Process Automation (RPA) workflows. 

It provides a unified, highly secure, and purely programmatic CRUD (Create, Read, Update, Delete) interface to seamlessly manage credentials for your RPA robots. Under the hood, it leverages **Pydantic** for data validation and masking, preventing accidental leakage of secrets in production environments.

## Core Features
- **Unified Abstraction:** Interact with different providers (e.g., Azure Key Vault) using a single Protocol.
- **Synchronous & Asynchronous:** Built async-first for performance, but includes a robust `SyncVault` context manager for traditional synchronous RPA bots.
- **Enterprise Security:** Pydantic `SecretStr` models natively mask values in memory to prevent accidental log leakage.
- **RPA-Ready**: Easily consumable within Robocorp Action Server, simple python robots, or standalone CI/CD pipelines.

---

## Installation

Add `rpa-vault` to your project using your preferred package manager. Since it is designed for modern Python environments, we recommend `uv` or `pip`:

```bash
uv add rpa-vault
# or
pip install rpa-vault
```

*(Note: If you are installing directly from a Git repository, use `uv add git+https://github.com/21010/rpa-vault.git`)*

---

## Usage Scenarios

You can integrate `rpa-vault` into various Python environments. 

### 1. Robocorp and BotCity Bots
Robocorp and BotCity bots typically run synchronously. The best way to use `rpa-vault` here is via the `SyncVault` context manager, which completely hides event loop management and safely tears down resources when the block exits.

```python
from rpa_vault.core.factory import VaultFactory

def get_db_credentials():
    # Automatically manages connections and teardown!
    with VaultFactory.get_sync_provider("azure") as vault:
        # get_value() automatically parses JSON if the secret is stored as application/json
        creds = vault.get_secret("database-creds").get_value()
        
    return creds["username"], creds["password"]
```

### 2. Regular Python Scripts
If you are writing a standard asynchronous Python script or application (e.g., FastAPI backend, or a bulk migration script), you can use the async provider directly to benefit from high-concurrency streaming.

```python
import asyncio
from rpa_vault.core.factory import VaultFactory

async def migrate_secrets():
    provider = VaultFactory.get_provider("azure")
    
    # get_secrets() is a memory-efficient asynchronous generator!
    async for secret in provider.get_secrets():
        print(f"Migrating secret: {secret.name}")
        
    await provider.close()

if __name__ == "__main__":
    asyncio.run(migrate_secrets())
```

### 3. `uv` Projects
If you are managing your project via `uv` (Astral's fast Python package installer), add `rpa-vault` to your `pyproject.toml` dependencies, and run:
```bash
uv sync
uv run python my_bot.py
```

### 4. Full Secret Lifecycle (CRUD)
Because `rpa-vault` provides a pure CRUD interface, managing the full lifecycle of a secret is highly intuitive. Here is a complete example of creating, reading, updating, and deleting a JSON secret:

```python
import asyncio
from rpa_vault.core.factory import VaultFactory

async def lifecycle_demo():
    provider = VaultFactory.get_provider("azure")

    # 1. Create (Set)
    payload = {"username": "admin", "password": "old_password"}
    await provider.set_secret("db-credentials", payload)

    # 2. Read (Get)
    secret = await provider.get_secret("db-credentials")
    creds = secret.get_value() # Returns a masked SecretDict!
    print(f"Username: {creds['username']}")

    # 3. Update (Modify property)
    # Easily rotate a specific key inside the JSON payload without overwriting the rest
    await provider.update_secret_property("db-credentials", "password", "new_secure_password!")

    # 4. Delete
    await provider.delete_secret("db-credentials")

    await provider.close()

if __name__ == "__main__":
    asyncio.run(lifecycle_demo())
```

### 5. Error Handling
RPA bots must be resilient. The library catches underlying SDK errors and throws domain-specific exceptions (`SecretNotFoundError`, `VaultAuthenticationError`), allowing you to handle missing configurations gracefully without importing cloud-specific exceptions.

```python
from rpa_vault.core.exceptions import SecretNotFoundError, VaultAuthenticationError

try:
    with VaultFactory.get_sync_provider("azure") as vault:
        optional_config = vault.get_secret("feature-flags")
except SecretNotFoundError:
    print("Feature flags not found. Using defaults.")
except VaultAuthenticationError as e:
    print(f"Critical Auth Error: {e}")
```

> **Note:** For complete, runnable code including FastAPI, BotCity, and Robocorp integrations, check out the [`/examples` directory](./examples/).

---

## Environment Configuration

The library uses environment variables for configuration. Because we prioritize a zero-trust model, `rpa-vault` no longer loads `.env` files automatically (to prevent supply chain risks with `python-dotenv`). You must pass these to your environment directly (via Docker, GitHub Actions, Robocorp Vault, or your shell).

- `AZURE_VAULT_URL` **(Required)**: The base URL of your Key Vault (e.g., `https://my-vault.vault.azure.net/`).
- `AZURE_VAULT_CONCURRENCY` *(Optional)*: Controls how many secrets are fetched concurrently during a bulk `get_secrets()` operation. Defaults to `10`.
- `AZURE_SDK_DEBUG` *(Optional)*: Set to `true` to enable verbose logging in the Azure SDK (Not recommended in production as it may log sensitive HTTP headers).

---

## Azure Authorization

`rpa-vault` delegates authorization securely to Azure's `DefaultAzureCredential`. This means your bots can run anywhere without changing the code, relying entirely on the environment.

1. **Local Development (Developer Machine)**:
   Just run `az login` using the Azure CLI. The library will automatically pick up your logged-in Entra ID account and use it to access the Key Vault. No environment variables required!
   
2. **Unattended Bots (Azure VMs / Azure Container Apps)**:
   Use **Managed Identities**. Assign a System-Assigned or User-Assigned Managed Identity to your Bot Runner VM and grant it "Key Vault Secrets User" access. The library will authenticate automatically with zero credentials stored.

3. **External Systems (Robocorp Cloud / AWS / On-Premise)**:
   If you cannot use Managed Identities, you can authenticate using an Azure Service Principal by providing the following standard environment variables:
   - `AZURE_TENANT_ID`
   - `AZURE_CLIENT_ID`
   - `AZURE_CLIENT_SECRET`

---

## Security Posture

`rpa-vault` has been heavily audited and hardened for enterprise use:

1. **Strict CRUD API:** The library acts as a thin, purely programmatic conduit to the Vault. Local file export features and CLIs have been explicitly removed to prevent credential dumping or CSV injection vulnerabilities.
2. **Log Leakage Prevention:** All secrets are returned wrapped in Pydantic `SecretStr`, `SecretDict`, or `SecretList` objects. If a developer accidentally logs the response to `stdout` (`print(secret)`), it will safely output `**********` instead of the raw password.
3. **Least Privilege & Zero-Trust:** By delegating to `DefaultAzureCredential`, the library avoids handling plain-text credentials for authentication. 
4. **Dependency Minimalism:** We enforce strict supply-chain security by relying exclusively on official Azure SDKs and `pydantic`. No extraneous CLI parsing or cryptography libraries are included.

### Encryption & Data States

Understanding how your sensitive data is handled at every stage of the pipeline is critical for enterprise compliance:

- **Data at Rest:** `rpa-vault` does **not** store secrets locally on the disk. All secrets are stored securely inside Azure Key Vault, which encrypts data at rest using Microsoft's FIPS 140-2 validated Hardware Security Modules (HSMs).
- **Data in Transit:** All communication between your bot/machine and the Azure Key Vault is conducted over strictly enforced **TLS 1.2+ (HTTPS)**. The official Azure SDK handles this natively, ensuring no payloads are sent in plaintext.
- **Data in Memory:** Once the secret is fetched into the Python runtime, it is immediately wrapped in Pydantic `SecretStr` or custom `SecretDict` models. This guarantees that the plain text is obscured (outputting `**********`) if the object is accidentally written to standard output, logs, or caught in an exception traceback. To access the real value in memory, developers must explicitly call `.get_secret_value()` or unpack the dictionary directly where needed.

---

## Extending with Custom Providers

`rpa-vault` adheres to the Open/Closed Principle. To add support for a new provider (e.g., AWS Secrets Manager, HashiCorp Vault), you don't need to fork or modify the core code.

1. Create a class that implements the `VaultProtocol` from `rpa_vault.core.protocol`.
2. Register it with the `VaultFactory`.

```python
from rpa_vault.core.protocol import VaultProtocol
from rpa_vault.core.factory import VaultFactory

class HashiCorpProvider(VaultProtocol):
    async def get_secret(self, secret_name: str):
        # Implementation here
        pass
    # ... implement other protocol methods ...

# Register the provider
VaultFactory.register("hashicorp", HashiCorpProvider)

# Use it identically to Azure!
provider = VaultFactory.get_provider("hashicorp")
```

---

## Testing & Local Development

The testing suite is comprehensive and split into two tiers: **Unit Tests** and **Integration Tests**. We use `pytest` and `pytest-asyncio`.

### 1. Unit Tests (Local Mocking)
Unit tests use `AsyncMock` to completely mock external dependencies and the Azure SDK. They run instantly without network connectivity, making them perfect for CI pipelines.

If you are building your own RPA bot and want to write tests without real Azure credentials, you can mock the `VaultFactory` similarly!

```bash
uv run pytest tests/unit/
```

### 2. Integration Tests
Integration tests run against a real, live backend to ensure the API contracts work in the real world. Because integration tests mutate a real Vault, they are safely skipped by default unless your environment is configured.

```bash
# Ensure AZURE_VAULT_URL is set in your environment
uv run pytest -m "integration"
```
*(Note: If `AZURE_VAULT_URL` is omitted, Pytest will gracefully skip integration tests instead of failing).*
