from contextlib import asynccontextmanager

# pyrefly: ignore [missing-import]
from fastapi import FastAPI, HTTPException

from rpa_vault.core.exceptions import SecretNotFoundError
from rpa_vault.core.factory import VaultFactory

# Store the provider instance globally for the app lifecycle
vault_provider = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global vault_provider
    # Initialize the Azure Key Vault provider on startup
    vault_provider = VaultFactory.get_provider("azure")
    yield
    # Safely close the provider on shutdown
    if vault_provider:
        await vault_provider.close()


app = FastAPI(lifespan=lifespan)


@app.get("/config/{secret_name}")
async def get_config(secret_name: str):
    """
    Endpoint to retrieve a configuration from the Vault securely.
    """
    try:
        # Fetch the secret
        # pyrefly: ignore [missing-attribute]
        secret = await vault_provider.get_secret(secret_name)

        # NOTE: Returning the raw value over HTTP is generally a security risk!
        # This is just an example of how to access the value.
        # In a real app, you would use this value internally to connect to a DB, etc.
        return {"status": "success", "secret_name": secret_name, "value_length": len(str(secret.get_value()))}
    except SecretNotFoundError:
        raise HTTPException(status_code=404, detail="Secret not found in Vault")


# Run with: uv run uvicorn examples.fastapi_app:app --reload
