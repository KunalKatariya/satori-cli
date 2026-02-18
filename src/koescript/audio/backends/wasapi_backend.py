"""WASAPI audio backend for Windows loopback support."""

from typing import List, Optional

import numpy as np

try:
    import pyaudio

    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False

from koescript.audio.backends.base import AudioBackend, AudioDevice


class WASAPIBackend(AudioBackend):
    """Audio backend using PyAudio with WASAPI for Windows.

    This backend provides Windows-specific loopback device support through WASAPI.
    It's the preferred backend for Windows platforms.
    """

    def __init__(self, sample_rate: int = 16000, channels: int = 1) -> None:
        """Initialize WASAPI backend.

        Args:
            sample_rate: Audio sample rate in Hz (default: 16000 for Whisper)
            channels: Number of audio channels (default: 1 for mono)
        """
        super().__init__(sample_rate, channels)
        self._pa: Optional[pyaudio.PyAudio] = None

    def _get_pyaudio(self) -> pyaudio.PyAudio:
        """Get or create PyAudio instance with proper error handling.

        Returns:
            PyAudio instance

        Raises:
            RuntimeError: If PyAudio is not available
        """
        if not PYAUDIO_AVAILABLE:
            raise RuntimeError(
                "PyAudio library is not installed. " "Install with: pip install pyaudio"
            )

        if self._pa is None:
            self._pa = pyaudio.PyAudio()

        return self._pa

    def __del__(self) -> None:
        """Cleanup PyAudio instance on deletion."""
        if self._pa is not None:
            self._pa.terminate()

    def is_available(self) -> bool:
        """Check if PyAudio is available."""
        return PYAUDIO_AVAILABLE

    def get_backend_name(self) -> str:
        """Get backend name."""
        return "WASAPI"

    def get_available_devices(
        self, include_loopback: bool = False
    ) -> List[AudioDevice]:
        """Get list of available audio input devices.

        Args:
            include_loopback: Whether to include loopback/virtual audio devices
                            (On Windows, this includes devices with "loopback" in the name)

        Returns:
            List of AudioDevice objects

        Raises:
            RuntimeError: If device enumeration fails or PyAudio is not available
        """
        pa = self._get_pyaudio()
        devices = []

        try:
            device_count = pa.get_device_count()

            for i in range(device_count):
                try:
                    info = pa.get_device_info_by_index(i)

                    # Only include input devices (maxInputChannels > 0)
                    if info.get("maxInputChannels", 0) > 0:
                        device_name = info.get("name", f"Device {i}")

                        # If include_loopback is False, skip loopback-like devices
                        if not include_loopback:
                            # Check if device name suggests it's a loopback device
                            loopback_keywords = [
                                "stereo mix",
                                "what u hear",
                                "wave out",
                                "loopback",
                            ]
                            if any(
                                kw in device_name.lower() for kw in loopback_keywords
                            ):
                                continue

                        device = AudioDevice(
                            device=info, name=device_name, device_id=str(i)
                        )
                        devices.append(device)

                except Exception:
                    # Skip devices that cause errors during enumeration
                    continue

            return devices

        except Exception as e:
            raise RuntimeError(f"Failed to enumerate audio devices: {e}") from e

    def get_default_device(self) -> AudioDevice:
        """Get the system's default audio input device.

        Returns:
            AudioDevice object for the default input

        Raises:
            RuntimeError: If no default device is available or PyAudio is not installed
        """
        pa = self._get_pyaudio()

        try:
            # Get default input device info
            default_info = pa.get_default_input_device_info()

            if default_info is None:
                raise RuntimeError("No default input device found")

            device_id = str(default_info.get("index", 0))
            device_name = default_info.get("name", "Default Input")

            return AudioDevice(
                device=default_info, name=device_name, device_id=device_id
            )

        except Exception as e:
            raise RuntimeError(f"Failed to get default input device: {e}") from e

    def record_chunk(
        self, device: AudioDevice, duration: float
    ) -> Optional[np.ndarray]:
        """Record an audio chunk from the specified device.

        Args:
            device: AudioDevice to record from (must be a PyAudio device)
            duration: Duration to record in seconds

        Returns:
            Numpy array of audio samples (1D for mono) or None on failure

        Raises:
            RuntimeError: If recording fails
            ValueError: If device is invalid
        """
        if not isinstance(device, AudioDevice):
            raise ValueError("Invalid device type - must be AudioDevice")

        pa = self._get_pyaudio()

        try:
            # Get device index
            device_index = int(device.id)

            # Calculate chunk size
            chunk_size = 1024  # Read in chunks for better performance
            num_chunks = int((self.sample_rate * duration) / chunk_size)

            # Open audio stream
            stream = pa.open(
                format=pyaudio.paFloat32,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=chunk_size,
            )

            # Record audio in chunks
            frames = []
            for _ in range(num_chunks):
                data = stream.read(chunk_size, exception_on_overflow=False)
                frames.append(data)

            # Close stream
            stream.stop_stream()
            stream.close()

            # Convert bytes to numpy array
            audio_bytes = b"".join(frames)
            audio_data = np.frombuffer(audio_bytes, dtype=np.float32)

            # Ensure mono output
            if self.channels > 1:
                # Reshape to (samples, channels) and take mean across channels
                audio_data = audio_data.reshape(-1, self.channels).mean(axis=1)

            return audio_data

        except Exception as e:
            raise RuntimeError(f"Failed to capture audio: {e}") from e
