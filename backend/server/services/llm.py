from __future__ import annotations
import httpx
from .interfaces import LLM
from ..core.config import settings


class OllamaLLM(LLM):
    def __init__(self, host: str, model: str):
        self.host = host.rstrip("/")
        self.model = model

    async def _pull_if_needed(self) -> None:
        async with httpx.AsyncClient(timeout=None) as client:
            r = await client.post(f"{self.host}/api/pull", json={"name": self.model}, timeout=None)
            r.raise_for_status()

    async def generate(self, prompt: str) -> str:
        payload = {"model": self.model, "prompt": prompt, "stream": False}
        async with httpx.AsyncClient(timeout=120) as client:
            r = await client.post(f"{self.host}/api/generate", json=payload)
            if r.status_code == 404:
                await self._pull_if_needed()
                r = await client.post(f"{self.host}/api/generate", json=payload)
            r.raise_for_status()
            data = r.json()
            response = data.get("response", "")
            return str(response)


def get_llm() -> LLM:
    if settings.LLM_PROVIDER == "ollama":
        return OllamaLLM(settings.OLLAMA_HOST, settings.LLM_MODEL)
    raise NotImplementedError(f"Unsupported LLM_PROVIDER={settings.LLM_PROVIDER}")
