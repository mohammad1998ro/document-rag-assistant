from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """
    Common interface for interchangeable LLM providers.
    """

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """
        Generate a response from the language model.

        Args:
            prompt: Complete prompt sent to the model.

        Returns:
            Generated text response.
        """
        raise NotImplementedError