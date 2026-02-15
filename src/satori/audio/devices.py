"""Device management for audio capture."""

import json
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field


class DeviceConfig(BaseModel):
    """Configuration for audio devices."""

    device_name: str = Field(default="default", description="Name of the audio device")
    sample_rate: int = Field(default=16000, description="Sample rate in Hz")
    channels: int = Field(default=1, description="Number of audio channels")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "device_name": "BlackHole 2ch",
                "sample_rate": 16000,
                "channels": 1,
            }
        }


class DeviceManager:
    """Manages audio device configuration and selection."""

    def __init__(self, config_path: Optional[Path] = None) -> None:
        """Initialize the device manager.

        Args:
            config_path: Path to config file (optional)
        """
        self.config_path = config_path or Path.home() / ".satori" / "devices.json"
        self.config = self._load_config()

    def _load_config(self) -> DeviceConfig:
        """Load device configuration from file or use defaults.

        Returns:
            DeviceConfig object
        """
        if self.config_path.exists():
            try:
                with open(self.config_path) as f:
                    data = json.load(f)
                return DeviceConfig(**data)
            except Exception:
                return DeviceConfig()
        return DeviceConfig()

    def save_config(self) -> None:
        """Save current configuration to file."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w") as f:
            json.dump(self.config.model_dump(), f, indent=2)

    def set_device(self, device_name: str) -> None:
        """Set the active device.

        Args:
            device_name: Name of the device to use
        """
        self.config.device_name = device_name
        self.save_config()

    def get_device_name(self) -> str:
        """Get the currently configured device name.

        Returns:
            Name of the configured device
        """
        return self.config.device_name

    def set_sample_rate(self, sample_rate: int) -> None:
        """Set the sample rate.

        Args:
            sample_rate: Sample rate in Hz
        """
        if sample_rate <= 0:
            raise ValueError("Sample rate must be positive")
        self.config.sample_rate = sample_rate
        self.save_config()

    def get_sample_rate(self) -> int:
        """Get the configured sample rate.

        Returns:
            Sample rate in Hz
        """
        return self.config.sample_rate
