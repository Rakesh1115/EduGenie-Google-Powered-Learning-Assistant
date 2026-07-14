"""Lazy local LaMini-Flan-T5 text-generation fallback."""

import logging
from threading import Lock

import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

from ..config import settings

logger = logging.getLogger("edu_genie.lamini")


class LaminiServiceError(RuntimeError):
    """Raised when the configured local fallback model cannot generate text."""


class LaminiService:
    """Runs MBZUAI's LaMini-Flan-T5 model locally after a Gemini failure."""

    def __init__(self, model_name: str | None = None):
        self.model_name = model_name or settings.local_model_name
        self.device = "cuda" if settings.local_model_device == "auto" and torch.cuda.is_available() else settings.local_model_device
        if self.device == "auto":
            self.device = "cpu"
        self._tokenizer = None
        self._model = None
        self._load_lock = Lock()

    def _load_model(self) -> None:
        if self._model is not None and self._tokenizer is not None:
            return
        with self._load_lock:
            if self._model is not None and self._tokenizer is not None:
                return
            try:
                logger.info("Loading local LaMini fallback model '%s' on %s", self.model_name, self.device)
                self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                self._model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
                self._model.to(self.device)
                self._model.eval()
                logger.info("Local LaMini fallback model is ready")
            except Exception as exc:
                logger.exception("Unable to load local LaMini fallback model")
                raise LaminiServiceError(
                    "The local fallback model is unavailable. Download the configured model and try again."
                ) from exc

    def generate(self, prompt: str, *, max_output_tokens: int = 512, **_: object) -> str:
        self._load_model()
        try:
            encoded = self._tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=settings.local_model_max_input_tokens,
            )
            inputs = {name: value.to(self.device) for name, value in encoded.items()}
            with torch.inference_mode():
                generated = self._model.generate(
                    **inputs,
                    max_new_tokens=min(max_output_tokens, settings.local_model_max_output_tokens),
                    do_sample=False,
                )
            text = self._tokenizer.decode(generated[0], skip_special_tokens=True).strip()
        except LaminiServiceError:
            raise
        except Exception as exc:
            logger.exception("Local LaMini fallback generation failed")
            raise LaminiServiceError("The local fallback model could not generate a response.") from exc
        if not text:
            raise LaminiServiceError("The local fallback model returned an empty response.")
        logger.info("AI response source=local_fallback model=%s", self.model_name)
        return text


_service_instance: LaminiService | None = None
_service_lock = Lock()


def get_lamini_service() -> LaminiService:
    global _service_instance
    if _service_instance is None:
        with _service_lock:
            if _service_instance is None:
                _service_instance = LaminiService()
    return _service_instance
