#!/usr/bin/env python3
"""
Satori CLI - Main entry point
"""

__version__ = "0.1.1"

import os
import sys
import multiprocessing

# CRITICAL: Import numpy FIRST before any data science imports on ARM64 macOS
# See: https://github.com/OpenNMT/CTranslate2/issues/1181
# This must happen before importing faster-whisper/ctranslate2
import numpy as np  # noqa: F401

# Set multiprocessing start method to 'fork' BEFORE anything imports multiprocessing
if sys.platform == "darwin":
    try:
        multiprocessing.set_start_method("fork", force=True)
    except RuntimeError:
        # Already set, that's fine
        pass

# Set macOS fork safety BEFORE any other imports
# These must be set at module load time
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")
os.environ.setdefault("ACCELERATE_LAPACK", "1")
os.environ.setdefault("ACCELERATE_BLAS_MULTI_THREAD", "0")
os.environ.setdefault("PYTHONHASHSEED", "0")

# Disable fork warnings and unsafe behaviors on macOS
if sys.platform == "darwin":
    os.environ.setdefault("PYTHONWARNINGS", "ignore::RuntimeWarning")
    os.environ.setdefault("OBJC_DISABLE_INITIALIZE_FORK_SAFETY", "YES")

import click
from rich.console import Console
from rich.text import Text

from koescript.ai import Translator
from koescript.ai.whisper_cpp import WhisperCppTranscriber
from koescript.audio import AudioCapture
from koescript.models import ModelDownloader
from koescript.ui.app import KoescriptApp

# Set up file logging
import logging
from pathlib import Path

log_dir = Path.home() / ".koescript" / "logs"
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / "satori.log"

file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
file_handler.setFormatter(file_formatter)

root_logger = logging.getLogger()
root_logger.addHandler(file_handler)
root_logger.setLevel(logging.DEBUG)

console = Console()


def print_logo():
    """Display the Koescript logo on boot with gradient effect"""
    logo_lines = [
        "  _  _____  _____ ____   ____ ____  ___ ____ _____ ",
        " | |/ / _ \| ____/ ___| / ___|  _ \|_ _|  _ \_   _|",
        " | ' / | | |  _| \___ \| |   | |_) || || |_) || |  ",
        " | . \ |_| | |___ ___) | |___|  _ < | ||  __/ | |  ",
        " |_|\_\___/|_____|____/ \____|_| \_\___|_|    |_|",
    ]

    # Create gradient colors from blue to purple
    gradient_colors = [
        "bold bright_blue",
        "bold blue",
        "bold medium_purple1",
        "bold medium_purple3",
        "bold magenta",
    ]

    # Print each line with gradient effect
    for line, color in zip(logo_lines, gradient_colors):
        styled_line = Text(line, style=color)
        console.print(styled_line)

    # Version and tagline with gradient
    version_text = Text(f"v{__version__}", style="bold medium_purple1")
    tagline = Text("A powerful and intuitive CLI tool", style="dim medium_purple3")

    console.print()
    console.print(version_text)
    console.print(tagline)
    console.print()


@click.group(invoke_without_command=True)
@click.version_option(version=__version__, prog_name="koescript")
@click.pass_context
def cli(ctx):
    """
    Koescript - A powerful and intuitive CLI tool
    """
    # Show logo and version on first invocation
    if ctx.invoked_subcommand is None:
        print_logo()
        console.print(
            "[bold medium_purple1]Usage:[/bold medium_purple1] koescript [COMMAND] [OPTIONS]"
        )
        console.print("[bold medium_purple1]Commands:[/bold medium_purple1]")
        console.print(
            "  init          Initialize Koescript for first-time use (run this first!)"
        )
        console.print(
            "  devices       List available audio devices (microphones & loopback)"
        )
        console.print("  translate     Start live translation session")
        console.print("  config        Manage configuration")
        console.print()
        console.print("Run [bold blue]koescript --help[/bold blue] for more information")


@cli.command()
@click.option(
    "--model",
    "model_size",
    default="base",
    type=click.Choice(["tiny", "base", "small", "medium", "large"]),
    help="Initial Whisper model to download (default: base for quick start)",
)
@click.option(
    "--skip-download",
    is_flag=True,
    default=False,
    help="Skip model download during initialization",
)
@click.option(
    "--skip-deps",
    is_flag=True,
    default=False,
    help="Skip automatic dependency installation",
)
def init(model_size: str, skip_download: bool, skip_deps: bool):
    """Initialize Koescript for first-time use.

    This command performs initial setup:
    - Installs system dependencies (BlackHole, whisper.cpp) with your consent
    - Creates necessary directories
    - Downloads initial Whisper model (optional)
    - Verifies audio device availability

    Run this once before using 'koescript translate'.
    """
    console.print(
        "\n[bold medium_purple1]═══ Koescript Initialization ═══[/bold medium_purple1]\n"
    )

    # Step 1: Create directories
    console.print("[bold]1. Setting up directories...[/bold]")
    try:
        satori_dir = Path.home() / ".koescript"
        models_dir = satori_dir / "models" / "whisper"
        logs_dir = satori_dir / "logs"

        models_dir.mkdir(parents=True, exist_ok=True)
        logs_dir.mkdir(parents=True, exist_ok=True)

        console.print(f"   [green]✓[/green] Created: {satori_dir}")
        console.print(f"   [green]✓[/green] Models: {models_dir}")
        console.print(f"   [green]✓[/green] Logs: {logs_dir}")
    except Exception as e:
        console.print(f"   [red]✗[/red] Failed to create directories: {e}")
        raise click.ClickException(str(e))

    console.print()

    # Step 2: Auto-install dependencies (if not skipped)
    if not skip_deps:
        from koescript.setup import DependencyInstaller

        DependencyInstaller.auto_setup_dependencies()
    else:
        console.print(
            "[bold]2. Dependency check skipped[/bold] (--skip-deps flag used)\n"
        )

    # Step 3: Download initial model
    if not skip_download:
        console.print(
            f"[bold]3. Downloading initial Whisper model ({model_size})...[/bold]"
        )
        try:
            downloader = ModelDownloader()

            # Download multilingual model (works for all languages)
            model_name = model_size if model_size != "large" else "large-v2"

            if downloader.is_model_downloaded(model_name):
                console.print(
                    f"   [green]✓[/green] Model {model_name} already downloaded"
                )
            else:
                console.print(
                    f"\n[dim]Downloading {model_name} multilingual model...[/dim]"
                )
                if downloader.download_model(model_name):
                    console.print(
                        f"   [green]✓[/green] Model {model_name} downloaded successfully"
                    )
                else:
                    console.print(
                        "   [yellow]⚠[/yellow]  Model download skipped or failed"
                    )
                    console.print(
                        "[dim]Models will be downloaded automatically when you run 'koescript translate'[/dim]"
                    )
        except Exception as e:
            console.print(f"   [yellow]⚠[/yellow]  Model download error: {e}")
            console.print(
                "[dim]Models will be downloaded automatically when you run 'koescript translate'[/dim]"
            )
    else:
        console.print(
            "[bold]3. Model download skipped[/bold] (--skip-download flag used)"
        )

    console.print()

    # Step 4: Verify audio devices
    console.print("[bold]4. Verifying audio setup...[/bold]")
    try:
        audio_capture = AudioCapture()
        devices = audio_capture.get_available_devices()

        if devices:
            console.print(f"   [green]✓[/green] Found {len(devices)} audio device(s)")

            # Show loopback devices
            loopback_devices = [
                d
                for d in devices
                if any(
                    kw in d.name.lower()
                    for kw in ["blackhole", "loopback", "soundflower", "virtual"]
                )
            ]

            if loopback_devices:
                console.print(
                    f"   [green]✓[/green] Found {len(loopback_devices)} loopback device(s) for system audio:"
                )
                for dev in loopback_devices:
                    console.print(f"      • {dev.name}")
            else:
                console.print("   [yellow]⚠[/yellow]  No loopback devices found")
                console.print(
                    "\n[dim]Run 'satori init' again to install BlackHole automatically[/dim]"
                )
                console.print(
                    "[dim]Or install manually: brew install blackhole-2ch[/dim]"
                )
        else:
            console.print("   [yellow]⚠[/yellow]  No audio devices found")
    except Exception as e:
        console.print(f"   [yellow]⚠[/yellow]  Could not check audio devices: {e}")

    console.print()

    # Step 5: Summary
    console.print("[bold medium_purple1]═══ Setup Complete ═══[/bold medium_purple1]\n")
    console.print("[bold green]✓[/bold green] Koescript is ready to use!\n")
    console.print("[bold]Next steps:[/bold]")
    console.print("  1. List available audio devices:")
    console.print("     [cyan]koescript devices[/cyan]")
    console.print()
    console.print("  2. Start transcribing with microphone:")
    console.print("     [cyan]koescript translate[/cyan]")
    console.print()
    console.print("  3. Transcribe YouTube/Spotify (with BlackHole):")
    console.print("     [cyan]koescript translate --loopback[/cyan]")
    console.print()
    console.print("  4. Translate Japanese to English:")
    console.print(
        "     [cyan]koescript translate --loopback --language ja --translate-to en[/cyan]"
    )
    console.print()
    console.print("[dim]Run 'koescript --help' for more options[/dim]\n")


@cli.command()
def config():
    """Manage configuration"""
    console.print("[bold green]✓[/bold green] Configuration command")


@cli.command()
def devices():
    """List available audio devices including loopback devices for system audio capture.

    Loopback devices allow you to capture system audio directly (e.g., YouTube, Spotify).
    Common loopback devices: BlackHole, Loopback, Soundflower.
    """
    try:
        audio_capture = AudioCapture()
        devices = audio_capture.get_available_devices()

        console.print(
            "\n[bold medium_purple1]Available Audio Devices:[/bold medium_purple1]\n"
        )

        if not devices:
            console.print("[yellow]No audio devices found.[/yellow]")
            return

        for i, device in enumerate(devices, 1):
            # Try to identify loopback devices by common names
            is_loopback = any(
                keyword in device.name.lower()
                for keyword in [
                    "blackhole",
                    "loopback",
                    "soundflower",
                    "virtual",
                    "aggregate",
                ]
            )

            if is_loopback:
                console.print(
                    f"  [bold green]{i}.[/bold green] [bold]{device.name}[/bold] "
                    "[dim cyan](System Audio/Loopback)[/dim cyan]"
                )
            else:
                console.print(f"  [dim]{i}.[/dim] {device.name}")

        console.print(
            "\n[dim]Tip: Use loopback devices to capture YouTube, Spotify, etc.[/dim]"
        )
        console.print('[dim]Example: koescript translate --device "BlackHole 2ch"[/dim]\n')

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise click.ClickException(str(e))


@cli.command()
@click.option(
    "--device",
    default=None,
    help="Audio device name (e.g., 'BlackHole 2ch'). Use 'koescript devices' to list all.",
)
@click.option(
    "--loopback",
    is_flag=True,
    default=False,
    help="Auto-select first loopback device for system audio (YouTube, etc.)",
)
@click.option(
    "--model",
    "model_size",
    default="medium",
    type=click.Choice(["tiny", "base", "small", "medium", "large"]),
    help="Whisper model size (default: medium for best accuracy)",
)
@click.option(
    "--language",
    default="en",
    help="Source language code for transcription (e.g., 'ja' for Japanese, 'hi' for Hindi, 'en' for English). Use 'auto' to auto-detect.",
)
@click.option(
    "--translate-to",
    default=None,
    type=click.Choice(["en", "ja", "hi"]),
    help="Enable translation to target language: 'en' (English), 'ja' (Japanese), or 'hi' (Hindi)",
)
def translate(
    device: str, loopback: bool, model_size: str, language: str, translate_to: str
) -> None:
    """Start live translation session with real-time transcription.

    Captures audio from your configured device, transcribes with Whisper,
    and displays results in the Koescript TUI.

    For YouTube/Spotify transcription, use --loopback flag or specify a loopback device.
    Run 'koescript devices' to see available devices.

    \b
    Keyboard shortcuts:
      Ctrl+R - Reset transcription
      Ctrl+C - Exit application

    \b
    Examples:
      koescript translate --loopback  # YouTube with GPU acceleration
      koescript translate --device "BlackHole 2ch" --model small
      koescript translate --model large  # Use microphone, better accuracy
      koescript translate --loopback --language ja --translate-to en
    """
    console.print(
        "[bold medium_purple1]Launching Koescript live translation...[/bold medium_purple1]"
    )

    try:
        # Initialize audio capture
        audio_capture = AudioCapture(
            sample_rate=16000,
            channels=1,
        )

        # Select device: --loopback flag > CLI option > config > system default
        if loopback:
            # Auto-select first loopback device
            console.print(
                "[dim]Auto-selecting loopback device for system audio...[/dim]"
            )
            all_devices = audio_capture.get_available_devices()
            loopback_device = None

            for dev in all_devices:
                # Check for common loopback device names
                if any(
                    keyword in dev.name.lower()
                    for keyword in [
                        "blackhole",
                        "loopback",
                        "soundflower",
                        "virtual",
                        "aggregate",
                    ]
                ):
                    loopback_device = dev
                    break

            if loopback_device:
                console.print(
                    f"[bold green]✓[/bold green] Selected loopback: {loopback_device.name}"
                )
                audio_capture.set_device(loopback_device)
            else:
                console.print(
                    "[yellow]Warning: No loopback device found. "
                    "Install BlackHole or similar for system audio capture.[/yellow]"
                )
                console.print(
                    "[dim]Falling back to default microphone. "
                    "Run 'koescript devices' to see available devices.[/dim]"
                )
        elif device:
            console.print(f"[dim]Selecting device: {device}[/dim]")
            selected_device = audio_capture.get_device_by_name(device)
            if selected_device:
                audio_capture.set_device(selected_device)
            else:
                console.print(
                    f"[yellow]Warning: Device '{device}' not found. "
                    "Using system default.[/yellow]"
                )
        else:
            # Use default device
            try:
                default_device = audio_capture.get_default_device()
                console.print(f"[dim]Using default device: {default_device.name}[/dim]")
                audio_capture.set_device(default_device)
            except RuntimeError:
                console.print(
                    "[yellow]Warning: Could not detect default device. "
                    "Attempting to use any available device.[/yellow]"
                )

        # Initialize Whisper transcriber (whisper.cpp required)
        console.print(
            f"[dim]Loading Whisper model ({model_size})... "
            "This may take a minute on first run.[/dim]"
        )

        try:
            # Import here to avoid circular dependency
            from koescript.ai.whisper_cpp import find_whisper_binary

            # Check if whisper.cpp is installed first
            whisper_binary = find_whisper_binary()
            if whisper_binary is None:
                console.print("\n[bold red]✗ Error:[/bold red] whisper.cpp not found\n")
                console.print(
                    "[bold yellow]whisper.cpp is required for transcription[/bold yellow]"
                )
                console.print("\n[bold]To install whisper.cpp, run:[/bold]")
                console.print("  [cyan]satori init[/cyan]")
                console.print(
                    "\n[dim]This will automatically install and build whisper.cpp with GPU support.[/dim]"
                )
                raise click.ClickException(
                    "whisper.cpp not installed. Run 'satori init' to install."
                )

            # Initialize model downloader
            downloader = ModelDownloader()

            # Always use multilingual models (work for all languages including English)
            model_name = model_size if model_size != "large" else "large-v2"
            whisper_language = None if language == "auto" else language

            # Ensure model is downloaded
            try:
                model_path = downloader.ensure_model(model_name)
            except FileNotFoundError as model_error:
                # Model download was cancelled or failed
                console.print(
                    f"\n[bold red]✗ Model Error:[/bold red] {str(model_error)}"
                )
                raise click.ClickException(
                    f"Model '{model_name}' not available. Run 'satori init --model {model_size}' to download."
                )

            whisper_transcriber = WhisperCppTranscriber(
                model_path=str(model_path),
                beam_size=5,  # Max 8 for whisper.cpp, using 5 for good balance
                threads=8,
                language=whisper_language,
            )
            console.print(
                f"[bold green]✓[/bold green] Using GPU-accelerated whisper.cpp (multilingual, language: {whisper_language or 'auto-detect'})"
            )
        except click.ClickException:
            # Re-raise ClickException to show error message
            raise
        except FileNotFoundError as e:
            # This should rarely happen now, but keep for safety
            console.print(f"\n[bold red]✗ Error:[/bold red] {str(e)}")
            raise click.ClickException(str(e))

        # Initialize translator if requested
        translator = None
        if translate_to:
            console.print(
                "[dim]Loading Meta NLLB translation model (1.3B)... This may take a minute on first run.[/dim]"
            )
            translator = Translator(target_language=translate_to, model_size="1.3B")
            console.print(
                f"[bold green]✓[/bold green] Translation enabled: Meta NLLB-1.3B (Auto-detect → {translate_to.upper()})"
            )

        # Create and run the app
        app = KoescriptApp(
            audio_capture=audio_capture,
            whisper_transcriber=whisper_transcriber,
            translator=translator,
        )
        app.run()

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise click.ClickException(str(e))


def main():
    """Entry point for the CLI"""
    cli()


if __name__ == "__main__":
    main()
