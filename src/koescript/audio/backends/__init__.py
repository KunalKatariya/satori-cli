"""Audio backend factory for cross-platform audio capture."""

import platform
from typing import Optional

from koescript.audio.backends.base import AudioBackend, AudioDevice

# Cached backend instance
_cached_backend: Optional[AudioBackend] = None


def get_audio_backend(sample_rate: int = 16000, channels: int = 1) -> AudioBackend:
    """Get the appropriate audio backend for the current platform.

    This function automatically selects the best audio backend based on:
    1. Platform (macOS/Linux prefer SoundCard, Windows prefers WASAPI)
    2. Backend availability (fallback if preferred backend not installed)

    Args:
        sample_rate: Audio sample rate in Hz (default: 16000)
        channels: Number of audio channels (default: 1)

    Returns:
        AudioBackend instance suitable for the current platform

    Raises:
        RuntimeError: If no audio backend is available
    """
    global _cached_backend

    # Return cached instance if parameters match
    if (
        _cached_backend is not None
        and _cached_backend.sample_rate == sample_rate
        and _cached_backend.channels == channels
    ):
        return _cached_backend

    system = platform.system()

    # Platform-specific backend selection
    if system in ("Darwin", "Linux"):
        # macOS and Linux: prefer SoundCard
        backend = _try_soundcard_backend(sample_rate, channels)
        if backend is not None:
            _cached_backend = backend
            return backend

        # Fallback to WASAPI if SoundCard not available
        backend = _try_wasapi_backend(sample_rate, channels)
        if backend is not None:
            _cached_backend = backend
            return backend

    elif system == "Windows":
        # Windows: prefer WASAPI (better loopback support)
        backend = _try_wasapi_backend(sample_rate, channels)
        if backend is not None:
            _cached_backend = backend
            return backend

        # Fallback to SoundCard
        backend = _try_soundcard_backend(sample_rate, channels)
        if backend is not None:
            _cached_backend = backend
            return backend

    # No backend available
    raise RuntimeError(
        "No audio backend available. Please install either:\n"
        "  - soundcard: pip install soundcard (macOS/Linux)\n"
        "  - pyaudio: pip install pyaudio (Windows)"
    )


def _try_soundcard_backend(sample_rate: int, channels: int) -> Optional[AudioBackend]:
    """Try to create a SoundCard backend.

    Args:
        sample_rate: Audio sample rate in Hz
        channels: Number of audio channels

    Returns:
        SoundCardBackend if available, None otherwise
    """
    try:
        from koescript.audio.backends.soundcard_backend import SoundCardBackend

        backend = SoundCardBackend(sample_rate=sample_rate, channels=channels)
        if backend.is_available():
            return backend
    except ImportError:
        pass

    return None


def _try_wasapi_backend(sample_rate: int, channels: int) -> Optional[AudioBackend]:
    """Try to create a WASAPI backend.

    Args:
        sample_rate: Audio sample rate in Hz
        channels: Number of audio channels

    Returns:
        WASAPIBackend if available, None otherwise
    """
    try:
        from koescript.audio.backends.wasapi_backend import WASAPIBackend

        backend = WASAPIBackend(sample_rate=sample_rate, channels=channels)
        if backend.is_available():
            return backend
    except ImportError:
        pass

    return None


__all__ = [
    "AudioBackend",
    "AudioDevice",
    "get_audio_backend",
]
