"""Piper TTS service wrapper."""

import json
import logging
import subprocess
from pathlib import Path
from threading import Lock
from typing import Any, Optional
from urllib.request import urlretrieve

import numpy as np

from ..config import get_settings
from ..models import ModelInfo, VoiceInfo

logger = logging.getLogger(__name__)

VOICES_URL = "https://huggingface.co/rhasspy/piper-voices/raw/main/voices.json"

VOICE_METADATA = {
    "en": {"gender": "U", "name": "English"},
    "es": {"gender": "U", "name": "Spanish"},
    "fr": {"gender": "U", "name": "French"},
    "de": {"gender": "U", "name": "German"},
    "it": {"gender": "U", "name": "Italian"},
    "ru": {"gender": "U", "name": "Russian"},
    "zh": {"gender": "U", "name": "Chinese"},
    "ja": {"gender": "U", "name": "Japanese"},
    "ko": {"gender": "U", "name": "Korean"},
    "pt": {"gender": "U", "name": "Portuguese"},
    "nl": {"gender": "U", "name": "Dutch"},
    "pl": {"gender": "U", "name": "Polish"},
    "tr": {"gender": "U", "name": "Turkish"},
    "ar": {"gender": "U", "name": "Arabic"},
    "hi": {"gender": "U", "name": "Hindi"},
}


class PiperTTSService:
    """Service for Piper TTS model management and synthesis."""

    _instance: Optional["PiperTTSService"] = None
    _lock = Lock()

    def __new__(cls, served_models: Optional[list[str]] = None) -> "PiperTTSService":
        """Singleton pattern for TTS service."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, served_models: Optional[list[str]] = None):
        """Initialize the Piper TTS service."""
        if self._initialized:
            return

        self._settings = get_settings()
        self._cache_dir = self._settings.cache_dir
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        
        self._models_dir = self._cache_dir / "models"
        self._models_dir.mkdir(parents=True, exist_ok=True)
        
        self._voices_cache: Optional[dict] = None
        self._served_models = served_models
        self._loaded_models: dict[str, Path] = {}
        
        logger.info(f"Cache directory: {self._cache_dir}")
        logger.info(f"Models directory: {self._models_dir}")
        
        self._initialized = True

    def _get_voices_catalog(self) -> dict:
        """Get the voices catalog from Hugging Face."""
        if self._voices_cache is not None:
            return self._voices_cache
        
        voices_file = self._cache_dir / "voices.json"
        
        if not voices_file.exists():
            logger.info(f"Downloading voices catalog from {VOICES_URL}")
            urlretrieve(VOICES_URL, voices_file)
        
        with open(voices_file, 'r') as f:
            self._voices_cache = json.load(f)
        
        return self._voices_cache

    def _download_model(self, model_key: str) -> Path:
        """Download a Piper model if not already cached.
        
        Args:
            model_key: Model key from voices catalog (e.g., "en_US-lessac-medium")
            
        Returns:
            Path to the model .onnx file
        """
        voices = self._get_voices_catalog()
        
        if model_key not in voices:
            raise ValueError(f"Model {model_key} not found in voices catalog")
        
        model_info = voices[model_key]
        model_url = model_info["files"][".onnx"]
        config_url = model_info["files"][".onnx.json"]
        
        model_file = self._models_dir / f"{model_key}.onnx"
        config_file = self._models_dir / f"{model_key}.onnx.json"
        
        if not model_file.exists():
            logger.info(f"Downloading model {model_key} from {model_url}")
            urlretrieve(model_url, model_file)
        
        if not config_file.exists():
            logger.info(f"Downloading config for {model_key}")
            urlretrieve(config_url, config_file)
        
        return model_file

    def preload_models(self, model_keys: list[str]):
        """Preload specified models into cache.
        
        Args:
            model_keys: List of model keys to preload
        """
        logger.info(f"Preloading {len(model_keys)} models...")
        
        for model_key in model_keys:
            try:
                model_path = self._download_model(model_key)
                self._loaded_models[model_key] = model_path
                logger.info(f"Preloaded model: {model_key}")
            except Exception as e:
                logger.error(f"Failed to preload model {model_key}: {e}")

    def get_available_voices(self) -> list[VoiceInfo]:
        """Get list of available voices.
        
        Returns:
            List of VoiceInfo objects
        """
        voices = self._get_voices_catalog()
        voice_list = []
        
        for model_key, model_data in voices.items():
            if self._served_models and model_key not in self._served_models:
                continue
            
            language_code = model_data.get("language", {}).get("code", "en")
            lang_short = language_code.split("_")[0] if "_" in language_code else language_code[:2]
            
            metadata = VOICE_METADATA.get(lang_short, {"gender": "U", "name": language_code})
            
            quality = model_data.get("quality", "medium")
            num_speakers = model_data.get("num_speakers", 1)
            
            if num_speakers > 1:
                for speaker_id in range(num_speakers):
                    voice_id = f"piper:{model_key}#{speaker_id}"
                    voice_list.append(VoiceInfo(
                        id=voice_id,
                        name=f"{model_key} (Speaker {speaker_id})",
                        gender=metadata["gender"],
                        language=lang_short,
                        locale=language_code.lower().replace("_", "-"),
                        tts_name="piper",
                        model_id=model_key,
                        quality=quality,
                    ))
            else:
                voice_id = f"piper:{model_key}"
                voice_list.append(VoiceInfo(
                    id=voice_id,
                    name=model_key,
                    gender=metadata["gender"],
                    language=lang_short,
                    locale=language_code.lower().replace("_", "-"),
                    tts_name="piper",
                    model_id=model_key,
                    quality=quality,
                ))
        
        return voice_list

    def get_available_languages(self) -> list[str]:
        """Get list of available language codes.
        
        Returns:
            List of 2-character language codes
        """
        voices = self.get_available_voices()
        languages = sorted(set(v.language for v in voices))
        return languages

    def get_available_models(self, language: Optional[str] = None) -> list[ModelInfo]:
        """Get list of available models.
        
        Args:
            language: Optional language filter
            
        Returns:
            List of ModelInfo objects
        """
        voices_catalog = self._get_voices_catalog()
        models = []
        
        for model_key, model_data in voices_catalog.items():
            if self._served_models and model_key not in self._served_models:
                continue
            
            language_code = model_data.get("language", {}).get("code", "en")
            lang_short = language_code.split("_")[0] if "_" in language_code else language_code[:2]
            
            if language and lang_short != language:
                continue
            
            models.append(ModelInfo(
                model_id=model_key,
                language=lang_short,
                name=model_data.get("name", model_key),
                quality=model_data.get("quality", "medium"),
                num_speakers=model_data.get("num_speakers", 1),
                sample_rate=model_data.get("audio", {}).get("sample_rate", 22050),
            ))
        
        return models

    def synthesize(
        self,
        text: str,
        voice_id: str,
        sample_rate: int = 22050,
        speed: float = 1.0,
        speaker_id: Optional[int] = None,
    ) -> np.ndarray:
        """Synthesize speech from text using Piper.
        
        Args:
            text: Text to synthesize
            voice_id: Voice ID in format "piper:model_key" or "piper:model_key#speaker_id"
            sample_rate: Target sample rate
            speed: Speech speed multiplier
            speaker_id: Optional speaker ID for multi-speaker models
            
        Returns:
            Audio as numpy array
        """
        if not voice_id.startswith("piper:"):
            raise ValueError(f"Invalid voice ID format: {voice_id}")
        
        voice_parts = voice_id[6:].split("#")
        model_key = voice_parts[0]
        
        if len(voice_parts) > 1 and speaker_id is None:
            # Handle both numeric speaker IDs and "default"
            speaker_part = voice_parts[1]
            if speaker_part.lower() != "default":
                try:
                    speaker_id = int(speaker_part)
                except ValueError:
                    # If not a number and not "default", use None
                    speaker_id = None
        
        model_path = self._loaded_models.get(model_key)
        if model_path is None:
            model_path = self._download_model(model_key)
            self._loaded_models[model_key] = model_path
        
        cmd = ["piper", "--model", str(model_path), "--output-raw"]
        
        if speaker_id is not None:
            cmd.extend(["--speaker", str(speaker_id)])
        
        if speed != 1.0:
            cmd.extend(["--length-scale", str(1.0 / speed)])
        
        try:
            result = subprocess.run(
                cmd,
                input=text.encode("utf-8"),
                capture_output=True,
                check=True,
            )
            
            audio_bytes = result.stdout
            audio = np.frombuffer(audio_bytes, dtype=np.int16)
            
            if len(audio) == 0:
                raise ValueError("Piper returned empty audio")
            
            return audio
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Piper synthesis failed: {e.stderr.decode('utf-8')}")
            raise ValueError(f"Piper synthesis failed: {e.stderr.decode('utf-8')}")
        except FileNotFoundError:
            raise ValueError("Piper executable not found. Please install Piper TTS.")
