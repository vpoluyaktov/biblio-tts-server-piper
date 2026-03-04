"""Voice and model discovery API endpoints."""

import logging
from typing import Optional

from fastapi import APIRouter, Query

from ..models import ModelInfo, VoiceInfo
from ..services import PiperTTSService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["voices"])


@router.get("/voices", response_model=list[VoiceInfo])
async def list_voices(
    language: Optional[str] = Query(None, description="Filter by language code"),
) -> list[VoiceInfo]:
    """List all available voices.
    
    Args:
        language: Optional 2-character language code filter
        
    Returns:
        List of available voices
    """
    tts_service = PiperTTSService()
    voices = tts_service.get_available_voices()
    
    if language:
        voices = [v for v in voices if v.language == language]
    
    logger.debug(f"Returning {len(voices)} voices" + (f" for language '{language}'" if language else ""))
    return voices


@router.get("/languages", response_model=list[str])
async def list_languages() -> list[str]:
    """List all available language codes.
    
    Returns:
        List of 2-character language codes
    """
    tts_service = PiperTTSService()
    languages = tts_service.get_available_languages()
    
    logger.debug(f"Returning {len(languages)} languages")
    return languages


@router.get("/models", response_model=list[ModelInfo])
async def list_models(
    language: Optional[str] = Query(None, description="Filter by language code"),
) -> list[ModelInfo]:
    """List all available models.
    
    Args:
        language: Optional 2-character language code filter
        
    Returns:
        List of available models
    """
    tts_service = PiperTTSService()
    models = tts_service.get_available_models(language=language)
    
    logger.debug(f"Returning {len(models)} models" + (f" for language '{language}'" if language else ""))
    return models
