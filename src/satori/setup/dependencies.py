"""Dependency installer for Satori CLI."""

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


class DependencyInstaller:
    """Handles installation of system dependencies."""

    @staticmethod
    def check_homebrew() -> bool:
        """Check if Homebrew is installed.

        Returns:
            True if Homebrew is available, False otherwise
        """
        try:
            result = subprocess.run(
                ["which", "brew"], capture_output=True, text=True, timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False

    @staticmethod
    def check_blackhole() -> bool:
        """Check if BlackHole is installed.

        Returns:
            True if BlackHole is installed, False otherwise
        """
        try:
            # Check if BlackHole is installed via Homebrew
            result = subprocess.run(
                ["brew", "list", "blackhole-2ch"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return True

            # Check if BlackHole audio device exists
            result = subprocess.run(
                ["system_profiler", "SPAudioDataType"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return "BlackHole" in result.stdout
        except Exception:
            return False

    @staticmethod
    def install_blackhole() -> Tuple[bool, str]:
        """Install BlackHole using Homebrew.

        Returns:
            Tuple of (success: bool, message: str)
        """
        if not DependencyInstaller.check_homebrew():
            return (
                False,
                "Homebrew not found. Please install from https://brew.sh/",
            )

        try:
            console.print("   [dim]Installing BlackHole via Homebrew...[/dim]")

            result = subprocess.run(
                ["brew", "install", "blackhole-2ch"],
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            if result.returncode == 0:
                return (True, "BlackHole installed successfully")
            else:
                return (
                    False,
                    f"Installation failed: {result.stderr[:200]}",
                )

        except subprocess.TimeoutExpired:
            return (False, "Installation timeout - please try manually")
        except Exception as e:
            return (False, f"Installation error: {str(e)}")

    @staticmethod
    def check_whisper_cpp() -> Optional[Path]:
        """Check if whisper.cpp is installed.

        Returns:
            Path to binary if found, None otherwise
        """
        from satori.ai.whisper_cpp import find_whisper_binary

        return find_whisper_binary()

    @staticmethod
    def check_git() -> bool:
        """Check if git is installed.

        Returns:
            True if git is available, False otherwise
        """
        try:
            result = subprocess.run(
                ["which", "git"], capture_output=True, text=True, timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False

    @staticmethod
    def check_make() -> bool:
        """Check if make is installed.

        Returns:
            True if make is available, False otherwise
        """
        try:
            result = subprocess.run(
                ["which", "make"], capture_output=True, text=True, timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False

    @staticmethod
    def install_whisper_cpp() -> Tuple[bool, str]:
        """Clone and build whisper.cpp with GPU support.

        Returns:
            Tuple of (success: bool, message: str)
        """
        # Check prerequisites
        if not DependencyInstaller.check_git():
            return (
                False,
                "git not found. Please install Xcode Command Line Tools: xcode-select --install",
            )

        if not DependencyInstaller.check_make():
            return (
                False,
                "make not found. Please install Xcode Command Line Tools: xcode-select --install",
            )

        whisper_dir = Path.home() / "whisper.cpp"

        try:
            # Step 1: Clone repository
            console.print("   [dim]Cloning whisper.cpp repository...[/dim]")

            if whisper_dir.exists():
                console.print(
                    "   [yellow]⚠[/yellow]  Directory ~/whisper.cpp already exists"
                )
                if not click.confirm("   Remove and re-clone?", default=False):
                    return (False, "Installation cancelled")

                # Remove existing directory
                subprocess.run(
                    ["rm", "-rf", str(whisper_dir)],
                    check=True,
                    timeout=30,
                )

            result = subprocess.run(
                [
                    "git",
                    "clone",
                    "https://github.com/ggerganov/whisper.cpp.git",
                    str(whisper_dir),
                ],
                capture_output=True,
                text=True,
                timeout=120,  # 2 minute timeout for clone
            )

            if result.returncode != 0:
                return (False, f"Clone failed: {result.stderr[:200]}")

            console.print("   [green]✓[/green] Repository cloned")

            # Step 2: Build with GPU support
            console.print(
                "   [dim]Building with Metal GPU support (this may take 3-5 minutes)...[/dim]"
            )

            # Detect platform for appropriate GPU flag
            platform = sys.platform
            if platform == "darwin":
                # macOS - use Metal
                make_command = ["make"]
                env = {"WHISPER_METAL": "1"}
            else:
                # Linux - try CUDA, fall back to CPU
                make_command = ["make"]
                env = {}
                console.print(
                    "   [dim]Note: CUDA detection will be attempted automatically[/dim]"
                )

            result = subprocess.run(
                make_command,
                cwd=str(whisper_dir),
                capture_output=True,
                text=True,
                timeout=600,  # 10 minute timeout for build
                env={**os.environ, **env},
            )

            if result.returncode != 0:
                return (
                    False,
                    f"Build failed: {result.stderr[:200]}\n\nTry running manually: cd ~/whisper.cpp && WHISPER_METAL=1 make",
                )

            # Verify build succeeded
            binary_path = whisper_dir / "build" / "bin" / "whisper-cli"
            if not binary_path.exists():
                # Try alternative path
                binary_path = whisper_dir / "main"

            if not binary_path.exists():
                return (False, "Build completed but binary not found")

            console.print("   [green]✓[/green] Build completed successfully")

            # Check if GPU support is enabled
            if "Metal" in result.stdout or "CUDA" in result.stdout:
                return (True, "whisper.cpp installed with GPU acceleration")
            else:
                return (True, "whisper.cpp installed (CPU-only mode)")

        except subprocess.TimeoutExpired:
            return (False, "Build timeout - please try manually")
        except Exception as e:
            return (False, f"Installation error: {str(e)}")

    @staticmethod
    def auto_setup_dependencies() -> Tuple[bool, bool]:
        """Interactively set up missing dependencies.

        Returns:
            Tuple of (blackhole_installed: bool, whisper_cpp_installed: bool)
        """
        blackhole_ok = False
        whisper_cpp_ok = False

        # Check and install BlackHole
        console.print("\n[bold]Checking dependencies...[/bold]\n")

        if DependencyInstaller.check_blackhole():
            console.print("   [green]✓[/green] BlackHole is installed")
            blackhole_ok = True
        else:
            console.print("   [yellow]⚠[/yellow]  BlackHole not found")

            if not DependencyInstaller.check_homebrew():
                console.print(
                    "\n[dim]BlackHole requires Homebrew for automatic installation[/dim]"
                )
                console.print("[dim]Install Homebrew: https://brew.sh/[/dim]")
                console.print(
                    "[dim]Or install BlackHole manually: https://existential.audio/blackhole/[/dim]\n"
                )
            else:
                console.print(
                    "\n[dim]BlackHole is required for system audio capture (YouTube, Spotify, etc.)[/dim]"
                )
                console.print("[dim]This will run: brew install blackhole-2ch[/dim]\n")

                if click.confirm("   Install BlackHole now?", default=True):
                    success, message = DependencyInstaller.install_blackhole()
                    if success:
                        console.print(f"   [green]✓[/green] {message}")
                        console.print(
                            "\n[yellow]Note:[/yellow] You may need to configure Multi-Output Device in Audio MIDI Setup"
                        )
                        console.print(
                            "[dim]See USAGE.md for audio configuration instructions[/dim]\n"
                        )
                        blackhole_ok = True
                    else:
                        console.print(f"   [red]✗[/red] {message}")
                else:
                    console.print(
                        "   [dim]Skipped - you can install later with: brew install blackhole-2ch[/dim]\n"
                    )

        # Check and install whisper.cpp
        if DependencyInstaller.check_whisper_cpp():
            binary_path = DependencyInstaller.check_whisper_cpp()
            console.print(
                f"   [green]✓[/green] whisper.cpp is installed: {binary_path}"
            )
            whisper_cpp_ok = True
        else:
            console.print("   [yellow]⚠[/yellow]  whisper.cpp not found")

            console.print(
                "\n[dim]whisper.cpp provides 30x faster transcription with GPU acceleration[/dim]"
            )
            console.print("[dim]Build time: ~3-5 minutes[/dim]")
            console.print("[dim]This will clone and build: ~/whisper.cpp[/dim]\n")

            if click.confirm("   Install and build whisper.cpp now?", default=True):
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                ) as progress:
                    progress.add_task("Installing whisper.cpp...", total=None)

                    success, message = DependencyInstaller.install_whisper_cpp()

                    progress.stop()

                if success:
                    console.print(f"   [green]✓[/green] {message}")
                    whisper_cpp_ok = True
                else:
                    console.print(f"   [red]✗[/red] {message}")
                    console.print(
                        "\n[dim]You can still use faster-whisper (CPU-only fallback)[/dim]"
                    )
                    console.print(
                        "[dim]Or install manually later - see WHISPER_SETUP.md[/dim]\n"
                    )
            else:
                console.print(
                    "   [dim]Skipped - you can use CPU-based faster-whisper instead[/dim]"
                )
                console.print(
                    "   [dim]Or install manually later - see WHISPER_SETUP.md[/dim]\n"
                )

        return (blackhole_ok, whisper_cpp_ok)
