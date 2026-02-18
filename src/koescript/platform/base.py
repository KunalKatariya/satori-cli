"""Abstract base classes for platform-specific implementations."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass
class GPUInfo:
    """Information about available GPU."""

    backend: str  # "metal", "cuda", "directml", "rocm", or "cpu"
    name: str
    memory_gb: Optional[float] = None
    supported: bool = True


@dataclass
class AudioDriverInfo:
    """Information about virtual audio driver."""

    name: str
    installed: bool
    version: Optional[str] = None


class PlatformAudioBackend(ABC):
    """Abstract base class for platform-specific audio operations."""

    @abstractmethod
    def get_virtual_audio_keywords(self) -> List[str]:
        """Get keywords for detecting virtual audio devices.

        Returns:
            List of lowercase keywords to match against device names
        """
        pass

    @abstractmethod
    def check_virtual_audio_driver(self) -> bool:
        """Check if virtual audio driver is installed.

        Returns:
            True if virtual audio driver is installed
        """
        pass

    @abstractmethod
    def install_virtual_audio_driver(self) -> Tuple[bool, str]:
        """Install virtual audio driver.

        Returns:
            Tuple of (success: bool, message: str)
        """
        pass

    @abstractmethod
    def get_driver_info(self) -> AudioDriverInfo:
        """Get information about the virtual audio driver.

        Returns:
            AudioDriverInfo object with driver details
        """
        pass


class PlatformGPUBackend(ABC):
    """Abstract base class for platform-specific GPU operations."""

    @abstractmethod
    def detect_gpu(self) -> Optional[GPUInfo]:
        """Detect available GPU and backend.

        Returns:
            GPUInfo if GPU available, None if CPU-only
        """
        pass

    @abstractmethod
    def get_whisper_build_flags(self) -> Dict[str, str]:
        """Get environment variables for whisper.cpp build.

        Returns:
            Dictionary of environment variable names and values
        """
        pass


class PlatformPackageManager(ABC):
    """Abstract base class for platform-specific package management."""

    @abstractmethod
    def is_available(self) -> bool:
        """Check if package manager is available.

        Returns:
            True if package manager is installed and usable
        """
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Get the name of the package manager.

        Returns:
            Package manager name (e.g., "homebrew", "apt", "chocolatey")
        """
        pass

    @abstractmethod
    def install_package(
        self, package_name: str, timeout: int = 300
    ) -> Tuple[bool, str]:
        """Install a package using the package manager.

        Args:
            package_name: Name of package to install
            timeout: Timeout in seconds (default: 300)

        Returns:
            Tuple of (success: bool, message: str)
        """
        pass

    @abstractmethod
    def check_package_installed(self, package_name: str) -> bool:
        """Check if a package is installed.

        Args:
            package_name: Name of package to check

        Returns:
            True if package is installed
        """
        pass


class PlatformBackend(ABC):
    """Combined platform backend with all platform-specific operations."""

    def __init__(self) -> None:
        """Initialize platform backend."""
        self.audio: PlatformAudioBackend = self._create_audio_backend()
        self.gpu: PlatformGPUBackend = self._create_gpu_backend()
        self.package_manager: Optional[PlatformPackageManager] = (
            self._create_package_manager()
        )

    @abstractmethod
    def _create_audio_backend(self) -> PlatformAudioBackend:
        """Create platform-specific audio backend."""
        pass

    @abstractmethod
    def _create_gpu_backend(self) -> PlatformGPUBackend:
        """Create platform-specific GPU backend."""
        pass

    @abstractmethod
    def _create_package_manager(self) -> Optional[PlatformPackageManager]:
        """Create platform-specific package manager."""
        pass

    @abstractmethod
    def get_platform_name(self) -> str:
        """Get platform name.

        Returns:
            Platform name (e.g., "macOS", "Windows", "Linux")
        """
        pass

    @abstractmethod
    def setup_environment(self) -> None:
        """Setup platform-specific environment variables and settings."""
        pass
