"""Configuration management for Satori CLI."""

import json
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field


class WhisperConfig(BaseModel):
    """Whisper AI configuration."""

    model_size: str = Field(
        default="small", description="Model size: tiny, base, small"
    )
    language: Optional[str] = Field(default="en", description="Language code")
    beam_size: int = Field(default=5, description="Beam size for decoding")
    best_of: int = Field(default=5, description="Best of N candidates")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "model_size": "base",
                "language": "en",
                "beam_size": 5,
                "best_of": 5,
            }
        }


class TranslationConfig(BaseModel):
    """Translation configuration."""

    target_language: str = Field(default="en", description="Target language code")
    provider: str = Field(default="none", description="Translation provider")

    class Config:
        """Pydantic config."""

        json_schema_extra = {"example": {"target_language": "en", "provider": "none"}}


class SatoriConfig(BaseModel):
    """Main Satori configuration."""

    whisper: WhisperConfig = Field(default_factory=WhisperConfig)
    translation: TranslationConfig = Field(default_factory=TranslationConfig)
    auto_save: bool = Field(default=True, description="Auto-save transcriptions")
    log_directory: str = Field(
        default=str(Path.home() / ".satori" / "logs"),
        description="Directory for saving logs",
    )

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "whisper": {"model_size": "base", "language": "en"},
                "translation": {"target_language": "en", "provider": "none"},
                "auto_save": True,
                "log_directory": "~/.satori/logs",
            }
        }


class ConfigManager:
    """Manages Satori configuration."""

    def __init__(self, config_path: Optional[Path] = None) -> None:
        """Initialize config manager.

        Args:
            config_path: Path to config file (optional)
        """
        self.config_path = config_path or Path.home() / ".satori" / "config.json"
        self.config = self._load_config()

    def _load_config(self) -> SatoriConfig:
        """Load configuration from file or use defaults.

        Returns:
            SatoriConfig object
        """
        if self.config_path.exists():
            try:
                with open(self.config_path) as f:
                    data = json.load(f)
                return SatoriConfig(**data)
            except Exception:
                return SatoriConfig()
        return SatoriConfig()

    def save_config(self) -> None:
        """Save current configuration to file."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w") as f:
            json.dump(self.config.model_dump(), f, indent=2)

    def get_whisper_config(self) -> WhisperConfig:
        """Get Whisper configuration.

        Returns:
            WhisperConfig object
        """
        return self.config.whisper

    def set_whisper_model(self, model_size: str) -> None:
        """Set Whisper model size.

        Args:
            model_size: Model size (tiny, base, small)
        """
        if model_size not in ["tiny", "base", "small", "medium", "large"]:
            raise ValueError("Invalid model size")
        self.config.whisper.model_size = model_size
        self.save_config()

    def get_log_directory(self) -> Path:
        """Get log directory path.

        Returns:
            Path to log directory
        """
        log_dir = Path(self.config.log_directory).expanduser()
        log_dir.mkdir(parents=True, exist_ok=True)
        return log_dir
