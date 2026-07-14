import logging
from typing import Optional

from google import genai
from google.genai import types

from ..config import settings
from .lamini_service import LaminiServiceError, get_lamini_service

logger = logging.getLogger("edu_genie.gemini")


class GeminiServiceError(RuntimeError):
    def __init__(self, message: str, status_code: int = 503):
        super().__init__(message)
        self.status_code = status_code


class GeminiService:
    """Small synchronous wrapper around the official google-genai SDK."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        key = api_key or settings.gemini_api_key
        self.model_name = model or settings.gemini_model
        # Leave enough time for the preloaded local model if Gemini is slow or
        # unavailable, while staying inside the frontend's 15-second limit.
        self.client = (
            genai.Client(api_key=key, http_options=types.HttpOptions(timeout=5_000))
            if key
            else None
        )
        self._use_local_fallback = self.client is None

    def _generate_with_fallback(self, prompt: str, *, max_output_tokens: int) -> str:
        try:
            return get_lamini_service().generate(prompt, max_output_tokens=max_output_tokens)
        except LaminiServiceError as exc:
            raise GeminiServiceError(str(exc)) from exc

    def generate(self, prompt: str, *, temperature: float = 0.2, max_output_tokens: int = 1024) -> str:
        if self._use_local_fallback or self.client is None:
            logger.warning("Using local LaMini fallback")
            return self._generate_with_fallback(prompt, max_output_tokens=max_output_tokens)

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=temperature,
                    max_output_tokens=max_output_tokens,
                ),
            )
        except Exception as exc:
            # A quota/rate-limit failure will not recover during this server
            # process. Avoid making every user request wait for Gemini before
            # it can use the local fallback.
            if getattr(exc, "status_code", None) == 429 or "RESOURCE_EXHAUSTED" in str(exc):
                self._use_local_fallback = True
            logger.warning(
                "Gemini generation failed (%s); using local LaMini fallback",
                type(exc).__name__,
                exc_info=True,
            )
            return self._generate_with_fallback(prompt, max_output_tokens=max_output_tokens)
        text = (response.text or "").strip()
        if not text:
            logger.warning("Gemini returned an empty response; using local LaMini fallback")
            return self._generate_with_fallback(prompt, max_output_tokens=max_output_tokens)
        logger.info("AI response source=gemini model=%s", self.model_name)
        return text


_service_instance: Optional[GeminiService] = None


def get_gemini_service() -> GeminiService:
    global _service_instance
    if _service_instance is None:
        _service_instance = GeminiService()
    return _service_instance
