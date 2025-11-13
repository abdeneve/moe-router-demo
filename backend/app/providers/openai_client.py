from __future__ import annotations

from ..models.schemas import RouterRequest
from .base_client import LlmProviderClient


class OpenAIClient(LlmProviderClient):
    name = 'openai'
    default_model = 'gpt-4o-mini'

    async def generate(self, payload: RouterRequest, *, model: str | None = None) -> str:
        await self._simulate_latency(60)
        target_model = model or self.default_model
        prompt = self._short_prompt(payload.query)
        return f'[{self.name}:{target_model}] response for {prompt}'
