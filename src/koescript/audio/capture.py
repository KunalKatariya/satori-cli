"""Audio capture module for Koescript CLI with cross-platform backend support."""

from typing import Optional

import numpy as np

from koescript.audio.backends import AudioDevice, get_audio_backend
from koescript.audio.backends.base import AudioBackend


class AudioCapture:
    """Handles audio capture from system audio or specific devices.

    This class uses platform-specific audio backends to provide consistent
    audio capture functionality across macOS, Linux, and Windows.
    """

    def __init__(self, sample_rate: int = 16000, channels: int = 1) -> None:
        """Initialize the audio capture handler.

        Args:
            sample_rate: Sample rate in Hz (default: 16000 for Whisper)
            channels: Number of audio channels (default: 1 for mono)
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.is_recording = False
        self._current_device: Optional[AudioDevice] = None

        # Get platform-appropriate audio backend
        self._backend: AudioBackend = get_audio_backend(
            sample_rate=sample_rate, channels=channels
        )

    def get_available_devices(self) -> list[AudioDevice]:
        """Get list of all available microphone devices.

        Returns:
            List of AudioDevice objects

        Raises:
            RuntimeError: If device enumeration fails
        """
        try:
            return self._backend.get_available_devices(include_loopback=True)
        except Exception as e:
            raise RuntimeError(f"Failed to get audio devices: {e}") from e

    def get_default_device(self) -> AudioDevice:
        """Get the default system microphone.

        Returns:
            AudioDevice object for the default microphone

        Raises:
            RuntimeError: If default device cannot be found
        """
        try:
            return self._backend.get_default_device()
        except Exception as e:
            raise RuntimeError(f"Failed to get default microphone: {e}") from e

    def get_device_by_name(self, name: str) -> Optional[AudioDevice]:
        """Get an audio device by name.

        Args:
            name: Name of the device to find

        Returns:
            AudioDevice if found, None otherwise
        """
        devices = self.get_available_devices()
        for device in devices:
            if device.name.lower() == name.lower():
                return device
        return None

    def set_device(self, device: AudioDevice) -> None:
        """Set the active recording device.

        Args:
            device: AudioDevice to use for recording

        Raises:
            ValueError: If device is invalid
        """
        if not isinstance(device, AudioDevice):
            raise ValueError("Invalid device type - must be AudioDevice")
        self._current_device = device

    def start_recording(self) -> None:
        """Start audio recording from the current device.

        Raises:
            RuntimeError: If no device is set
        """
        if self._current_device is None:
            raise RuntimeError("No audio device selected. Call set_device() first.")
        self.is_recording = True

    def stop_recording(self) -> None:
        """Stop audio recording."""
        self.is_recording = False

    def get_audio_chunk(self, duration: float = 0.5) -> Optional[np.ndarray]:
        """Capture audio chunk from the current device.

        Args:
            duration: Duration of audio chunk in seconds (default: 0.5)

        Returns:
            Audio data as numpy array (1D mono) or None if not recording

        Raises:
            RuntimeError: If recording fails or no device is set
        """
        if not self.is_recording:
            return None

        if self._current_device is None:
            raise RuntimeError("No audio device selected. Call set_device() first.")

        try:
            # Use backend to record audio chunk
            audio_data = self._backend.record_chunk(self._current_device, duration)
            return audio_data
        except Exception as e:
            raise RuntimeError(f"Failed to capture audio: {e}") from e
