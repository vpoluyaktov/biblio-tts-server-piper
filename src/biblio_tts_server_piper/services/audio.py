"""Audio processing utilities."""

import io
import wave
from typing import Union

import numpy as np


class AudioService:
    """Service for audio processing and conversion."""

    @staticmethod
    def numpy_to_wav_bytes(audio: np.ndarray, sample_rate: int) -> bytes:
        """Convert numpy array to WAV bytes.
        
        Args:
            audio: Audio data as numpy array
            sample_rate: Sample rate in Hz
            
        Returns:
            WAV file bytes
        """
        if audio.dtype != np.int16:
            audio = (audio * 32767).astype(np.int16)
        
        buffer = io.BytesIO()
        with wave.open(buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio.tobytes())
        
        return buffer.getvalue()

    @staticmethod
    def resample_audio(audio: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
        """Resample audio to target sample rate.
        
        Args:
            audio: Audio data as numpy array
            orig_sr: Original sample rate
            target_sr: Target sample rate
            
        Returns:
            Resampled audio
        """
        if orig_sr == target_sr:
            return audio
        
        from scipy import signal
        
        num_samples = int(len(audio) * target_sr / orig_sr)
        resampled = signal.resample(audio, num_samples)
        
        return resampled
