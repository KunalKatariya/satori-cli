"""Audio capture module for Koescript CLI using SoundCard."""

from typing import Any, Optional

import numpy as np
import soundcard as sc


class AudioDevice:
    """Represents an audio device."""

    def __init__(self, device: Any) -> None:
        """Initialize an audio device wrapper.

        Args:
            device: A soundcard microphone object
        """
        self.device = device
        self.name = device.name
        self.id = device.wasapi_name if hasattr(device, "wasapi_name") else device.name

    def __repr__(self) -> str:
        """String representation of the audio device."""
        return f"AudioDevice(name='{self.name}')"


class AudioCapture:
    """Handles audio capture from system audio or specific devices."""

    def __init__(self, sample_rate: int = 16000, channels: int = 1) -> None:
        """Initialize the audio capture handler.

        Args:
            sample_rate: Sample rate in Hz (default: 16000 for Whisper)
            channels: Number of audio channels (default: 1 for mono)
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.is_recording = False
        self._current_device: Optional[Any] = None

    def get_available_devices(self) -> list[AudioDevice]:
        """Get list of all available microphone devices.

        Returns:
            List of AudioDevice objects
        """
        try:
            microphones = sc.all_microphones(include_loopback=True)
            return [AudioDevice(mic) for mic in microphones]
        except Exception as e:
            raise RuntimeError(f"Failed to get audio devices: {e}")

    def get_default_device(self) -> AudioDevice:
        """Get the default system microphone.

        Returns:
            AudioDevice object for the default microphone

        Raises:
            RuntimeError: If default device cannot be found
        """
        try:
            default_mic = sc.default_microphone()
            if default_mic is None:
                raise RuntimeError("No default microphone found")
            return AudioDevice(default_mic)
        except Exception as e:
            raise RuntimeError(f"Failed to get default microphone: {e}")

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
            raise ValueError("Invalid device type")
        self._current_device = device.device

    def start_recording(self) -> None:
        """Start audio recording from the current device.

        Raises:
            RuntimeError: If no device is set or recording fails
        """
        if self._current_device is None:
            raise RuntimeError("No audio device selected")
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
            RuntimeError: If recording fails
        """
        if not self.is_recording:
            return None

        try:
            if self._current_device is None:
                raise RuntimeError("No audio device selected")

            # Record audio chunk
            with self._current_device.recorder(
                samplerate=self.sample_rate, channels=self.channels
            ) as recorder:
                audio: np.ndarray = np.array(
                    recorder.record(numframes=int(self.sample_rate * duration))
                )
            # Convert to 1D (mono) for Whisper
            return audio.squeeze()
        except Exception as e:
            raise RuntimeError(f"Failed to capture audio: {e}")
