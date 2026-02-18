"""Audio capture and processing module for Koescript CLI."""

from koescript.audio.backends import AudioDevice
from koescript.audio.capture import AudioCapture
from koescript.audio.devices import DeviceConfig, DeviceManager

__all__ = ["AudioCapture", "AudioDevice", "DeviceConfig", "DeviceManager"]
