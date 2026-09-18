import json
import urllib.request

from src.llm.base import LLMProvider


class OllamaProvider(LLMProvider):
    """
    Local LLM provider using the Ollama HTTP API.
    """

    def __init__(
        self,
        model: str = "qwen2.5:3b",
        base_url: str = "http://localhost:11434",
    ):
        self.model = model
        self.base_url = base_url.rstrip("/")

    def generate(self, prompt: str) -> str:
        """
        Generate a response using a local Ollama model.
        """
        if not prompt.strip():
            raise ValueError("Prompt cannot be empty")

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }

        request = urllib.request.Request(
            url=f"{self.base_url}/api/generate",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                result = json.loads(
                    response.read().decode("utf-8")
                )
        except Exception as exc:
            raise RuntimeError(
                "Could not communicate with Ollama. "
                "Make sure Ollama is running."
            ) from exc

        return result["response"].strip()