"""Model downloader with progress tracking and user consent."""

import subprocess
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)

console = Console()


class ModelDownloader:
    """Manages model downloads with user consent and progress tracking."""

    # Model sizes (approximate - for display and rough validation)
    MODEL_SIZES = {
        "tiny": "75 MB",
        "tiny.en": "75 MB",
        "base": "142 MB",
        "base.en": "142 MB",
        "small": "466 MB",
        "small.en": "466 MB",
        "medium": "1.5 GB",
        "medium.en": "1.5 GB",
        "large": "2.9 GB",
        "large.en": "2.9 GB",
        "large-v2": "2.9 GB",
        "large-v3-turbo": "1.5 GB",
    }

    # Expected file sizes in bytes (for validation)
    MODEL_BYTES = {
        "tiny": 75 * 1024 * 1024,
        "tiny.en": 75 * 1024 * 1024,
        "base": 142 * 1024 * 1024,
        "base.en": 142 * 1024 * 1024,
        "small": 466 * 1024 * 1024,
        "small.en": 466 * 1024 * 1024,
        "medium": 1500 * 1024 * 1024,
        "medium.en": 1500 * 1024 * 1024,
        "large": 3000 * 1024 * 1024,  # ~3 GB
        "large.en": 3000 * 1024 * 1024,
        "large-v2": 3000 * 1024 * 1024,  # ~3 GB
        "large-v3-turbo": 1500 * 1024 * 1024,
    }

    def __init__(self, models_dir: Optional[Path] = None):
        """Initialize model downloader.

        Args:
            models_dir: Directory to store models (default: ~/.satori/models)
        """
        if models_dir is None:
            self.models_dir = Path.home() / ".satori" / "models" / "whisper"
        else:
            self.models_dir = Path(models_dir)

        self.models_dir.mkdir(parents=True, exist_ok=True)

    def get_model_path(self, model_name: str) -> Path:
        """Get path to model file.

        Args:
            model_name: Model name (e.g., 'base.en', 'medium')

        Returns:
            Path to model file
        """
        return self.models_dir / f"ggml-{model_name}.bin"

    def is_model_downloaded(self, model_name: str) -> bool:
        """Check if model is already downloaded.

        Args:
            model_name: Model name (e.g., 'base.en', 'medium')

        Returns:
            True if model exists locally
        """
        model_path = self.get_model_path(model_name)
        temp_path = model_path.with_suffix(".tmp")

        # Check if we have a complete .tmp file that needs to be finalized
        if not model_path.exists() and temp_path.exists():
            temp_size = temp_path.stat().st_size
            if temp_size > 1000000:  # At least 1MB, likely complete
                console.print(
                    f"[yellow]Found incomplete download:[/yellow] {temp_path.name}"
                )
                console.print(f"[dim]Size: {temp_size / (1024**3):.2f} GB[/dim]")
                console.print("[dim]Attempting to finalize download...[/dim]")
                try:
                    temp_path.rename(model_path)
                    console.print(
                        f"[green]✓[/green] Successfully recovered model [bold]{model_name}[/bold]"
                    )
                    return True
                except Exception as e:
                    console.print(f"[yellow]⚠[/yellow] Could not rename .tmp file: {e}")
                    console.print("[dim]Cleaning up and will re-download...[/dim]")
                    try:
                        temp_path.unlink()
                    except Exception:
                        pass
                    return False

        return (
            model_path.exists() and model_path.stat().st_size > 1000000
        )  # At least 1MB

    def request_download_consent(self, model_name: str) -> bool:
        """Ask user for consent to download model.

        Args:
            model_name: Model name to download

        Returns:
            True if user consents, False otherwise
        """
        size = self.MODEL_SIZES.get(model_name, "unknown size")

        console.print()
        console.print(
            f"[bold yellow]Model Required:[/bold yellow] Whisper [bold]{model_name}[/bold] model"
        )
        console.print(f"[dim]Size:[/dim] {size}")
        console.print(f"[dim]Location:[/dim] {self.models_dir}")
        console.print()
        console.print(
            "[dim]This is a one-time download. The model will be cached for future use.[/dim]"
        )
        console.print()

        return click.confirm("Download model now?", default=True)

    def download_model(self, model_name: str, force: bool = False) -> bool:
        """Download Whisper model with progress tracking.

        Args:
            model_name: Model name (e.g., 'base.en', 'medium')
            force: Force download even if model exists

        Returns:
            True if download succeeded, False otherwise
        """
        model_path = self.get_model_path(model_name)
        temp_path = model_path.with_suffix(".tmp")

        # Check if already downloaded
        if not force and self.is_model_downloaded(model_name):
            console.print(
                f"[green]✓[/green] Model [bold]{model_name}[/bold] already downloaded"
            )
            return True

        # Clean up any existing incomplete .tmp file
        if temp_path.exists():
            console.print("[dim]Cleaning up previous incomplete download...[/dim]")
            try:
                temp_path.unlink()
                console.print("[green]✓[/green] Cleanup successful")
            except Exception as e:
                console.print(f"[yellow]⚠[/yellow] Could not remove old .tmp file: {e}")

        # Request consent
        if not force and not self.request_download_consent(model_name):
            console.print("[yellow]Model download cancelled by user[/yellow]")
            return False

        # Download using HuggingFace (they host whisper.cpp models)
        base_url = "https://huggingface.co/ggerganov/whisper.cpp/resolve/main"
        model_url = f"{base_url}/ggml-{model_name}.bin"

        console.print("[dim]Starting download from HuggingFace...[/dim]")
        console.print(f"[dim]URL: {model_url}[/dim]")
        console.print(f"[dim]Downloading to: {temp_path}[/dim]")

        try:
            import urllib.request

            # Download with Rich progress bar
            with Progress(
                TextColumn("[bold blue]Downloading {task.fields[filename]}"),
                BarColumn(),
                DownloadColumn(),
                TransferSpeedColumn(),
                TimeRemainingColumn(),
                console=console,
            ) as progress:
                task_id = progress.add_task(
                    "download", filename=f"{model_name} model", total=None
                )

                def show_progress(block_num, block_size, total_size):
                    """Update progress bar."""
                    if total_size > 0:
                        downloaded = block_num * block_size
                        if progress.tasks[task_id].total is None:
                            progress.update(task_id, total=total_size)
                        progress.update(task_id, completed=min(downloaded, total_size))

                urllib.request.urlretrieve(model_url, temp_path, show_progress)

            # Verify download completed
            if not temp_path.exists():
                console.print(
                    "[bold red]✗[/bold red] Download failed: temp file not created"
                )
                return False

            temp_size = temp_path.stat().st_size
            console.print(
                f"[green]✓[/green] Download complete: {temp_size / (1024**3):.2f} GB"
            )

            # Validate file size (allow 10% variance)
            expected_bytes = self.MODEL_BYTES.get(model_name, 0)
            if expected_bytes > 0:
                min_size = expected_bytes * 0.9  # 10% tolerance
                if temp_size < min_size:
                    console.print("[bold red]✗[/bold red] Downloaded file too small!")
                    console.print(
                        f"[yellow]Expected:[/yellow] ~{expected_bytes / (1024**3):.2f} GB"
                    )
                    console.print(
                        f"[yellow]Got:[/yellow] {temp_size / (1024**3):.2f} GB"
                    )
                    console.print(
                        "[dim]The download may have been interrupted or corrupted[/dim]"
                    )
                    temp_path.unlink()  # Remove incomplete file
                    return False
                else:
                    console.print(
                        f"[green]✓[/green] File size validated ({temp_size / (1024**3):.2f} GB)"
                    )

            # Move to final location
            console.print(
                f"[dim]Finalizing: renaming {temp_path.name} → {model_path.name}[/dim]"
            )
            try:
                # Remove existing file if present (might be from earlier partial download)
                if model_path.exists():
                    console.print(
                        f"[dim]Removing existing file: {model_path.name}[/dim]"
                    )
                    model_path.unlink()

                # Now rename temp to final
                temp_path.rename(model_path)
                console.print("[green]✓[/green] Rename successful")
            except Exception as rename_error:
                console.print(
                    f"[bold red]✗[/bold red] Failed to rename file: {rename_error}"
                )

                # Check if file already exists at destination (might have been renamed already)
                if model_path.exists() and model_path.stat().st_size > 1000000:
                    console.print(
                        "[yellow]⚠[/yellow] But destination file exists and looks valid"
                    )
                    console.print("[dim]Cleaning up temp file...[/dim]")
                    try:
                        if temp_path.exists():
                            temp_path.unlink()
                    except Exception:
                        pass
                    # Consider this a success since the file is at the destination
                    pass  # Continue to verification below
                else:
                    console.print("[yellow]Manual fix:[/yellow] Run this command:")
                    console.print(f"  mv {temp_path} {model_path}")
                    return False

            # Verify final file
            if not model_path.exists():
                console.print(
                    "[bold red]✗[/bold red] Model file not found after rename"
                )
                return False

            final_size = model_path.stat().st_size
            console.print(
                f"[bold green]✓[/bold green] Model [bold]{model_name}[/bold] ready ({final_size / (1024**3):.2f} GB)"
            )
            return True

        except KeyboardInterrupt:
            console.print("\n[yellow]Download interrupted by user (Ctrl+C)[/yellow]")
            console.print(f"[dim]Incomplete download saved as: {temp_path}[/dim]")
            console.print(
                "[dim]Run the command again to resume or complete the download[/dim]"
            )
            return False

        except Exception as e:
            console.print(f"[bold red]✗[/bold red] Download failed: {e}")

            # Try fallback: use curl with silent mode
            console.print("[dim]Trying alternative download method (curl)...[/dim]")
            try:
                # Clean up failed attempt
                if temp_path.exists():
                    temp_path.unlink()

                result = subprocess.run(
                    [
                        "curl",
                        "-L",  # Follow redirects
                        "-s",  # Silent mode
                        "-S",  # Show errors
                        "-o",
                        str(model_path),
                        model_url,
                    ],
                    capture_output=True,
                    text=True,
                    timeout=600,
                )

                if (
                    result.returncode == 0
                    and model_path.exists()
                    and model_path.stat().st_size > 1000000
                ):
                    final_size = model_path.stat().st_size
                    console.print(
                        f"[bold green]✓[/bold green] Model [bold]{model_name}[/bold] downloaded via curl ({final_size / (1024**3):.2f} GB)"
                    )
                    return True
                else:
                    console.print("[bold red]✗[/bold red] curl download also failed")
                    if result.stderr:
                        console.print(f"[dim]Error: {result.stderr[:200]}[/dim]")

            except Exception as fallback_error:
                console.print(
                    f"[bold red]✗[/bold red] Fallback download failed: {fallback_error}"
                )

            return False

    def ensure_model(self, model_name: str) -> Path:
        """Ensure model is downloaded, download if necessary.

        Args:
            model_name: Model name (e.g., 'base.en', 'medium')

        Returns:
            Path to model file

        Raises:
            FileNotFoundError: If model cannot be downloaded
        """
        if not self.is_model_downloaded(model_name):
            if not self.download_model(model_name):
                raise FileNotFoundError(
                    f"Model '{model_name}' not found and download was cancelled or failed.\n\n"
                    f"You can manually download models from:\n"
                    f"https://huggingface.co/ggerganov/whisper.cpp/tree/main\n\n"
                    f"Place them in: {self.models_dir}"
                )

        return self.get_model_path(model_name)
