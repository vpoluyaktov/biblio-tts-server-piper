"""Pydantic models for API requests and responses."""

from typing import Optional

from pydantic import BaseModel, Field


class VoiceInfo(BaseModel):
    """Information about a TTS voice."""

    id: str = Field(..., description="Voice identifier")
    name: str = Field(..., description="Friendly name of the voice")
    gender: str = Field(..., description="Gender: M, F, or U")
    language: str = Field(..., description="2-character language code")
    locale: str = Field(..., description="Locale code (e.g., en-us)")
    tts_name: str = Field(default="piper", description="TTS system name")
    model_id: str = Field(..., description="Piper model identifier")
    quality: str = Field(default="medium", description="Voice quality: low, medium, high")


class ModelInfo(BaseModel):
    """Information about a Piper TTS model."""

    model_id: str = Field(..., description="Model identifier")
    language: str = Field(..., description="Language code")
    name: str = Field(..., description="Model name")
    quality: str = Field(..., description="Model quality")
    num_speakers: int = Field(..., description="Number of speakers")
    sample_rate: int = Field(..., description="Sample rate")


class TTSRequest(BaseModel):
    """Request body for TTS synthesis (POST endpoint)."""

    text: str = Field(..., description="Text to synthesize")
    voice: str = Field(..., description="Voice ID in format piper:model#speaker")
    sample_rate: int = Field(default=22050, description="Output sample rate")
    speed: float = Field(default=1.0, description="Speech speed multiplier")
    speaker_id: Optional[int] = Field(default=None, description="Speaker ID for multi-speaker models")


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = "ok"
    version: str = "0.1.0"


class ErrorResponse(BaseModel):
    """Error response."""

    detail: str
    error_code: Optional[str] = None
