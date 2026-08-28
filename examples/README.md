# RPA Vault Examples

This directory contains examples showing how to use `rpa_vault` in real-world scenarios.

## Files

- [`botcity_bot.py`](./botcity_bot.py): Shows how to integrate securely with [BotCity](https://botcity.dev/) desktop or web bots using the synchronous context manager.
- [`bulk_migration.py`](./bulk_migration.py): Demonstrates how to use the high-performance async generator `get_secrets()` to stream and migrate secrets in bulk.
- [`crud_example.py`](./crud_example.py): A complete demonstration of the secret lifecycle (Create, Read, Update, Delete) using the async provider.
- [`fastapi_app.py`](./fastapi_app.py): Shows how to integrate the async provider into a FastAPI application lifecycle (startup/shutdown events).
- [`robocorp_task.py`](./robocorp_task.py): Demonstrates how to integrate `rpa_vault` with [Robocorp Automation Framework](https://robocorp.com/docs/development-guide/framework) using the `@task` decorator.
- [`sync_script.py`](./sync_script.py): An example of using the `SyncVault` context manager for traditional, synchronous Python scripts where `asyncio` is not needed.

## Running the Examples

1. Ensure you have the required dependencies installed (e.g., `uv sync`).
2. Set your Azure Key Vault environment variables:
   ```bash
   set AZURE_VAULT_URL=https://your-vault-name.vault.azure.net/
   ```
3. Run the examples:
   ```bash
   uv run python examples/bulk_migration.py
   uv run python examples/crud_example.py
   uv run python examples/sync_script.py
   uv run python examples/botcity_bot.py
   uv run python examples/robocorp_task.py
   uv run uvicorn examples.fastapi_app:app --reload
   ```
