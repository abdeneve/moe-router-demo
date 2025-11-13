from __future__ import annotations

from ..models.schemas import RouterRequest
from .base_client import LlmProviderClient


class GeminiProClient(LlmProviderClient):
    name = 'gemini_pro'
    default_model = 'gemini-2.5-pro'

    async def generate(self, payload: RouterRequest, *, model: str | None = None) -> str:
        await self._simulate_latency(85)
        target_model = model or self.default_model
        prompt = self._short_prompt(payload.query)
        return f'[{self.name}:{target_model}] analytical response for {prompt}'
