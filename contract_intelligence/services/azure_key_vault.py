"""
Azure Key Vault service implementation.

Provides secure secret retrieval.
"""

from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

from contract_intelligence.config.settings import settings
from contract_intelligence.services.base import KeyVaultService
from contract_intelligence.utils.exceptions import AzureServiceError
from contract_intelligence.utils.logging import get_logger

logger = get_logger(__name__)


class AzureKeyVaultService(KeyVaultService):
    """Azure Key Vault service implementation."""

    def __init__(self) -> None:
        """Initialize the Key Vault client."""
        try:
            credential = DefaultAzureCredential()
            self.client = SecretClient(
                vault_url=settings.key_vault.url,
                credential=credential,
            )
            logger.info("Azure Key Vault service initialized", vault_url=settings.key_vault.url)
        except Exception as e:
            logger.error("Failed to initialize Key Vault service", error=str(e))
            raise AzureServiceError(f"Failed to initialize Key Vault service: {e}") from e

    def get_secret(self, secret_name: str) -> str:
        """
        Retrieve a secret from key vault.

        Args:
            secret_name: Name of the secret.

        Returns:
            Secret value.

        Raises:
            AzureServiceError: If secret retrieval fails.
        """
        try:
            logger.info("Retrieving secret", secret_name=secret_name)

            secret = self.client.get_secret(secret_name)
            secret_value = secret.value

            if not secret_value:
                raise AzureServiceError(f"Secret '{secret_name}' is empty")

            logger.info("Secret retrieved successfully", secret_name=secret_name)
            return secret_value

        except Exception as e:
            logger.error("Secret retrieval failed", secret_name=secret_name, error=str(e))
            raise AzureServiceError(f"Secret retrieval failed: {e}") from e