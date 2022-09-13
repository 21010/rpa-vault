# RPA Vault Examples

This directory contains examples showing how to use `rpa_vault` in real-world scenarios.

## Files

- [`robocorp_task.py`](./robocorp_task.py): Demonstrates how to integrate `rpa_vault` with [Robocorp Automation Framework](https://robocorp.com/docs/development-guide/framework) using the `@task` decorator. It shows how to bridge the synchronous nature of Robocorp tasks with the asynchronous, high-performance fetching capabilities of RPA Vault.

## Running the Examples

1. Ensure you have the required dependencies installed (e.g., `robocorp-tasks`).
2. Set your Azure Key Vault environment variables:
   ```bash
   set AZURE_VAULT_URL=https://your-vault-name.vault.azure.net/
   # set AZURE_TENANT_ID, AZURE_CLIENT_ID, and AZURE_CLIENT_SECRET if you are not using Managed Identity
   ```
3. Run the task:
   ```bash
   python -m robocorp.tasks run examples/robocorp_task.py
   ```
