import os

from dotenv import load_dotenv
from openai import OpenAI

from src.llm.base import LLMProvider


class OpenAIProvider(LLMProvider):
    """
    Cloud LLM provider using the OpenAI Responses API.
    """

    def __init__(self, model: str | None = None):
        load_dotenv()

        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY is not configured in the .env file"
            )

        self.model = model or os.getenv(
            "OPENAI_MODEL",
            "gpt-5.6-luna",
        )

        self.client = OpenAI(api_key=api_key)

    def generate(self, prompt: str) -> str:
        """
        Generate a response using the OpenAI cloud model.
        """
        if not prompt.strip():
            raise ValueError("Prompt cannot be empty")

        response = self.client.responses.create(
            model=self.model,
            input=prompt,
        )

        return response.output_text.strip()