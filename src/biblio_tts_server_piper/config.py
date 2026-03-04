"""Configuration settings for Piper TTS Server."""

from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    host: str = "0.0.0.0"
    port: int = 5556
    cache_dir: Path = Path.home() / ".cache" / "piper"
    served_models: Optional[str] = None
    log_level: str = "INFO"
    base_path: str = ""

    class Config:
        env_prefix = "PIPER_"


def get_settings() -> Settings:
    """Get settings, reloading from environment variables."""
    return Settings()


settings = get_settings()
