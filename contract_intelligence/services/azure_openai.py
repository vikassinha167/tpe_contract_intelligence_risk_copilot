"""
Azure OpenAI service implementation.

Provides AI-powered text generation and conversation capabilities.
"""

from typing import Any, Dict, Optional

from openai import AzureOpenAI

from contract_intelligence.config.settings import settings
from contract_intelligence.services.base import OpenAIService
from contract_intelligence.utils.exceptions import AzureServiceError
from contract_intelligence.utils.logging import get_logger

logger = get_logger(__name__)


class AzureOpenAIService(OpenAIService):
    """Azure OpenAI service implementation."""

    def __init__(self) -> None:
        """Initialize the Azure OpenAI client."""
        try:
            self.client = AzureOpenAI(
                api_key=settings.openai.key.get_secret_value(),
                api_version="2024-02-01",
                azure_endpoint=settings.openai.endpoint,
            )
            self.deployment = settings.openai.deployment
            logger.info("Azure OpenAI service initialized", deployment=self.deployment)
        except Exception as e:
            logger.error("Failed to initialize OpenAI service", error=str(e))
            raise AzureServiceError(f"Failed to initialize OpenAI service: {e}") from e

    def generate_response(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate a response using OpenAI.

        Args:
            prompt: The prompt for generation.
            context: Optional context information.

        Returns:
            Generated response.

        Raises:
            AzureServiceError: If generation fails.
        """
        try:
            logger.info("Generating response", prompt_length=len(prompt))

            # Prepare messages
            messages = []

            if context:
                # Add system message with context
                system_message = f"You are a contract intelligence assistant. Context: {context}"
                messages.append({"role": "system", "content": system_message})

            messages.append({"role": "user", "content": prompt})

            # Generate response
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=messages,
                max_tokens=1000,
                temperature=0.7,
            )

            generated_text = response.choices[0].message.content.strip()

            logger.info("Response generated", response_length=len(generated_text))
            return generated_text

        except Exception as e:
            logger.error("Response generation failed", error=str(e))
            raise AzureServiceError(f"Response generation failed: {e}") from e