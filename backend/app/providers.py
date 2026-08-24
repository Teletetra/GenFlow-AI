from anthropic import Anthropic
from openai import OpenAI
from .config import settings


class LLMProvider:
    def generate(self, prompt: str, temperature: float = 0.4) -> tuple[str, str, str]:
        raise NotImplementedError


class OpenAIProvider(LLMProvider):
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)

    def generate(self, prompt: str, temperature: float = 0.4):
        response = self.client.chat.completions.create(
            model=settings.openai_model,
            temperature=temperature,
            messages=[
                {"role": "system", "content": "You are GenFlow, an enterprise content generation agent. Produce accurate, useful, structured content."},
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content or "", "openai", settings.openai_model


class AnthropicProvider(LLMProvider):
    def __init__(self):
        self.client = Anthropic(api_key=settings.anthropic_api_key)

    def generate(self, prompt: str, temperature: float = 0.4):
        response = self.client.messages.create(
            model=settings.anthropic_model,
            max_tokens=2000,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join(getattr(block, "text", "") for block in response.content)
        return text, "anthropic", settings.anthropic_model


def get_provider(name: str | None = None) -> LLMProvider:
    selected = (name or settings.llm_provider).lower()
    if selected == "anthropic":
        if not settings.anthropic_api_key:
            raise RuntimeError("ANTHROPIC_API_KEY is not configured")
        return AnthropicProvider()
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured")
    return OpenAIProvider()
