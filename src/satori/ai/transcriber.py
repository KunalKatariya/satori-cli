"""Faster Whisper transcription service for Satori CLI."""

import logging
from typing import Optional

# CRITICAL: Import numpy FIRST before any other imports on ARM64 macOS
import numpy as np

from faster_whisper import WhisperModel

from satori.config.settings import WhisperConfig

logger = logging.getLogger(__name__)


class WhisperTranscriber:
    """Wrapper around Faster Whisper for speech-to-text transcription."""

    def __init__(self, config: WhisperConfig, use_multilingual: bool = False) -> None:
        """Initialize the Whisper transcriber.

        Args:
            config: WhisperConfig object with model settings
            use_multilingual: If True, use multilingual models instead of English-only

        Raises:
            ValueError: If model size is invalid
        """
        self.config = config
        self._model: Optional[WhisperModel] = None
        self._valid_models = ["tiny.en", "base.en", "small.en", "medium.en", "large-v2"]

        # Determine which model to use based on language requirements
        if use_multilingual or (
            config.language and config.language not in ["en", "auto"]
        ):
            # Use multilingual model for non-English languages
            self.model_name = (
                config.model_size if config.model_size != "large" else "large-v2"
            )
        else:
            # Use English-only models for better performance on English
            self.model_name = (
                f"{config.model_size}.en"
                if config.model_size in ["tiny", "base", "small", "medium"]
                else "base.en"
            )

        logger.debug(
            f"WhisperTranscriber initialized with model={self.model_name}, "
            f"language={config.language}, multilingual={use_multilingual}"
        )

    def _load_model(self) -> None:
        """Load the Whisper model lazily on first use.

        This downloads the model if not already cached locally.

        Raises:
            RuntimeError: If model download or initialization fails
        """
        if self._model is not None:
            return

        try:
            logger.info(f"Loading Faster Whisper model: {self.model_name}")

            # Use English-only model on CPU with int8 for speed
            self._model = WhisperModel(
                self.model_name,
                device="cpu",
                compute_type="int8",
                num_workers=1,
            )

            logger.info("Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}", exc_info=True)
            raise RuntimeError("Failed to load Whisper model. Check logs for details.")

    def is_model_loaded(self) -> bool:
        """Check if the model is already loaded in memory.

        Returns:
            True if model is loaded, False otherwise
        """
        return self._model is not None

    def transcribe(self, audio: np.ndarray) -> str:
        """Transcribe audio chunk to text using Whisper.

        Args:
            audio: Numpy array of audio samples (16kHz mono recommended)

        Returns:
            Transcribed text, or empty string if no speech detected

        Raises:
            RuntimeError: If transcription fails
        """
        if audio is None or len(audio) == 0:
            return ""

        try:
            # Load model if not already loaded
            if not self.is_model_loaded():
                self._load_model()

            # Model should be loaded at this point
            assert self._model is not None, "Whisper model failed to load"

            # Simple, straightforward audio conversion
            # Convert to numpy array if needed
            if not isinstance(audio, np.ndarray):
                audio = np.array(audio, dtype=np.float32)

            # Ensure float32
            if audio.dtype != np.float32:
                audio = audio.astype(np.float32)

            # Ensure it's C-contiguous
            if not audio.flags["C_CONTIGUOUS"]:
                audio = np.ascontiguousarray(audio, dtype=np.float32)

            # Ensure 1D
            if audio.ndim > 1:
                audio = audio.flatten()

            logger.debug(
                f"Audio ready - shape: {audio.shape}, dtype: {audio.dtype}, "
                f"min: {audio.min():.6f}, max: {audio.max():.6f}"
            )

            # Transcribe using Faster Whisper with streaming-optimized params
            # Pass language if specified (for multilingual models)
            transcribe_params = {
                "beam_size": 1,  # Greedy decoding for lowest latency
                "temperature": 0.0,  # Deterministic
                "compression_ratio_threshold": 2.4,
                "log_prob_threshold": -1.0,
                "no_speech_threshold": 0.6,
                "condition_on_previous_text": True,  # Better context
                "vad_filter": True,  # Voice activity detection
                "vad_parameters": dict(
                    min_silence_duration_ms=250,  # Aggressive VAD for speed
                    speech_pad_ms=150,
                ),
            }

            # Add language parameter if specified (for multilingual models)
            if self.config.language and self.config.language != "auto":
                transcribe_params["language"] = self.config.language

            segments, info = self._model.transcribe(audio, **transcribe_params)

            # Combine all segments into single text
            text = " ".join(segment.text for segment in segments).strip()

            if text:
                logger.debug(f"Transcribed: {text[:50]}...")

            return text

        except Exception as e:
            logger.error(f"Transcription failed: {e}", exc_info=True)
            # Include audio info in error for debugging
            error_details = f"Transcription failed: {str(e)}"
            if "audio" in locals():
                error_details += (
                    f" | Audio: shape={audio.shape}, dtype={audio.dtype}, "
                    f"ndim={audio.ndim}, C_CONTIGUOUS={audio.flags['C_CONTIGUOUS']}"
                )

            # Print to stdout for easy copying from terminal
            print(f"\n{'='*80}", flush=True)
            print(f"TRANSCRIPTION ERROR:\n{error_details}", flush=True)
            print(f"{'='*80}\n", flush=True)

            raise RuntimeError(error_details)

    def __repr__(self) -> str:
        """String representation of transcriber."""
        return (
            f"WhisperTranscriber(model={self.model_name}, "
            f"language={self.config.language})"
        )
