"""
Configuration settings for the Contract Intelligence application.

This module uses Pydantic settings to manage configuration from environment variables.
"""

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings


class AzureSettings(BaseSettings):
    """Azure-related configuration settings."""

    subscription_id: str = Field(..., env="AZURE_SUBSCRIPTION_ID")
    client_id: str = Field(..., env="AZURE_CLIENT_ID")
    client_secret: SecretStr = Field(..., env="AZURE_CLIENT_SECRET")
    tenant_id: str = Field(..., env="AZURE_TENANT_ID")


class AIFoundrySettings(BaseSettings):
    """Azure AI Foundry configuration."""

    project_connection_string: SecretStr = Field(..., env="AZURE_AI_FOUNDRY_PROJECT_CONNECTION_STRING")
    endpoint: str = Field(..., env="AZURE_AI_FOUNDRY_ENDPOINT")
    key: SecretStr = Field(..., env="AZURE_AI_FOUNDRY_KEY")


class OpenAISettings(BaseSettings):
    """Azure OpenAI configuration."""

    endpoint: str = Field(..., env="AZURE_OPENAI_ENDPOINT")
    key: SecretStr = Field(..., env="AZURE_OPENAI_KEY")
    deployment: str = Field(..., env="AZURE_OPENAI_DEPLOYMENT")


class DocumentIntelligenceSettings(BaseSettings):
    """Azure Document Intelligence configuration."""

    endpoint: str = Field(..., env="AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
    key: SecretStr = Field(..., env="AZURE_DOCUMENT_INTELLIGENCE_KEY")


class LanguageSettings(BaseSettings):
    """Azure Language Service configuration."""

    endpoint: str = Field(..., env="AZURE_LANGUAGE_ENDPOINT")
    key: SecretStr = Field(..., env="AZURE_LANGUAGE_KEY")


class SearchSettings(BaseSettings):
    """Azure Search configuration."""

    endpoint: str = Field(..., env="AZURE_SEARCH_ENDPOINT")
    key: SecretStr = Field(..., env="AZURE_SEARCH_KEY")
    index_name: str = Field("contract-index", env="AZURE_SEARCH_INDEX_NAME")


class StorageSettings(BaseSettings):
    """Azure Blob Storage configuration."""

    account: str = Field(..., env="AZURE_STORAGE_ACCOUNT")
    key: SecretStr = Field(..., env="AZURE_STORAGE_KEY")
    container: str = Field("contracts", env="AZURE_STORAGE_CONTAINER")


class SQLSettings(BaseSettings):
    """Azure SQL configuration."""

    server: str = Field(..., env="AZURE_SQL_SERVER")
    database: str = Field(..., env="AZURE_SQL_DATABASE")
    user: str = Field(..., env="AZURE_SQL_USER")
    password: SecretStr = Field(..., env="AZURE_SQL_PASSWORD")


class KeyVaultSettings(BaseSettings):
    """Azure Key Vault configuration."""

    url: str = Field(..., env="AZURE_KEY_VAULT_URL")


class LoggingSettings(BaseSettings):
    """Logging configuration."""

    level: str = Field("INFO", env="LOG_LEVEL")


class Settings(BaseSettings):
    """Main application settings."""

    azure: AzureSettings = AzureSettings()
    ai_foundry: AIFoundrySettings = AIFoundrySettings()
    openai: OpenAISettings = OpenAISettings()
    document_intelligence: DocumentIntelligenceSettings = DocumentIntelligenceSettings()
    language: LanguageSettings = LanguageSettings()
    search: SearchSettings = SearchSettings()
    storage: StorageSettings = StorageSettings()
    sql: SQLSettings = SQLSettings()
    key_vault: KeyVaultSettings = KeyVaultSettings()
    logging: LoggingSettings = LoggingSettings()

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()