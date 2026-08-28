# pyrefly: ignore [missing-import]
from botcity.core import DesktopBot

from rpa_vault.core.exceptions import SecretNotFoundError
from rpa_vault.core.factory import VaultFactory


class MyBot(DesktopBot):
    def action(self, execution=None):
        print("BotCity RPA Bot Started")

        # BotCity bots are typically synchronous, so we use the SyncVault context manager
        # It handles connecting to Azure and safely tearing down resources when finished!
        with VaultFactory.get_sync_provider("azure") as vault:
            try:
                # Fetching the SAP credentials securely
                print("Fetching credentials from Azure Key Vault...")
                secret = vault.get_secret("sap-login")

                # Retrieve the masked dictionary
                creds = secret.get_value()  # noqa: F841

                print("Credentials retrieved successfully!")

                # Example: using the credentials in a Desktop automation
                # self.execute(r"C:\\SAP\\saplogon.exe")
                # self.type_keys(creds["username"])
                # self.type_keys(creds["password"])

            except SecretNotFoundError:
                print("Error: The 'sap-login' secret was not found in the vault.")

        print("Bot completed!")


if __name__ == "__main__":
    # Initialize and run the bot
    MyBot.main()
