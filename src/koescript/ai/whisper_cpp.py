"""WhisperCpp transcription service with cross-platform support."""

import logging
import os
import platform
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

import numpy as np
import scipy.io.wavfile as wav

logger = logging.getLogger(__name__)


def find_whisper_binary() -> Optional[Path]:
    """Find whisper.cpp binary in common locations (cross-platform).

    Searches for whisper-cli binary on macOS/Linux and whisper-cli.exe on Windows.

    Returns:
        Path to binary if found, None otherwise
    """
    # Determine executable name based on platform
    is_windows = platform.system() == "Windows"
    binary_name = "whisper-cli.exe" if is_windows else "whisper-cli"
    alt_binary_name = "main.exe" if is_windows else "main"

    # Common installation paths (cross-platform)
    search_paths = [
        # User's home directory builds
        Path.home() / "whisper.cpp" / "build" / "bin" / binary_name,
        Path.home() / "whisper.cpp" / alt_binary_name,
        Path.home() / ".whisper.cpp" / "build" / "bin" / binary_name,
        Path.home() / ".whisper.cpp" / alt_binary_name,
    ]

    # Add platform-specific system paths
    if is_windows:
        search_paths.extend(
            [
                Path("C:/Program Files/whisper.cpp") / binary_name,
                Path("C:/Program Files (x86)/whisper.cpp") / binary_name,
            ]
        )
    else:
        search_paths.extend(
            [
                Path("/usr/local/bin") / binary_name,
                Path("/usr/bin") / binary_name,
            ]
        )

    # Check all search paths
    for path in search_paths:
        try:
            if path.exists() and path.is_file():
                return path
        except Exception:
            continue

    # Last resort: Check if in PATH
    try:
        if is_windows:
            # Windows: use 'where' command
            result = subprocess.run(
                ["where", binary_name],
                capture_output=True,
                text=True,
                timeout=5,
            )
        else:
            # macOS/Linux: use 'which' command
            result = subprocess.run(
                ["which", binary_name],
                capture_output=True,
                text=True,
                timeout=5,
            )

        if result.returncode == 0 and result.stdout.strip():
            return Path(result.stdout.strip().split("\n")[0])  # Take first match
    except Exception:
        pass

    return None


class WhisperCppTranscriber:
    """Wrapper around whisper.cpp binary for fast GPU-accelerated transcription."""

    def __init__(
        self,
        binary_path: Optional[str] = None,
        model_path: str = "",
        beam_size: int = 5,
        threads: int = 8,
        language: Optional[str] = "en",
    ) -> None:
        """Initialize WhisperCpp transcriber.

        Args:
            binary_path: Path to whisper-cli binary (auto-detected if None)
            model_path: Path to ggml model file
            beam_size: Beam size for decoding (1=greedy, 5=balanced, 10=best)
            threads: Number of CPU threads
            language: Language code (default: en, None for auto-detect)

        Raises:
            FileNotFoundError: If binary or model not found
        """
        # Auto-detect binary if not provided
        if binary_path is None:
            detected_binary = find_whisper_binary()
            if detected_binary is None:
                raise FileNotFoundError(
                    "whisper.cpp binary not found!\n\n"
                    "Install whisper.cpp with:\n\n"
                    "  # Clone repository\n"
                    "  cd ~\n"
                    "  git clone https://github.com/ggerganov/whisper.cpp.git\n"
                    "  cd whisper.cpp\n\n"
                    "  # Build with GPU support\n"
                    "  # For Apple Silicon (Metal):\n"
                    "  WHISPER_METAL=1 make\n\n"
                    "  # For NVIDIA GPUs (CUDA):\n"
                    "  WHISPER_CUDA=1 make\n\n"
                    "  # For CPU only:\n"
                    "  make\n\n"
                    "Alternatively, install via package manager or specify binary_path manually."
                )
            self.binary_path = detected_binary
        else:
            self.binary_path = Path(binary_path)

        self.model_path = Path(model_path)
        self.beam_size = beam_size
        self.threads = threads
        self.language = language

        # Validate paths
        if not self.binary_path.exists():
            raise FileNotFoundError(
                f"whisper.cpp binary not found at {self.binary_path}\n\n"
                "Please install whisper.cpp or specify correct binary_path."
            )

        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Model not found at {self.model_path}\n\n"
                "Models are managed by satori and should be downloaded automatically.\n"
                "If you see this error, there may be an issue with the model downloader."
            )

        logger.info(
            f"WhisperCppTranscriber initialized: model={self.model_path.name}, "
            f"beam_size={beam_size}, threads={threads}"
        )

    def transcribe(self, audio: np.ndarray, sample_rate: int = 16000) -> str:
        """Transcribe audio using whisper.cpp.

        Args:
            audio: Numpy array of audio samples (float32, mono)
            sample_rate: Sample rate in Hz (default: 16000)

        Returns:
            Transcribed text

        Raises:
            RuntimeError: If transcription fails
        """
        if audio is None or len(audio) == 0:
            return ""

        try:
            # Ensure audio is float32, mono, and C-contiguous
            if not isinstance(audio, np.ndarray):
                audio = np.array(audio, dtype=np.float32)

            if audio.dtype != np.float32:
                audio = audio.astype(np.float32)

            if audio.ndim > 1:
                audio = audio.flatten()

            if not audio.flags["C_CONTIGUOUS"]:
                audio = np.ascontiguousarray(audio, dtype=np.float32)

            # Normalize audio to int16 range
            audio_int16 = (audio * 32767).astype(np.int16)

            # Write to temporary WAV file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_wav:
                wav.write(tmp_wav.name, sample_rate, audio_int16)
                tmp_wav_path = tmp_wav.name

            try:
                # Build whisper.cpp command
                cmd = [
                    str(self.binary_path),
                    "-m",
                    str(self.model_path),
                    "-f",
                    tmp_wav_path,
                    "--beam-size",
                    str(self.beam_size),
                    "--threads",
                    str(self.threads),
                    "--no-timestamps",  # Faster, we don't need timestamps
                ]

                # Only add language flag if not auto-detect
                if self.language and self.language != "auto":
                    cmd.extend(["--language", self.language])

                logger.debug(f"Running: {' '.join(cmd)}")

                # Run whisper.cpp with timeout
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=30,  # 30 second timeout
                    check=False,
                )

                logger.debug(f"whisper.cpp return code: {result.returncode}")
                logger.debug(f"stdout length: {len(result.stdout)}")
                logger.debug(f"stderr length: {len(result.stderr)}")

                if result.returncode != 0:
                    logger.error(f"whisper.cpp failed with code {result.returncode}")
                    logger.error(f"stderr: {result.stderr[:500]}")
                    raise RuntimeError(
                        f"whisper.cpp transcription failed: {result.stderr[:200]}"
                    )

                # Parse output - whisper.cpp writes to stdout
                text = result.stdout

                # Filter out metadata lines - keep only transcription
                lines = []
                for line in text.split("\n"):
                    line_stripped = line.strip()
                    # Skip empty lines and metadata
                    if not line_stripped:
                        continue
                    if line_stripped.startswith("["):
                        continue
                    if line_stripped.startswith("whisper_"):
                        continue
                    if line_stripped.startswith("main:"):
                        continue
                    if line_stripped.startswith("system_info:"):
                        continue
                    if line_stripped.startswith("ggml_"):
                        continue
                    if "error:" in line_stripped.lower():
                        continue
                    # This is likely transcription text
                    lines.append(line_stripped)

                transcription = " ".join(lines).strip()

                if transcription:
                    logger.debug(f"Transcribed: {transcription[:50]}...")
                else:
                    logger.debug(
                        f"No transcription found. Raw output length: {len(text)}"
                    )

                return transcription

            finally:
                # Clean up temp file
                try:
                    os.unlink(tmp_wav_path)
                except Exception as e:
                    logger.warning(f"Failed to delete temp file {tmp_wav_path}: {e}")

        except subprocess.TimeoutExpired:
            logger.error("whisper.cpp transcription timeout")
            raise RuntimeError("Transcription timeout (>30s)")
        except Exception as e:
            logger.error(f"Transcription failed: {e}", exc_info=True)
            raise RuntimeError(f"Transcription failed: {str(e)}")

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"WhisperCppTranscriber(model={self.model_path.name}, "
            f"beam_size={self.beam_size})"
        )
