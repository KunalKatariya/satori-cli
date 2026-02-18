"""Platform abstraction layer for cross-platform support."""

import platform as platform_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from koescript.platform.base import PlatformBackend

# Cached platform backend instance
_platform_backend: "PlatformBackend | None" = None


def get_platform_backend() -> "PlatformBackend":
    """Get the appropriate platform backend for the current system.

    Returns:
        Platform-specific backend instance

    Raises:
        RuntimeError: If platform is not supported
    """
    global _platform_backend

    # Return cached instance if available
    if _platform_backend is not None:
        return _platform_backend

    system = platform_module.system()

    if system == "Darwin":
        from koescript.platform.macos import MacOSBackend

        _platform_backend = MacOSBackend()
    elif system == "Linux":
        from koescript.platform.linux import LinuxBackend

        _platform_backend = LinuxBackend()
    elif system == "Windows":
        from koescript.platform.windows import WindowsBackend

        _platform_backend = WindowsBackend()
    else:
        raise RuntimeError(
            f"Unsupported platform: {system}. "
            "Koescript currently supports macOS, Linux, and Windows."
        )

    return _platform_backend


def get_platform_name() -> str:
    """Get the current platform name.

    Returns:
        Platform name: "macOS", "Linux", or "Windows"
    """
    system = platform_module.system()
    if system == "Darwin":
        return "macOS"
    elif system == "Linux":
        return "Linux"
    elif system == "Windows":
        return "Windows"
    else:
        return system


__all__ = [
    "get_platform_backend",
    "get_platform_name",
    "PlatformBackend",
    "PlatformAudioBackend",
    "PlatformGPUBackend",
    "PlatformPackageManager",
    "GPUInfo",
    "AudioDriverInfo",
]
