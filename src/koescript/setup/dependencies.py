"""Dependency installer for Koescript CLI with cross-platform support."""

import os
import subprocess
from pathlib import Path
from typing import Optional, Tuple

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from koescript.platform import get_platform_backend

console = Console()


class DependencyInstaller:
    """Handles installation of system dependencies with cross-platform support."""

    @staticmethod
    def check_virtual_audio_driver() -> bool:
        """Check if virtual audio driver is installed (platform-aware).

        Returns:
            True if virtual audio driver is installed, False otherwise
        """
        platform_backend = get_platform_backend()
        return platform_backend.audio.check_virtual_audio_driver()

    @staticmethod
    def install_virtual_audio_driver() -> Tuple[bool, str]:
        """Install virtual audio driver (platform-aware).

        Returns:
            Tuple of (success: bool, message: str)
        """
        platform_backend = get_platform_backend()

        # Show installation message with platform-specific driver name
        driver_info = platform_backend.audio.get_driver_info()
        console.print(f"   [dim]Installing {driver_info.name}...[/dim]")

        return platform_backend.audio.install_virtual_audio_driver()

    @staticmethod
    def check_whisper_cpp() -> Optional[Path]:
        """Check if whisper.cpp is installed.

        Returns:
            Path to binary if found, None otherwise
        """
        from koescript.ai.whisper_cpp import find_whisper_binary

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
                # Check if binary already exists (directory exists but not built)
                binary_path = whisper_dir / "build" / "bin" / "whisper-cli"
                alt_binary_path = whisper_dir / "main"

                if binary_path.exists() or alt_binary_path.exists():
                    # Directory exists and binary found - should have been detected earlier
                    console.print(
                        "   [yellow]⚠[/yellow]  whisper.cpp directory and binary already exist"
                    )
                    if not click.confirm("   Rebuild whisper.cpp?", default=False):
                        return (False, "Installation cancelled")
                else:
                    # Directory exists but binary not built - offer to build
                    console.print(
                        "   [yellow]⚠[/yellow]  whisper.cpp directory exists but binary not found"
                    )
                    console.print(
                        "   [dim]The repository was cloned but never compiled[/dim]"
                    )
                    if click.confirm("   Build whisper.cpp now?", default=True):
                        # Skip cloning, go straight to building
                        console.print("   [green]✓[/green] Using existing repository")
                    else:
                        if not click.confirm("   Remove and re-clone?", default=False):
                            return (False, "Installation cancelled")

                        # Remove existing directory
                        subprocess.run(
                            ["rm", "-rf", str(whisper_dir)],
                            check=True,
                            timeout=30,
                        )

            # Clone only if directory doesn't exist
            if not whisper_dir.exists():
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
            from koescript.platform import get_platform_backend

            platform_backend = get_platform_backend()
            gpu_info = platform_backend.gpu.detect_gpu()
            build_flags = platform_backend.gpu.get_whisper_build_flags()

            if gpu_info and gpu_info.supported:
                console.print(
                    f"   [dim]Building with {gpu_info.backend.upper()} GPU support ({gpu_info.name}) - this may take 3-5 minutes...[/dim]"
                )
            else:
                console.print(
                    "   [dim]Building in CPU-only mode - this may take 3-5 minutes...[/dim]"
                )
                if gpu_info and not gpu_info.supported:
                    console.print(
                        f"   [dim]Note: {gpu_info.backend.upper()} support coming in future version[/dim]"
                    )

            make_command = ["make"]

            result = subprocess.run(
                make_command,
                cwd=str(whisper_dir),
                capture_output=True,
                text=True,
                timeout=600,  # 10 minute timeout for build
                env={**os.environ, **build_flags},
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

        # Check and install virtual audio driver (platform-aware)
        console.print("\n[bold]Checking dependencies...[/bold]\n")

        platform_backend = get_platform_backend()
        driver_info = platform_backend.audio.get_driver_info()

        if DependencyInstaller.check_virtual_audio_driver():
            console.print(f"   [green]✓[/green] {driver_info.name} is installed")
            blackhole_ok = True
        else:
            console.print(f"   [yellow]⚠[/yellow]  {driver_info.name} not found")

            # Check if package manager is available
            if (
                platform_backend.package_manager is None
                or not platform_backend.package_manager.is_available()
            ):
                console.print(
                    f"\n[dim]{driver_info.name} automatic installation requires a package manager[/dim]"
                )
                console.print(
                    f"[dim]Please install {driver_info.name} manually[/dim]\n"
                )
            else:
                console.print(
                    f"\n[dim]{driver_info.name} is required for system audio capture (YouTube, Spotify, etc.)[/dim]"
                )
                console.print(
                    f"[dim]This will install via {platform_backend.package_manager.get_name()}[/dim]\n"
                )

                if click.confirm(f"   Install {driver_info.name} now?", default=True):
                    success, message = (
                        DependencyInstaller.install_virtual_audio_driver()
                    )
                    if success:
                        console.print(f"   [green]✓[/green] {message}")

                        # Platform-specific configuration notes
                        if platform_backend.get_platform_name() == "macOS":
                            console.print(
                                "\n[yellow]Note:[/yellow] You may need to configure Multi-Output Device in Audio MIDI Setup"
                            )
                            console.print(
                                "[dim]See README.md for audio configuration instructions[/dim]\n"
                            )
                        elif platform_backend.get_platform_name() == "Windows":
                            console.print(
                                "\n[yellow]Note:[/yellow] You may need to restart your system for the driver to take effect"
                            )
                            console.print(
                                "[dim]See README.md for audio configuration instructions[/dim]\n"
                            )
                        blackhole_ok = True
                    else:
                        console.print(f"   [red]✗[/red] {message}")
                else:
                    console.print(
                        f"   [dim]Skipped - you can install {driver_info.name} manually later[/dim]\n"
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
