"""Centralised, type-safe configuration loaded from environment variables.

We use `pydantic-settings` so configuration is **validated at startup** — failing
fast is a key enterprise principle.
"""
from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AzureSettings(BaseSettings):
    """All Azure endpoints / identifiers required by the application."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # Key Vault
    key_vault_url: str = Field(..., alias="AZURE_KEY_VAULT_URL")

    # Blob storage
    storage_account_url: str = Field(..., alias="AZURE_STORAGE_ACCOUNT_URL")
    blob_container: str = Field("contracts", alias="AZURE_BLOB_CONTAINER")

    # Document Intelligence
    docintel_endpoint: str = Field(..., alias="AZURE_DOCINTEL_ENDPOINT")

    # Language Service
    language_endpoint: str = Field(..., alias="AZURE_LANGUAGE_ENDPOINT")

    # AI Search
    search_endpoint: str = Field(..., alias="AZURE_SEARCH_ENDPOINT")
    search_index: str = Field("contracts-index", alias="AZURE_SEARCH_INDEX")

    # Azure OpenAI
    openai_endpoint: str = Field(..., alias="AZURE_OPENAI_ENDPOINT")
    openai_deployment: str = Field("gpt-4o", alias="AZURE_OPENAI_DEPLOYMENT")
    openai_api_version: str = Field(
        "2024-08-01-preview", alias="AZURE_OPENAI_API_VERSION"
    )

    # AI Foundry project (used by Evaluators / Agents)
    ai_project_connection_string: str = Field(
        ..., alias="AZURE_AI_PROJECT_CONNECTION_STRING"
    )

    # Content Safety
    content_safety_endpoint: str = Field(..., alias="AZURE_CONTENT_SAFETY_ENDPOINT")

    # SQL
    sql_connection_string: str = Field(..., alias="AZURE_SQL_CONNECTION_STRING")

    # Misc
    log_level: str = Field("INFO", alias="LOG_LEVEL")


@lru_cache
def get_settings() -> AzureSettings:
    """Cached settings accessor — instantiated once per process."""
    return AzureSettings()  # type: ignore[call-arg]
