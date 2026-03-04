"""TTS API endpoints."""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response

from ..models import TTSRequest
from ..services import AudioService, PiperTTSService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["tts"])


@router.get("/tts")
async def synthesize_get(
    voice: str = Query(..., description="Voice ID in format piper:model#speaker"),
    text: str = Query(..., description="Text to synthesize"),
    sample_rate: int = Query(22050, description="Output sample rate"),
    speed: float = Query(1.0, description="Speech speed multiplier"),
    speaker_id: Optional[int] = Query(None, description="Speaker ID for multi-speaker models"),
    cache: bool = Query(True, description="Enable caching (not implemented)"),
) -> Response:
    """Synthesize speech from text (GET endpoint).

    Returns WAV audio bytes.
    """
    return await _synthesize(text, voice, sample_rate, speed, speaker_id)


@router.post("/tts")
async def synthesize_post(request: TTSRequest) -> Response:
    """Synthesize speech from text (POST endpoint).

    Returns WAV audio bytes.
    """
    return await _synthesize(
        request.text,
        request.voice,
        request.sample_rate,
        request.speed,
        request.speaker_id,
    )


async def _synthesize(
    text: str,
    voice: str,
    sample_rate: int,
    speed: float = 1.0,
    speaker_id: Optional[int] = None,
) -> Response:
    """Internal synthesis function.

    Args:
        text: Text to synthesize
        voice: Voice ID
        sample_rate: Output sample rate
        speed: Speech speed multiplier
        speaker_id: Optional speaker ID

    Returns:
        WAV audio response
    """
    text_preview = text[:50] + "..." if len(text) > 50 else text
    logger.debug(f"TTS request: voice={voice}, sample_rate={sample_rate}, speed={speed}, text='{text_preview}'")
    
    if not text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    try:
        tts_service = PiperTTSService()
        audio_array = tts_service.synthesize(
            text=text,
            voice_id=voice,
            sample_rate=sample_rate,
            speed=speed,
            speaker_id=speaker_id,
        )
        
        if audio_array is None or len(audio_array) == 0:
            raise ValueError("TTS returned empty audio")

        audio_service = AudioService()
        wav_bytes = audio_service.numpy_to_wav_bytes(audio_array, sample_rate)
        
        logger.debug(f"TTS complete: {len(wav_bytes)} bytes generated")

        return Response(
            content=wav_bytes,
            media_type="audio/wav",
            headers={
                "Content-Disposition": 'attachment; filename="tts_output.wav"',
            },
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("TTS synthesis failed")
        raise HTTPException(status_code=500, detail=f"TTS synthesis failed: {e}")
