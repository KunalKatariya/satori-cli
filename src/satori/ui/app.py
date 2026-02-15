"""Main Textual TUI application for Satori."""

import asyncio
import logging
from collections import deque
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

import numpy as np
from rich.text import Text
from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, RichLog, Static

from satori.audio import AudioCapture

if TYPE_CHECKING:
    from satori.ai.translator import Translator

logger = logging.getLogger(__name__)


class UILogHandler(logging.Handler):
    """Custom logging handler that stores log messages for UI display."""

    def __init__(self, max_logs: int = 10) -> None:
        """Initialize the handler.

        Args:
            max_logs: Maximum number of log messages to keep
        """
        super().__init__()
        self.logs: deque = deque(maxlen=max_logs)

    def emit(self, record: logging.LogRecord) -> None:
        """Store log record.

        Args:
            record: The log record
        """
        msg = self.format(record)
        self.logs.append(msg)


class StatusBar(Static):
    """Status bar showing recording and processing state."""

    def __init__(self, name: str = "status") -> None:
        """Initialize status bar.

        Args:
            name: Widget name
        """
        super().__init__(name=name)
        self.status_text = "Ready"

    def render(self) -> Text:
        """Render the status bar.

        Returns:
            Status bar text as Rich Text
        """
        return Text(self.status_text, style="bold")

    def set_status(self, status: str) -> None:
        """Update status text.

        Args:
            status: New status text
        """
        self.status_text = status
        self.refresh()


class TranscriptionDisplay(RichLog):
    """Display area for live transcription."""

    def __init__(
        self, name: str = "transcription", log_handler: Optional[UILogHandler] = None
    ) -> None:
        """Initialize transcription display.

        Args:
            name: Widget name
            log_handler: Optional UILogHandler for displaying logs
        """
        super().__init__(
            name=name, highlight=False, markup=True, auto_scroll=True, wrap=True
        )
        self.log_handler = log_handler
        self._has_content = False

    def update_transcription(self, text: str) -> None:
        """Update transcription text with auto-scroll.

        Args:
            text: New text to append
        """
        # Clear initial "Waiting for audio..." message on first real transcription
        if not self._has_content:
            self.clear()
            self._has_content = True

        # Write new text (RichLog will auto-scroll)
        self.write(text)


class TranslationDisplay(RichLog):
    """Display area for translations."""

    def __init__(self, name: str = "translation") -> None:
        """Initialize translation display.

        Args:
            name: Widget name
        """
        super().__init__(
            name=name, highlight=False, markup=True, auto_scroll=True, wrap=True
        )
        self._has_content = False

    def update_translation(self, text: str) -> None:
        """Update translation text with auto-scroll.

        Args:
            text: New translation text to append
        """
        if text:
            # Clear initial message on first real translation
            if not self._has_content:
                self.clear()
                self._has_content = True

            # Write new text (RichLog will auto-scroll)
            self.write(text)


class SatoriApp(App):
    """Main Satori CLI application with live transcription."""

    CSS = """
    Screen {
        layout: vertical;
        overflow: hidden;
    }

    StatusBar {
        height: 3;
        padding: 1;
    }

    TranscriptionDisplay {
        height: 1fr;
        border: solid #5fd7af;
    }

    TranslationDisplay {
        height: 1fr;
        border: solid #af87d7;
    }
    """

    TITLE = "Satori - Live Translation"
    BINDINGS = [
        ("ctrl+c", "quit", "Exit"),
        ("ctrl+r", "reset", "Reset"),
    ]

    def __init__(
        self,
        audio_capture: Optional[AudioCapture] = None,
        whisper_transcriber: Any = None,
        translator: Optional["Translator"] = None,
    ) -> None:
        """Initialize Satori app with audio and transcription components.

        Args:
            audio_capture: AudioCapture instance for audio input
            whisper_transcriber: WhisperTranscriber instance for transcription
            translator: Translator instance for translation (optional)
        """
        super().__init__()
        self.audio_capture = audio_capture
        self.whisper_transcriber = whisper_transcriber
        self.translator = translator
        self.is_recording = False
        self.transcription_text = ""
        self.translation_text = ""
        self.audio_loop_task: Optional[asyncio.Task] = None
        self.log_handler = UILogHandler(max_logs=10)
        self.last_timestamp_time = datetime.now()

    def compose(self) -> ComposeResult:
        """Compose the UI.

        Yields:
            Widgets for the application
        """
        yield Header(show_clock=False)
        yield StatusBar()
        yield TranscriptionDisplay(log_handler=self.log_handler)
        yield TranslationDisplay()
        yield Footer()

    def on_mount(self) -> None:
        """Called when the app is mounted."""
        # Set up logging to display in UI
        root_logger = logging.getLogger()
        self.log_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
        self.log_handler.setLevel(logging.DEBUG)
        root_logger.addHandler(self.log_handler)

        status_bar = self.query_one(StatusBar)
        transcription_widget = self.query_one(TranscriptionDisplay)
        translation_widget = self.query_one(TranslationDisplay)

        # Show initial messages
        transcription_widget.write("[dim]Waiting for audio...[/dim]")

        if self.translator:
            translation_widget.write(
                f"[dim]Translation enabled: Auto-detect → {self.translator.target_language.upper()}[/dim]"
            )
        else:
            translation_widget.write(
                "[dim]Translation disabled. Use --translate-to to enable.[/dim]"
            )

        # Start audio capture if components are available
        if self.audio_capture and self.whisper_transcriber:
            status_bar.set_status("🎤 Initializing audio...")
            self.is_recording = True

            try:
                # Start audio capture
                self.audio_capture.start_recording()
                self.audio_loop_task = asyncio.create_task(self._audio_loop())
                status_bar.set_status(
                    "🎤 Recording... (Ctrl+R to reset, Ctrl+C to exit)"
                )
            except Exception as e:
                import traceback

                error_msg = f"{type(e).__name__}: {str(e)}"
                logger.error(f"Failed to start audio capture: {error_msg}")
                logger.error(traceback.format_exc())
                status_bar.set_status(f"❌ {error_msg[:50]}")
        else:
            status_bar.set_status("⏹ No audio configured - (Ctrl+C to exit)")

    async def _audio_loop(self) -> None:
        """Background task for continuous audio capture and transcription with VAD."""
        if not self.audio_capture or not self.whisper_transcriber:
            return

        status_bar = self.query_one(StatusBar)
        transcription_widget = self.query_one(TranscriptionDisplay)

        # VAD-based phrase detection with real-time processing
        phrase_buffer = []  # Accumulates audio until phrase boundary
        phrase_duration = 0.0

        # Energy threshold for speech detection (tune based on your environment)
        energy_threshold = 0.0015  # Even lower to catch all speech

        # Track silence duration
        last_speech_time = None
        phrase_timeout = 2.0  # Wait 2 seconds of silence for complete thoughts

        # Max phrase duration for real-time feedback (don't wait for silence)
        max_phrase_duration = 4.0  # Reduced from 6s for lower latency

        # Track if we're currently in a phrase
        in_phrase = False

        while self.is_recording:
            try:
                # Capture small audio chunk (0.5 second for responsiveness)
                chunk = self.audio_capture.get_audio_chunk(0.5)

                if chunk is None:
                    await asyncio.sleep(0.1)
                    continue

                # Calculate audio energy (RMS) for VAD
                audio_energy = float(np.sqrt(np.mean(chunk**2)))

                # Visual feedback
                level_bars = int(audio_energy * 1000)
                level_indicator = "▮" * min(level_bars, 20)

                # Detect speech vs silence
                is_speech = audio_energy > energy_threshold
                current_time = datetime.now()

                if is_speech:
                    last_speech_time = current_time
                    if not in_phrase:
                        in_phrase = True
                    status_bar.set_status(f"🎤 Recording... {level_indicator}")

                    # Add audio to phrase buffer
                    phrase_buffer.append(chunk)
                    phrase_duration += 0.5
                else:
                    status_bar.set_status(f"🔇 Silence... {level_indicator}")

                    # Still add silence to buffer if we're in a phrase (natural pauses)
                    if in_phrase and phrase_duration < max_phrase_duration:
                        phrase_buffer.append(chunk)
                        phrase_duration += 0.5

                # Transcribe if: 1) Hit max duration (real-time), 2) Detected silence after speech, or 3) Safety max (30s)
                should_transcribe = False

                if in_phrase and phrase_duration > 0.5:
                    # Real-time: transcribe every 4s even without pause
                    if phrase_duration >= max_phrase_duration:
                        should_transcribe = True

                    # Natural boundary: 1.5s silence after speech
                    elif last_speech_time:
                        silence_duration = (
                            current_time - last_speech_time
                        ).total_seconds()
                        if silence_duration >= phrase_timeout:
                            should_transcribe = True

                    # Safety: max 30s to prevent memory issues
                    if phrase_duration >= 30.0:
                        should_transcribe = True

                if should_transcribe:
                    # Concatenate accumulated phrase audio
                    full_audio = np.concatenate(phrase_buffer)

                    # Log audio duration for debugging
                    audio_duration = phrase_duration
                    logger.info(
                        f"Transcribing {audio_duration:.1f}s of audio ({len(phrase_buffer)} chunks)"
                    )

                    # Transcribe the complete phrase
                    status_bar.set_status(
                        f"⚙️ Processing {audio_duration:.1f}s audio..."
                    )
                    text = self.whisper_transcriber.transcribe(full_audio)

                    if text.strip():
                        # Add timestamp only every 30 seconds
                        time_since_last_timestamp = (
                            current_time - self.last_timestamp_time
                        ).total_seconds()

                        if time_since_last_timestamp >= 30:
                            timestamp = current_time.strftime("%H:%M:%S")
                            timestamped_text = f"\n\n[{timestamp}]\n{text}"
                            self.last_timestamp_time = current_time
                        else:
                            # Continue with space for natural flow
                            timestamped_text = f" {text}"

                        # Accumulate transcription
                        self.transcription_text += timestamped_text
                        transcription_widget.update_transcription(timestamped_text)

                        # Translate if translator is enabled
                        if self.translator:
                            import time

                            translation_start = time.time()
                            status_bar.set_status("🌐 Translating...")
                            try:
                                translated = self.translator.translate(text.strip())
                                translation_time = time.time() - translation_start

                                if translated:
                                    logger.info(
                                        f"Translation took {translation_time:.2f}s"
                                    )

                                    # Add same formatting to translation
                                    if time_since_last_timestamp >= 30:
                                        translated_timestamped = (
                                            f"\n\n[{timestamp}]\n{translated}"
                                        )
                                    else:
                                        translated_timestamped = f" {translated}"

                                    self.translation_text += translated_timestamped
                                    translation_widget = self.query_one(
                                        TranslationDisplay
                                    )
                                    translation_widget.update_translation(
                                        translated_timestamped
                                    )

                                    # Log if translation didn't change anything
                                    if translated == text.strip():
                                        logger.warning(
                                            "Translation returned same text as original"
                                        )
                            except Exception as e:
                                logger.error(f"Translation error: {e}")
                                import traceback

                                logger.error(traceback.format_exc())

                        status_bar.set_status("✓ Transcribed")
                        await asyncio.sleep(0.2)  # Brief pause for feedback

                    # Reset for next phrase
                    phrase_buffer = []
                    phrase_duration = 0.0
                    in_phrase = False
                    last_speech_time = None

                # Small sleep to prevent CPU overload
                await asyncio.sleep(0.05)

            except Exception as e:
                import traceback

                error_msg = f"{type(e).__name__}: {str(e)}"
                logger.error(f"Transcription error: {error_msg}")
                logger.error(traceback.format_exc())

                # Print full error to stdout for easy copying from terminal
                full_traceback = traceback.format_exc()
                print(f"\n{'='*80}", flush=True)
                print(f"TRANSCRIPTION ERROR:\n{error_msg}", flush=True)
                print(f"\nFull traceback:\n{full_traceback}", flush=True)
                print(f"{'='*80}\n", flush=True)

                # Show more of the error message (100 chars instead of 50)
                status_bar.set_status(f"❌ {error_msg[:100]}")
                await asyncio.sleep(1)

    def action_reset(self) -> None:
        """Reset transcription and translation."""
        transcription = self.query_one(TranscriptionDisplay)
        translation = self.query_one(TranslationDisplay)

        # Clear both displays and reset content flags
        transcription.clear()
        transcription.write("[dim]Waiting for audio...[/dim]")
        transcription._has_content = False

        translation.clear()
        if self.translator:
            translation.write(
                f"[dim]Translation enabled: Auto-detect → {self.translator.target_language.upper()}[/dim]"
            )
        else:
            translation.write(
                "[dim]Translation disabled. Use --translate-to to enable.[/dim]"
            )
        translation._has_content = False

        self.transcription_text = ""
        self.translation_text = ""
        self.last_timestamp_time = datetime.now()
        status_bar = self.query_one(StatusBar)
        status_bar.set_status("↻ Reset - Ready for new input")

    async def on_unmount(self) -> None:
        """Clean up when app unmounts."""
        self.is_recording = False
        if self.audio_capture:
            try:
                self.audio_capture.stop_recording()
            except Exception as e:
                logger.error(f"Error stopping audio capture: {e}")

        if self.audio_loop_task:
            self.audio_loop_task.cancel()
