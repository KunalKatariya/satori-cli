"""macOS platform-specific implementations."""

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


class MacOSAudioBackend(PlatformAudioBackend):
    """macOS-specific audio operations using BlackHole."""

    def get_virtual_audio_keywords(self) -> List[str]:
        """Get keywords for detecting virtual audio devices on macOS."""
        return ["blackhole", "loopback", "soundflower", "virtual", "aggregate"]

    def check_virtual_audio_driver(self) -> bool:
        """Check if BlackHole is installed."""
        try:
            # Check via Homebrew first
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

    def install_virtual_audio_driver(self) -> Tuple[bool, str]:
        """Install BlackHole using Homebrew."""
        # Check if Homebrew is available
        package_manager = HomebrewManager()
        if not package_manager.is_available():
            return (
                False,
                "Homebrew not found. Please install from https://brew.sh/",
            )

        # Install BlackHole via Homebrew
        return package_manager.install_package("blackhole-2ch", timeout=300)

    def get_driver_info(self) -> AudioDriverInfo:
        """Get BlackHole driver information."""
        installed = self.check_virtual_audio_driver()
        return AudioDriverInfo(name="BlackHole 2ch", installed=installed)


class MacOSGPUBackend(PlatformGPUBackend):
    """macOS-specific GPU operations using Metal."""

    def detect_gpu(self) -> Optional[GPUInfo]:
        """Detect Apple Silicon GPU."""
        try:
            # Check for Apple Silicon
            result = subprocess.run(
                ["sysctl", "machdep.cpu.brand_string"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0 and "Apple M" in result.stdout:
                # Extract chip name (e.g., "Apple M1", "Apple M2 Pro")
                cpu_brand = result.stdout.split(":")[-1].strip()
                return GPUInfo(
                    backend="metal",
                    name=cpu_brand,
                    supported=True,
                )
        except Exception:
            pass

        return None

    def get_whisper_build_flags(self) -> Dict[str, str]:
        """Get Metal build flags for whisper.cpp."""
        # Check if Metal is available
        gpu_info = self.detect_gpu()
        if gpu_info and gpu_info.backend == "metal":
            return {"WHISPER_METAL": "1"}
        return {}


class HomebrewManager(PlatformPackageManager):
    """Homebrew package manager for macOS."""

    def is_available(self) -> bool:
        """Check if Homebrew is installed."""
        try:
            result = subprocess.run(
                ["which", "brew"], capture_output=True, text=True, timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False

    def get_name(self) -> str:
        """Get package manager name."""
        return "homebrew"

    def install_package(
        self, package_name: str, timeout: int = 300
    ) -> Tuple[bool, str]:
        """Install package via Homebrew."""
        try:
            result = subprocess.run(
                ["brew", "install", package_name],
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
        """Check if package is installed via Homebrew."""
        try:
            result = subprocess.run(
                ["brew", "list", package_name],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.returncode == 0
        except Exception:
            return False


class MacOSBackend(PlatformBackend):
    """Combined macOS platform backend."""

    def _create_audio_backend(self) -> PlatformAudioBackend:
        """Create macOS audio backend."""
        return MacOSAudioBackend()

    def _create_gpu_backend(self) -> PlatformGPUBackend:
        """Create macOS GPU backend."""
        return MacOSGPUBackend()

    def _create_package_manager(self) -> Optional[PlatformPackageManager]:
        """Create Homebrew package manager."""
        return HomebrewManager()

    def get_platform_name(self) -> str:
        """Get platform name."""
        return "macOS"

    def setup_environment(self) -> None:
        """Setup macOS-specific environment variables."""
        # Thread limits for numerical libraries
        os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
        os.environ.setdefault("OMP_NUM_THREADS", "1")
        os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")

        # Accelerate framework optimizations
        os.environ.setdefault("ACCELERATE_LAPACK", "1")
        os.environ.setdefault("ACCELERATE_BLAS_MULTI_THREAD", "0")

        # Fork safety for Objective-C
        os.environ.setdefault("PYTHONWARNINGS", "ignore::RuntimeWarning")
        os.environ.setdefault("OBJC_DISABLE_INITIALIZE_FORK_SAFETY", "YES")
