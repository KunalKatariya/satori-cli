"""Windows platform-specific implementations."""

import os
import subprocess
from typing import Dict, List, Optional, Tuple

from koescript.platform.base import (
    AudioDriverInfo,
    GPUInfo,
    PlatformAudioBackend,
    PlatformBackend,
    PlatformGPUBackend,
    PlatformPackageManager,
)


class WindowsAudioBackend(PlatformAudioBackend):
    """Windows-specific audio operations using VB-Cable."""

    def get_virtual_audio_keywords(self) -> List[str]:
        """Get keywords for detecting virtual audio devices on Windows."""
        return [
            "vb-cable",
            "cable output",
            "cable input",
            "virtual audio cable",
            "line 1",
            "voicemeeter",
        ]

    def check_virtual_audio_driver(self) -> bool:
        """Check if VB-Cable or similar is installed."""
        try:
            # Check Windows registry for VB-Cable
            result = subprocess.run(
                [
                    "reg",
                    "query",
                    "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall",
                    "/s",
                    "/f",
                    "VB-Audio VB-CABLE",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                return True

            # Alternative: Check for Virtual Audio Cable
            result = subprocess.run(
                [
                    "reg",
                    "query",
                    "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall",
                    "/s",
                    "/f",
                    "Virtual Audio Cable",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.returncode == 0

        except Exception:
            return False

    def install_virtual_audio_driver(self) -> Tuple[bool, str]:
        """Offer to install VB-Cable."""
        # Check if Chocolatey is available
        choco = ChocolateyManager()
        if choco.is_available():
            return choco.install_package("vb-cable")

        # Fallback: Provide manual installation instructions
        return (
            False,
            "VB-Cable must be installed manually. "
            "Download from https://vb-audio.com/Cable/ or install via Chocolatey: choco install vb-cable",
        )

    def get_driver_info(self) -> AudioDriverInfo:
        """Get VB-Cable driver information."""
        installed = self.check_virtual_audio_driver()
        return AudioDriverInfo(
            name="VB-Cable Virtual Audio Device", installed=installed
        )


class WindowsGPUBackend(PlatformGPUBackend):
    """Windows-specific GPU operations."""

    def detect_gpu(self) -> Optional[GPUInfo]:
        """Detect NVIDIA GPU on Windows."""
        # Check for NVIDIA GPU via nvidia-smi
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0 and result.stdout.strip():
                gpu_name = result.stdout.strip().split("\n")[0]
                return GPUInfo(backend="cuda", name=gpu_name, supported=True)
        except FileNotFoundError:
            pass
        except Exception:
            pass

        # Check for any GPU via PowerShell (for DirectML in future)
        try:
            ps_script = "Get-WmiObject Win32_VideoController | Select-Object -First 1 -ExpandProperty Name"
            result = subprocess.run(
                ["powershell", "-Command", ps_script],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0 and result.stdout.strip():
                gpu_name = result.stdout.strip()
                # For now, only CUDA is supported in v1.0
                # DirectML support coming in v1.1
                return GPUInfo(
                    backend="directml",
                    name=gpu_name,
                    supported=False,  # Not yet supported
                )
        except Exception:
            pass

        return None

    def get_whisper_build_flags(self) -> Dict[str, str]:
        """Get CUDA build flags for whisper.cpp."""
        gpu_info = self.detect_gpu()
        if gpu_info and gpu_info.backend == "cuda":
            return {"WHISPER_CUDA": "1"}
        # DirectML support coming in v1.1
        # elif gpu_info and gpu_info.backend == "directml":
        #     return {"WHISPER_DIRECTML": "1"}
        return {}


class ChocolateyManager(PlatformPackageManager):
    """Chocolatey package manager for Windows."""

    def is_available(self) -> bool:
        """Check if Chocolatey is installed."""
        try:
            result = subprocess.run(
                ["choco", "--version"], capture_output=True, text=True, timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, Exception):
            return False

    def get_name(self) -> str:
        """Get package manager name."""
        return "chocolatey"

    def install_package(
        self, package_name: str, timeout: int = 300
    ) -> Tuple[bool, str]:
        """Install package via Chocolatey."""
        try:
            # Chocolatey requires admin privileges
            result = subprocess.run(
                ["choco", "install", package_name, "-y"],
                capture_output=True,
                text=True,
                timeout=timeout,
            )

            if result.returncode == 0:
                return (True, f"{package_name} installed successfully")
            else:
                return (
                    False,
                    f"Installation failed: {result.stderr[:200]}. "
                    "Make sure you're running as Administrator.",
                )

        except subprocess.TimeoutExpired:
            return (False, "Installation timeout - please try manually")
        except Exception as e:
            return (False, f"Installation error: {str(e)}")

    def check_package_installed(self, package_name: str) -> bool:
        """Check if package is installed via Chocolatey."""
        try:
            result = subprocess.run(
                ["choco", "list", "--local-only", package_name],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return (
                result.returncode == 0 and package_name.lower() in result.stdout.lower()
            )
        except Exception:
            return False


class ScoopManager(PlatformPackageManager):
    """Scoop package manager for Windows."""

    def is_available(self) -> bool:
        """Check if Scoop is installed."""
        try:
            result = subprocess.run(
                ["scoop", "--version"], capture_output=True, text=True, timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, Exception):
            return False

    def get_name(self) -> str:
        """Get package manager name."""
        return "scoop"

    def install_package(
        self, package_name: str, timeout: int = 300
    ) -> Tuple[bool, str]:
        """Install package via Scoop."""
        try:
            result = subprocess.run(
                ["scoop", "install", package_name],
                capture_output=True,
                text=True,
                timeout=timeout,
            )

            if result.returncode == 0:
                return (True, f"{package_name} installed successfully")
            else:
                return (False, f"Installation failed: {result.stderr[:200]}")

        except subprocess.TimeoutExpired:
            return (False, "Installation timeout - please try manually")
        except Exception as e:
            return (False, f"Installation error: {str(e)}")

    def check_package_installed(self, package_name: str) -> bool:
        """Check if package is installed via Scoop."""
        try:
            result = subprocess.run(
                ["scoop", "list", package_name],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.returncode == 0
        except Exception:
            return False


class WindowsBackend(PlatformBackend):
    """Combined Windows platform backend."""

    def _create_audio_backend(self) -> PlatformAudioBackend:
        """Create Windows audio backend."""
        return WindowsAudioBackend()

    def _create_gpu_backend(self) -> PlatformGPUBackend:
        """Create Windows GPU backend."""
        return WindowsGPUBackend()

    def _create_package_manager(self) -> Optional[PlatformPackageManager]:
        """Create package manager (Chocolatey or Scoop)."""
        # Try Chocolatey first
        choco = ChocolateyManager()
        if choco.is_available():
            return choco

        # Try Scoop
        scoop = ScoopManager()
        if scoop.is_available():
            return scoop

        # No package manager available
        return None

    def get_platform_name(self) -> str:
        """Get platform name."""
        return "Windows"

    def setup_environment(self) -> None:
        """Setup Windows-specific environment variables."""
        # Thread limits for numerical libraries
        os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
        os.environ.setdefault("OMP_NUM_THREADS", "1")

        # MKL settings for Intel CPUs (if available)
        os.environ.setdefault("MKL_NUM_THREADS", "1")
