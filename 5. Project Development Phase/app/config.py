from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    gemini_api_key: str = ""
    debug: bool = False
    host: str = "127.0.0.1"
    port: int = 8000
    gemini_model: str = "gemini-2.0-flash"
    local_model_name: str = "MBZUAI/LaMini-Flan-T5-248M"
    local_model_device: str = "auto"
    local_model_max_input_tokens: int = 512
    # Keep CPU fallback responses within the browser request window.
    local_model_max_output_tokens: int = 128

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("debug", mode="before")
    @classmethod
    def parse_debug(cls, value: object) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"1", "true", "yes", "on", "debug"}:
                return True
            if normalized in {"0", "false", "no", "off", "release", "production", ""}:
                return False
        raise ValueError("DEBUG must be true or false")

    @property
    def log_level(self) -> str:
        return "DEBUG" if self.debug else "INFO"


settings = Settings()
