import asyncio

from rpa_vault.core.factory import VaultFactory


async def lifecycle_demo():
    provider = VaultFactory.get_provider("azure")

    # 1. Create (Set)
    payload = {"username": "admin", "password": "old_password"}
    await provider.set_secret("db-credentials", payload)
    print("Secret created successfully.")

    # 2. Read (Get)
    secret = await provider.get_secret("db-credentials")
    creds = secret.get_value()  # Returns a masked SecretDict!
    print(f"Username retrieved: {creds['username']}")

    # 3. Update (Modify property)
    # Easily rotate a specific key inside the JSON payload without overwriting the rest
    await provider.update_secret_property("db-credentials", "password", "new_secure_password!")
    print("Secret password property updated.")

    # 4. Delete
    await provider.delete_secret("db-credentials")
    print("Secret deleted.")

    await provider.close()


if __name__ == "__main__":
    asyncio.run(lifecycle_demo())
