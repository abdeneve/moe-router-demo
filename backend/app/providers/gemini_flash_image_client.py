from __future__ import annotations

from ..models.schemas import RouterRequest
from .base_client import LlmProviderClient


class GeminiFlashImageClient(LlmProviderClient):
    name = 'gemini_flash_image'
    default_model = 'gemini-2.5-flash-image'

    async def generate(self, payload: RouterRequest, *, model: str | None = None) -> str:
        await self._simulate_latency(95)
        target_model = model or self.default_model
        prompt = self._short_prompt(payload.query)
        return f'[{self.name}:{target_model}] multimodal response for {prompt}'
