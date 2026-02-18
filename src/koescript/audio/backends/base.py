"""Audio backend abstraction for cross-platform audio capture."""

from abc import ABC, abstractmethod
from typing import Any, List, Optional

import numpy as np


class AudioDevice:
    """Represents an audio device across all platforms.

    This is a platform-agnostic wrapper around native audio device objects.
    """

    def __init__(self, device: Any, name: str, device_id: str) -> None:
        """Initialize an audio device wrapper.

        Args:
            device: Native audio device object (soundcard.Microphone, pyaudio device, etc.)
            name: Human-readable device name
            device_id: Unique device identifier
        """
        self.device = device
        self.name = name
        self.id = device_id

    def __repr__(self) -> str:
        """String representation of the audio device."""
        return f"AudioDevice(name='{self.name}', id='{self.id}')"

    def __eq__(self, other: object) -> bool:
        """Check equality based on device ID."""
        if not isinstance(other, AudioDevice):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash based on device ID for use in sets/dicts."""
        return hash(self.id)


class AudioBackend(ABC):
    """Abstract base class for platform-specific audio backends.

    This provides a consistent interface for audio capture across different
    platforms (macOS/Linux with SoundCard, Windows with WASAPI).
    """

    def __init__(self, sample_rate: int = 16000, channels: int = 1) -> None:
        """Initialize audio backend.

        Args:
            sample_rate: Audio sample rate in Hz (default: 16000 for Whisper)
            channels: Number of audio channels (default: 1 for mono)
        """
        self.sample_rate = sample_rate
        self.channels = channels

    @abstractmethod
    def get_available_devices(
        self, include_loopback: bool = False
    ) -> List[AudioDevice]:
        """Get list of available audio input devices.

        Args:
            include_loopback: Whether to include loopback/virtual audio devices

        Returns:
            List of AudioDevice objects

        Raises:
            RuntimeError: If device enumeration fails
        """
        pass

    @abstractmethod
    def get_default_device(self) -> AudioDevice:
        """Get the system's default audio input device.

        Returns:
            AudioDevice object for the default input

        Raises:
            RuntimeError: If no default device is available
        """
        pass

    @abstractmethod
    def record_chunk(
        self, device: AudioDevice, duration: float
    ) -> Optional[np.ndarray]:
        """Record an audio chunk from the specified device.

        Args:
            device: AudioDevice to record from
            duration: Duration to record in seconds

        Returns:
            Numpy array of audio samples (1D for mono, 2D for stereo) or None on failure

        Raises:
            RuntimeError: If recording fails
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this audio backend is available on the current system.

        Returns:
            True if backend can be used, False otherwise
        """
        pass

    @abstractmethod
    def get_backend_name(self) -> str:
        """Get the name of this audio backend.

        Returns:
            Backend name (e.g., "SoundCard", "WASAPI")
        """
        pass
