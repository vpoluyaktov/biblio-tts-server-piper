"""API routers for Biblio TTS Server (Piper)."""

from .tts import router as tts_router
from .voices import router as voices_router

__all__ = ["tts_router", "voices_router"]
