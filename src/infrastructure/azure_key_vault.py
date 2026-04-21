"""Azure Key Vault adapter implementing `ISecretProvider`."""
from __future__ import annotations

from azure.core.exceptions import ResourceNotFoundError
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

from src.interfaces import ISecretProvider
from src.utils import SecretNotFoundError, with_retry


class AzureKeyVaultSecretProvider(ISecretProvider):
    """Reads secrets from Azure Key Vault using `DefaultAzureCredential`.

    DefaultAzureCredential supports Managed Identity in Azure and developer
    credentials locally — so the same code works in every environment.
    """

    def __init__(self, vault_url: str) -> None:
        self._client = SecretClient(
            vault_url=vault_url, credential=DefaultAzureCredential()
        )

    @with_retry()
    def get_secret(self, name: str) -> str:
        try:
            return self._client.get_secret(name).value or ""
        except ResourceNotFoundError as exc:
            raise SecretNotFoundError(f"Secret '{name}' not found") from exc
