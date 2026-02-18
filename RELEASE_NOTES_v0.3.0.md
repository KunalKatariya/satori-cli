# Koescript v0.3.0 Release Notes

**Release Date:** February 19, 2025

## 🎉 Major Release: Cross-Platform Support

This is a major release featuring **full cross-platform support** for Windows, Linux, and macOS. Koescript now runs seamlessly on all three major operating systems with platform-specific optimizations and GPU acceleration.

## ✨ What's New

### Cross-Platform Support
- **Windows support** with WASAPI audio backend and VB-Cable integration
- **Linux support** with PulseAudio loopback and GPU acceleration via CUDA
- **Unified codebase** with platform abstraction layer for maximum compatibility

### Platform-Specific Features

#### macOS (Existing + Enhanced)
- ✅ **Metal GPU acceleration** for Apple Silicon (M1/M2/M3/M4)
- ✅ **BlackHole audio driver** auto-installation via Homebrew
- ✅ **SoundCard audio backend** for reliable capture
- ✅ Performance: 30-50x real-time transcription with Metal

#### Windows (NEW)
- 🎉 **WASAPI audio backend** for low-latency Windows audio capture
- 🎉 **VB-Cable auto-installation** via Chocolatey (or manual setup)
- 🎉 **CUDA GPU acceleration** for NVIDIA GPUs (10-20x real-time)
- 🎉 **Per-app audio routing** via Windows Sound Settings
- 🎉 CPU fallback for systems without NVIDIA GPUs (~2-5x real-time)

#### Linux (NEW)
- 🎉 **PulseAudio loopback module** for system audio capture (built-in, auto-configured)
- 🎉 **PipeWire compatibility** for modern distributions (Fedora 34+, Ubuntu 22.10+)
- 🎉 **CUDA GPU acceleration** for NVIDIA GPUs (10-20x real-time)
- 🎉 **Multiple package managers** supported: apt, yum/dnf, pacman
- 🎉 CPU fallback for systems without NVIDIA GPUs (~2-5x real-time)

### Architecture Improvements

#### Platform Abstraction Layer
- **New module**: `src/koescript/platform/` with factory pattern
- **Platform detection**: Automatic detection and configuration per OS
- **Extensible design**: Easy to add future platform support (FreeBSD, ARM Linux, etc.)

```
src/koescript/platform/
├── __init__.py          # Platform factory with caching
├── base.py              # Abstract base classes
├── macos.py             # macOS implementation (BlackHole, Metal, Homebrew)
├── windows.py           # Windows implementation (VB-Cable, CUDA, Chocolatey/Scoop)
└── linux.py             # Linux implementation (PulseAudio, CUDA, apt/yum/pacman)
```

#### Audio Backend Abstraction
- **New module**: `src/koescript/audio/backends/` with dual-backend system
- **SoundCard backend**: macOS and Linux (preferred)
- **WASAPI backend**: Windows with PyAudio for loopback support
- **Automatic selection**: Best backend chosen per platform with fallback

```
src/koescript/audio/backends/
├── __init__.py          # Backend factory
├── base.py              # Abstract audio backend interface
├── soundcard_backend.py # macOS/Linux backend
└── wasapi_backend.py    # Windows WASAPI backend
```

#### GPU Acceleration Matrix

| Platform | GPU Type | Backend | Installation |
|----------|----------|---------|--------------|
| macOS | Apple Silicon | Metal | Auto (built into macOS) |
| macOS | Intel | Metal (limited) | Auto (may not accelerate) |
| Windows | NVIDIA | CUDA | Auto-detected, CUDA Toolkit required |
| Windows | AMD/Intel | CPU fallback | Future: DirectML (v1.1) |
| Linux | NVIDIA | CUDA | Auto-detected, CUDA Toolkit required |
| Linux | AMD | CPU fallback | Future: ROCm (v1.1) |

### Virtual Audio Drivers

| Platform | Driver | Installation | Configuration |
|----------|--------|--------------|---------------|
| **macOS** | BlackHole 2ch | Auto via Homebrew | Multi-Output Device (Audio MIDI Setup) |
| **Windows** | VB-Cable | Semi-auto via Chocolatey or manual | Per-app routing (Sound Settings) |
| **Linux** | PulseAudio loopback | Auto via pactl | Auto-configured by Koescript |

### Updated Commands

All existing commands now work across all platforms:

```bash
# Initialize (auto-detects platform and installs dependencies)
koescript init

# List audio devices (shows platform-specific devices)
koescript devices

# Transcribe with loopback (uses platform-specific virtual audio)
koescript translate --loopback

# Translate with GPU acceleration (auto-detects Metal/CUDA/CPU)
koescript translate --loopback --language ja --translate-to en --model medium
```

## 📦 Installation

### macOS

**Via Homebrew (Recommended):**
```bash
brew tap KunalKatariya/koescript
brew install koescript
```

**Via pip:**
```bash
pip install koescript
```

### Windows

**Via pip (Recommended):**
```bash
pip install koescript
```

**From source:**
```bash
git clone https://github.com/KunalKatariya/koescript.git
cd koescript
pip install .
```

### Linux

**Via pip (Recommended):**
```bash
pip install koescript
```

**From source:**
```bash
git clone https://github.com/KunalKatariya/koescript.git
cd koescript
pip install .
```

## 🚀 Quick Start

### All Platforms

1. **First-time setup:**
   ```bash
   koescript init
   ```
   This will:
   - Auto-install virtual audio driver (with your consent)
   - Auto-build whisper.cpp with GPU support (if available)
   - Download initial Whisper model
   - Verify audio device availability

2. **Configure virtual audio:**
   - **macOS**: Create Multi-Output Device in Audio MIDI Setup
   - **Windows**: Route apps to VB-Cable in Sound Settings
   - **Linux**: Auto-configured by Koescript (PulseAudio loopback)

3. **Start transcribing:**
   ```bash
   # Basic microphone transcription
   koescript translate

   # System audio transcription with translation
   koescript translate --loopback --language ja --translate-to en
   ```

See platform-specific setup guides in [README.md](README.md) and [PLATFORM_SUPPORT.md](PLATFORM_SUPPORT.md).

## 🔄 Breaking Changes

### None for Existing macOS Users
- All existing macOS functionality preserved
- Config directory remains at `~/.koescript/`
- Commands unchanged
- BlackHole setup process unchanged

### For New Users
- Platform-specific setup required (virtual audio drivers)
- GPU acceleration requires CUDA Toolkit on Windows/Linux (NVIDIA GPUs only in v0.3.0)

## 📝 Full Changelog

### New Files Created (9)
- `src/koescript/platform/__init__.py` - Platform factory
- `src/koescript/platform/base.py` - Abstract platform interfaces
- `src/koescript/platform/macos.py` - macOS implementation
- `src/koescript/platform/windows.py` - Windows implementation
- `src/koescript/platform/linux.py` - Linux implementation
- `src/koescript/audio/backends/__init__.py` - Backend factory
- `src/koescript/audio/backends/base.py` - Abstract audio backend
- `src/koescript/audio/backends/soundcard_backend.py` - SoundCard backend
- `src/koescript/audio/backends/wasapi_backend.py` - Windows WASAPI backend

### Modified Files (6)
- `src/koescript/cli.py` - Platform-aware initialization and device detection
- `src/koescript/audio/capture.py` - Backend abstraction integration
- `src/koescript/audio/__init__.py` - Updated imports for AudioDevice
- `src/koescript/setup/dependencies.py` - Platform-aware driver installation
- `src/koescript/ai/whisper_cpp.py` - Cross-platform binary detection (.exe paths)
- `pyproject.toml` - Version bump to 0.3.0, added platform classifiers

### Documentation Updates (3)
- `README.md` - Complete rewrite with cross-platform installation and setup
- `PLATFORM_SUPPORT.md` - **NEW** comprehensive platform compatibility matrix
- `TROUBLESHOOTING.md` - Complete overhaul with platform-specific sections

### Commits
- (To be added with actual commit hashes after release)

## 🔧 System Requirements

### Minimum Requirements (All Platforms)
- **Python:** 3.11+
- **RAM:** 8GB (16GB recommended for large models)
- **Storage:** 5GB free space (for models and dependencies)

### Platform-Specific Requirements

#### macOS
- **OS:** macOS 11 (Big Sur) or later (macOS 13+ recommended)
- **CPU:** Intel x86_64 or Apple Silicon (M1/M2/M3/M4)
- **GPU:** Metal-capable GPU (all Apple Silicon, most modern Intel Macs)
- **Audio:** BlackHole 2ch (auto-installable via Homebrew)

#### Windows
- **OS:** Windows 10 (1809+) or Windows 11
- **CPU:** x86_64 processor (Intel or AMD)
- **GPU:** NVIDIA GPU with CUDA support (optional, recommended)
- **Audio:** VB-Cable (auto-installable via Chocolatey or manual)
- **Build Tools:** MinGW or Visual Studio Build Tools (for whisper.cpp compilation)

#### Linux
- **OS:** Ubuntu 20.04+, Debian 11+, Fedora 35+, Arch Linux (latest)
- **CPU:** x86_64 processor (Intel or AMD)
- **GPU:** NVIDIA GPU with CUDA support (optional, recommended)
- **Audio:** PulseAudio or PipeWire (usually pre-installed)
- **Build Tools:** build-essential, git, cmake

## 📊 Performance

### GPU-Accelerated Performance

| Model | macOS (Metal) | Windows/Linux (CUDA) | CPU Only (All Platforms) |
|-------|---------------|----------------------|--------------------------|
| tiny | 50x real-time | 25x real-time | 10x real-time |
| base | 30x real-time | 18x real-time | 5x real-time |
| small | 20x real-time | 12x real-time | 3x real-time |
| medium | 10x real-time | 8x real-time | 2x real-time |
| large | 10x real-time | 7x real-time | 1-1.5x real-time |

**Note:** Performance varies based on specific GPU model and system load. CPU fallback is fully functional on all platforms.

## 🐛 Known Issues

### Windows
- VB-Cable requires system restart after first installation
- Build-from-source requires 7GB+ Visual Studio Build Tools (pre-built binaries coming in v1.0)
- DirectML support for AMD/Intel GPUs coming in v1.1

### Linux
- PipeWire users need PulseAudio compatibility layer (usually installed by default)
- ALSA-only systems require manual PulseAudio installation
- ROCm support for AMD GPUs coming in v1.1

### General
- Large models (medium, large) require significant RAM (2-3.5GB)
- Translation adds +3GB RAM for NLLB model
- First translation is slower due to NLLB model download (~1.3GB)

## 📚 Documentation

Comprehensive documentation has been added or updated:

1. **[README.md](README.md)** - Complete rewrite with:
   - Cross-platform installation instructions
   - Virtual audio setup for all platforms
   - Platform-specific examples and use cases
   - Updated prerequisites and features

2. **[PLATFORM_SUPPORT.md](PLATFORM_SUPPORT.md)** - **NEW** comprehensive guide featuring:
   - Platform compatibility matrix
   - Hardware requirements per platform
   - GPU acceleration details
   - Virtual audio driver comparison
   - Performance benchmarks
   - Platform-specific installation notes
   - Roadmap for future features

3. **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Complete overhaul with:
   - Cross-platform troubleshooting sections
   - macOS: BlackHole issues, Metal GPU problems
   - Windows: VB-Cable setup, CUDA installation, build tools
   - Linux: PulseAudio/PipeWire configs, CUDA setup, package managers
   - Performance troubleshooting per platform
   - Debug logging for all platforms

4. **[USAGE.md](USAGE.md)** - Existing comprehensive command reference (unchanged)

5. **[WHISPER_SETUP.md](WHISPER_SETUP.md)** - Existing whisper.cpp installation guide (unchanged)

6. **[CONTRIBUTING.md](CONTRIBUTING.md)** - Existing development guidelines (unchanged)

## 🛣️ Roadmap

### v1.0.0 (Next Release - Planned)
- 🔄 DirectML support for Windows (AMD/Intel GPUs)
- 🔄 ROCm support for Linux (AMD GPUs)
- 🔄 Pre-built Windows binaries (eliminate 7GB build tools requirement)
- 🔄 Enhanced GPU detection and fallback
- 🔄 CI/CD pipeline for all platforms

### v1.1.0 (Future)
- 📋 ASIO support for Windows (professional audio)
- 📋 Jack support for Linux (professional audio)
- 📋 Multi-channel audio support
- 📋 Hardware acceleration on Intel integrated GPUs
- 📋 ARM64 Linux support (Raspberry Pi, etc.)

## 💡 Migration Guide

### For Existing macOS Users
**No migration needed!** Everything works exactly as before. You can simply upgrade:

```bash
# Via Homebrew
brew upgrade koescript

# Via pip
pip install --upgrade koescript
```

All your existing config, models, and BlackHole setup remain unchanged.

### For New Windows/Linux Users
Follow the platform-specific installation guide in [README.md](README.md):

1. Install Python 3.11+
2. Install Koescript via pip
3. Run `koescript init` to auto-install dependencies
4. Configure virtual audio for system capture (optional)

## 🙏 Credits

Built with:
- **[whisper.cpp](https://github.com/ggerganov/whisper.cpp)** - Fast Whisper implementation with GPU support
- **[Meta NLLB-200](https://ai.meta.com/research/no-language-left-behind/)** - Multilingual translation model
- **[Textual](https://textual.textualize.io/)** - Modern TUI framework
- **[BlackHole](https://existential.audio/blackhole/)** - Virtual audio driver for macOS
- **[VB-Cable](https://vb-audio.com/Cable/)** - Virtual audio driver for Windows
- **[PulseAudio](https://www.freedesktop.org/wiki/Software/PulseAudio/)** - Sound system for Linux

Special thanks to the open-source community for these amazing tools!

## 📞 Getting Help

- **Issues**: [GitHub Issues](https://github.com/KunalKatariya/koescript/issues)
- **Documentation**: See [README.md](README.md), [PLATFORM_SUPPORT.md](PLATFORM_SUPPORT.md), and [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Platform Support Matrix**: [PLATFORM_SUPPORT.md](PLATFORM_SUPPORT.md)

---

**Note:** This is a major feature release focused on expanding platform support. Report any platform-specific issues on GitHub. Windows and Linux support is actively maintained alongside macOS.
