"""SoundCard audio backend for macOS and Linux."""

from typing import List, Optional

import numpy as np

try:
    import soundcard as sc

    SOUNDCARD_AVAILABLE = True
except ImportError:
    SOUNDCARD_AVAILABLE = False

from koescript.audio.backends.base import AudioBackend, AudioDevice


class SoundCardBackend(AudioBackend):
    """Audio backend using the SoundCard library.

    This backend works on macOS and Linux with good loopback device support.
    It's the preferred backend for these platforms due to its simplicity and
    reliability.
    """

    def is_available(self) -> bool:
        """Check if SoundCard is available."""
        return SOUNDCARD_AVAILABLE

    def get_backend_name(self) -> str:
        """Get backend name."""
        return "SoundCard"

    def get_available_devices(
        self, include_loopback: bool = False
    ) -> List[AudioDevice]:
        """Get list of available audio input devices.

        Args:
            include_loopback: Whether to include loopback/virtual audio devices

        Returns:
            List of AudioDevice objects

        Raises:
            RuntimeError: If device enumeration fails or SoundCard is not available
        """
        if not SOUNDCARD_AVAILABLE:
            raise RuntimeError(
                "SoundCard library is not installed. "
                "Install with: pip install soundcard"
            )

        try:
            microphones = sc.all_microphones(include_loopback=include_loopback)
            devices = []

            for mic in microphones:
                # Get device ID - use WASAPI name if available (Windows compat), else regular name
                device_id = mic.wasapi_name if hasattr(mic, "wasapi_name") else mic.name
                devices.append(
                    AudioDevice(device=mic, name=mic.name, device_id=device_id)
                )

            return devices

        except Exception as e:
            raise RuntimeError(f"Failed to enumerate audio devices: {e}") from e

    def get_default_device(self) -> AudioDevice:
        """Get the system's default audio input device.

        Returns:
            AudioDevice object for the default microphone

        Raises:
            RuntimeError: If no default device is available or SoundCard is not installed
        """
        if not SOUNDCARD_AVAILABLE:
            raise RuntimeError(
                "SoundCard library is not installed. "
                "Install with: pip install soundcard"
            )

        try:
            default_mic = sc.default_microphone()
            if default_mic is None:
                raise RuntimeError("No default microphone found")

            device_id = (
                default_mic.wasapi_name
                if hasattr(default_mic, "wasapi_name")
                else default_mic.name
            )

            return AudioDevice(
                device=default_mic, name=default_mic.name, device_id=device_id
            )

        except Exception as e:
            raise RuntimeError(f"Failed to get default microphone: {e}") from e

    def record_chunk(
        self, device: AudioDevice, duration: float
    ) -> Optional[np.ndarray]:
        """Record an audio chunk from the specified device.

        Args:
            device: AudioDevice to record from (must be a SoundCard device)
            duration: Duration to record in seconds

        Returns:
            Numpy array of audio samples (1D for mono) or None on failure

        Raises:
            RuntimeError: If recording fails
            ValueError: If device is invalid
        """
        if not isinstance(device, AudioDevice):
            raise ValueError("Invalid device type - must be AudioDevice")

        if not SOUNDCARD_AVAILABLE:
            raise RuntimeError("SoundCard library is not installed")

        try:
            # Use the native soundcard microphone object
            mic = device.device

            # Calculate number of frames to record
            numframes = int(self.sample_rate * duration)

            # Record audio chunk using context manager for proper resource handling
            with mic.recorder(
                samplerate=self.sample_rate, channels=self.channels
            ) as recorder:
                audio_data: np.ndarray = np.array(recorder.record(numframes=numframes))

            # Convert to 1D (mono) for Whisper if needed
            if audio_data.ndim > 1:
                audio_data = audio_data.squeeze()

            return audio_data

        except Exception as e:
            raise RuntimeError(f"Failed to capture audio: {e}") from e
