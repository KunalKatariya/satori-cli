"""Linux platform-specific implementations."""

import os
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from koescript.platform.base import (
    AudioDriverInfo,
    GPUInfo,
    PlatformAudioBackend,
    PlatformBackend,
    PlatformGPUBackend,
    PlatformPackageManager,
)


class LinuxAudioBackend(PlatformAudioBackend):
    """Linux-specific audio operations using PulseAudio."""

    def get_virtual_audio_keywords(self) -> List[str]:
        """Get keywords for detecting virtual audio devices on Linux."""
        return ["pulse", "monitor", "loopback", "null", "sink"]

    def check_virtual_audio_driver(self) -> bool:
        """Check if PulseAudio loopback module is loaded."""
        try:
            result = subprocess.run(
                ["pactl", "list", "modules"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return "module-loopback" in result.stdout
        except FileNotFoundError:
            # PulseAudio not installed
            return False
        except Exception:
            return False

    def install_virtual_audio_driver(self) -> Tuple[bool, str]:
        """Load PulseAudio loopback module."""
        try:
            # Load loopback module with 1ms latency
            result = subprocess.run(
                ["pactl", "load-module", "module-loopback", "latency_msec=1"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                return (
                    True,
                    "PulseAudio loopback module loaded successfully",
                )
            else:
                return (
                    False,
                    f"Failed to load loopback module: {result.stderr[:200]}",
                )

        except FileNotFoundError:
            return (
                False,
                "PulseAudio not found. Install via: sudo apt install pulseaudio",
            )
        except Exception as e:
            return (False, f"Error loading loopback module: {str(e)}")

    def get_driver_info(self) -> AudioDriverInfo:
        """Get PulseAudio loopback information."""
        installed = self.check_virtual_audio_driver()
        return AudioDriverInfo(name="PulseAudio Loopback", installed=installed)


class LinuxGPUBackend(PlatformGPUBackend):
    """Linux-specific GPU operations."""

    def detect_gpu(self) -> Optional[GPUInfo]:
        """Detect NVIDIA GPU on Linux."""
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

        # Check for AMD GPU (ROCm support coming in v1.1)
        if Path("/dev/dri/renderD128").exists():
            try:
                result = subprocess.run(
                    ["lspci"], capture_output=True, text=True, timeout=5
                )
                for line in result.stdout.split("\n"):
                    if "VGA" in line and ("AMD" in line or "ATI" in line):
                        return GPUInfo(
                            backend="rocm",
                            name="AMD GPU",
                            supported=False,  # ROCm support coming in v1.1
                        )
            except Exception:
                pass

        return None

    def get_whisper_build_flags(self) -> Dict[str, str]:
        """Get CUDA build flags for whisper.cpp."""
        gpu_info = self.detect_gpu()
        if gpu_info and gpu_info.backend == "cuda":
            return {"WHISPER_CUDA": "1"}
        # ROCm support coming in v1.1
        # elif gpu_info and gpu_info.backend == "rocm":
        #     return {"WHISPER_HIPBLAS": "1"}
        return {}


class AptManager(PlatformPackageManager):
    """APT package manager for Debian/Ubuntu."""

    def is_available(self) -> bool:
        """Check if apt is available."""
        try:
            result = subprocess.run(
                ["which", "apt"], capture_output=True, text=True, timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False

    def get_name(self) -> str:
        """Get package manager name."""
        return "apt"

    def install_package(
        self, package_name: str, timeout: int = 300
    ) -> Tuple[bool, str]:
        """Install package via apt."""
        try:
            # apt requires sudo
            result = subprocess.run(
                ["sudo", "apt", "install", "-y", package_name],
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
        """Check if package is installed via apt."""
        try:
            result = subprocess.run(
                ["dpkg", "-l", package_name],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.returncode == 0
        except Exception:
            return False


class YumManager(PlatformPackageManager):
    """YUM package manager for RHEL/CentOS."""

    def is_available(self) -> bool:
        """Check if yum is available."""
        try:
            result = subprocess.run(
                ["which", "yum"], capture_output=True, text=True, timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False

    def get_name(self) -> str:
        """Get package manager name."""
        return "yum"

    def install_package(
        self, package_name: str, timeout: int = 300
    ) -> Tuple[bool, str]:
        """Install package via yum."""
        try:
            result = subprocess.run(
                ["sudo", "yum", "install", "-y", package_name],
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
        """Check if package is installed via yum."""
        try:
            result = subprocess.run(
                ["rpm", "-q", package_name],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.returncode == 0
        except Exception:
            return False


class LinuxBackend(PlatformBackend):
    """Combined Linux platform backend."""

    def _create_audio_backend(self) -> PlatformAudioBackend:
        """Create Linux audio backend."""
        return LinuxAudioBackend()

    def _create_gpu_backend(self) -> PlatformGPUBackend:
        """Create Linux GPU backend."""
        return LinuxGPUBackend()

    def _create_package_manager(self) -> Optional[PlatformPackageManager]:
        """Create package manager (apt, yum, etc.)."""
        # Try apt first (Debian/Ubuntu)
        apt = AptManager()
        if apt.is_available():
            return apt

        # Try yum (RHEL/CentOS)
        yum = YumManager()
        if yum.is_available():
            return yum

        # No supported package manager
        return None

    def get_platform_name(self) -> str:
        """Get platform name."""
        return "Linux"

    def setup_environment(self) -> None:
        """Setup Linux-specific environment variables."""
        # Thread limits for numerical libraries
        os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
        os.environ.setdefault("OMP_NUM_THREADS", "1")

        # MKL settings for Intel CPUs (if available)
        os.environ.setdefault("MKL_NUM_THREADS", "1")
