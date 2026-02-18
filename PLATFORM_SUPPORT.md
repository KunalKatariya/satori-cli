# Platform Support

Koescript v0.3.0+ provides cross-platform support for macOS, Windows, and Linux with platform-specific optimizations and features.

## Platform Compatibility Matrix

| Feature | macOS | Windows | Linux | Notes |
|---------|-------|---------|-------|-------|
| **Audio Capture** | ✅ Full | ✅ Full | ✅ Full | All platforms supported |
| **Loopback Audio** | ✅ BlackHole | ✅ VB-Cable | ✅ PulseAudio | Virtual audio drivers |
| **GPU Acceleration** | ✅ Metal | ⚠️ CUDA only | ⚠️ CUDA only | DirectML/ROCm planned for v1.1 |
| **Auto-Install Drivers** | ✅ Homebrew | ⚠️ Semi-auto | ✅ Built-in | Windows requires Chocolatey |
| **Package Manager** | ✅ Homebrew | ⚠️ Choco/Scoop | ✅ apt/yum/pacman | Multiple options |
| **Real-time Translation** | ✅ Full | ✅ Full | ✅ Full | All platforms supported |
| **Whisper Models** | ✅ All | ✅ All | ✅ All | tiny to large |
| **TUI Interface** | ✅ Full | ✅ Full | ✅ Full | Textual framework |

**Legend:**
- ✅ Full support with all features
- ⚠️ Partial support or limitations
- ❌ Not supported

## macOS

### Supported Versions
- **macOS 11 (Big Sur)** and later
- **Recommended**: macOS 13 (Ventura) or later for best performance

### Hardware Requirements
- **CPU**: Intel x86_64 or Apple Silicon (M1/M2/M3/M4)
- **RAM**: 8GB minimum, 16GB recommended for large models
- **Storage**: 5GB free space (for models and dependencies)
- **GPU**: Metal-capable GPU (all Apple Silicon, most modern Intel Macs)

### Audio Backend
- **Library**: SoundCard
- **Virtual Audio**: BlackHole 2ch
- **Installation**: Automatic via Homebrew (`brew install blackhole-2ch`)
- **Configuration**: Multi-Output Device via Audio MIDI Setup

### GPU Acceleration
- **Backend**: Metal Performance Shaders (MPS)
- **Build Flag**: `WHISPER_METAL=1`
- **Performance**: 30-50x real-time on Apple Silicon
- **Requirements**: macOS 12.3+ for optimal Metal support

### Known Limitations
- Multi-Output Device setup requires manual configuration
- Some older Intel Macs may have limited Metal support
- Rosetta 2 performance lower on Apple Silicon (use native build)

## Windows

### Supported Versions
- **Windows 10** (version 1809 or later)
- **Windows 11**
- **Recommended**: Windows 11 for best compatibility

### Hardware Requirements
- **CPU**: x86_64 processor (Intel or AMD)
- **RAM**: 8GB minimum, 16GB recommended for large models
- **Storage**: 5GB free space (for models and dependencies)
- **GPU**: NVIDIA GPU with CUDA support (optional, for acceleration)

### Audio Backend
- **Library**: PyAudio with WASAPI
- **Virtual Audio**: VB-Cable Virtual Audio Device
- **Installation**: Semi-automatic via Chocolatey or manual download
- **Configuration**: Windows Sound Settings + App volume preferences

### GPU Acceleration
- **Backend**: CUDA (NVIDIA GPUs only)
- **Build Flag**: `WHISPER_CUDA=1`
- **Performance**: 10-20x real-time with CUDA
- **Requirements**: CUDA Toolkit 11.x or 12.x, NVIDIA driver 470+
- **Fallback**: CPU-only (works on all systems, ~1-5x real-time)

### Known Limitations
- VB-Cable installation requires administrator privileges
- Reboot required after VB-Cable installation
- DirectML support (AMD/Intel GPUs) coming in v1.1
- Build-from-source requires Visual Studio Build Tools (7GB+)

### Audio Routing
Windows requires per-application audio routing to VB-Cable:
1. Right-click Speaker icon → Sound Settings
2. Advanced sound options → App volume and device preferences
3. Set application output to "CABLE Input (VB-Audio Virtual Cable)"

## Linux

### Supported Distributions
- **Ubuntu** 20.04 LTS and later
- **Debian** 11 (Bullseye) and later
- **Fedora** 35 and later
- **Arch Linux** (latest)
- **Pop!_OS** 20.04 and later

### Package Manager Support
- **apt** (Debian, Ubuntu, Pop!_OS, Mint)
- **yum/dnf** (Fedora, CentOS, RHEL)
- **pacman** (Arch Linux, Manjaro)

### Hardware Requirements
- **CPU**: x86_64 processor (Intel or AMD)
- **RAM**: 8GB minimum, 16GB recommended for large models
- **Storage**: 5GB free space (for models and dependencies)
- **GPU**: NVIDIA GPU with CUDA support (optional, for acceleration)

### Audio Backend
- **Library**: SoundCard (primary), PyAudio (fallback)
- **Virtual Audio**: PulseAudio loopback module (built-in)
- **Installation**: Automatic (loads `module-loopback` on demand)
- **Configuration**: No manual configuration required

### GPU Acceleration
- **Backend**: CUDA (NVIDIA GPUs only)
- **Build Flag**: `WHISPER_CUDA=1`
- **Performance**: 10-20x real-time with CUDA
- **Requirements**: CUDA Toolkit 11.x or 12.x, NVIDIA driver 470+
- **Fallback**: CPU-only (works on all systems, ~1-5x real-time)

### Known Limitations
- PipeWire users: May need PulseAudio compatibility layer
- ALSA-only systems: Requires PulseAudio installation
- ROCm support (AMD GPUs) coming in v1.1
- Some distributions may require manual build-essential packages

### Audio Configuration
PulseAudio loopback is loaded automatically by Koescript. Manual control:
```bash
# Load loopback module
pactl load-module module-loopback latency_msec=1

# Unload loopback module
pactl unload-module module-loopback

# List active modules
pactl list modules | grep loopback
```

## Performance Comparison

### GPU Acceleration Performance

| Platform | GPU Type | Backend | medium Model | large Model |
|----------|----------|---------|--------------|-------------|
| macOS (M1) | Apple Silicon | Metal | 35x real-time | 30x real-time |
| macOS (M2/M3) | Apple Silicon | Metal | 45x real-time | 40x real-time |
| Windows | NVIDIA RTX 3060 | CUDA | 18x real-time | 15x real-time |
| Windows | NVIDIA RTX 4090 | CUDA | 25x real-time | 22x real-time |
| Linux | NVIDIA RTX 3070 | CUDA | 20x real-time | 17x real-time |
| All | CPU (Intel i7) | CPU | 3x real-time | 2x real-time |
| All | CPU (AMD Ryzen 7) | CPU | 4x real-time | 2.5x real-time |

**Notes:**
- Performance varies based on CPU/GPU model and system load
- Real-time speeds measured with 16kHz audio input
- GPU acceleration highly recommended for `medium` and `large` models
- CPU-only is sufficient for `tiny`, `base`, and `small` models

### Memory Usage

| Model | Disk Size | RAM Usage (CPU) | VRAM Usage (GPU) |
|-------|-----------|-----------------|------------------|
| tiny | 75 MB | ~400 MB | ~200 MB |
| base | 142 MB | ~500 MB | ~300 MB |
| small | 466 MB | ~1.2 GB | ~800 MB |
| medium | 1.5 GB | ~2.5 GB | ~1.8 GB |
| large | 1.5 GB | ~3.5 GB | ~2.5 GB |

## Virtual Audio Driver Details

### macOS: BlackHole

**Installation:**
```bash
brew install blackhole-2ch
```

**Configuration:**
- Uses Multi-Output Device in Audio MIDI Setup
- Combines speakers + BlackHole for simultaneous output
- System-wide audio routing

**Advantages:**
- Free and open source
- Stable and well-maintained
- Low latency
- Works with all audio applications

**Disadvantages:**
- Requires manual Multi-Output Device setup
- Cannot route individual applications

### Windows: VB-Cable

**Installation:**
```bash
# Automatic (with Chocolatey)
choco install vb-cable

# Manual (requires reboot)
# Download from https://vb-audio.com/Cable/
# Run VBCABLE_Setup_x64.exe as Administrator
```

**Configuration:**
- Per-application audio routing via Sound Settings
- System default remains unchanged
- Flexible routing options

**Advantages:**
- Free for non-commercial use
- Per-application routing
- No system-wide audio changes
- Widely compatible

**Disadvantages:**
- Requires administrator privileges
- Reboot required after installation
- Manual per-app configuration
- Commercial use requires license

### Linux: PulseAudio

**Installation:**
- Built-in on most distributions
- Loaded automatically by Koescript

**Configuration:**
```bash
# Auto-loaded by Koescript
koescript translate --loopback

# Manual control (optional)
pactl load-module module-loopback latency_msec=1
pactl unload-module module-loopback
```

**Advantages:**
- No installation required
- No manual configuration
- System-wide audio capture
- Free and open source

**Disadvantages:**
- PipeWire users need compatibility layer
- ALSA-only systems require PulseAudio installation
- Higher latency than hardware loopback (usually acceptable)

## Platform-Specific Installation Notes

### macOS

1. **Python 3.11+ Installation:**
   ```bash
   brew install python@3.11
   ```

2. **Koescript Installation:**
   ```bash
   # Via Homebrew (recommended)
   brew tap KunalKatariya/koescript
   brew install koescript

   # Via pip
   pip install koescript
   ```

3. **First-time Setup:**
   ```bash
   koescript init  # Auto-installs BlackHole and builds whisper.cpp
   ```

### Windows

1. **Python 3.11+ Installation:**
   - Download from [python.org](https://www.python.org/downloads/)
   - Or via Chocolatey: `choco install python311`

2. **Koescript Installation:**
   ```bash
   # Via pip (recommended)
   pip install koescript

   # From source
   git clone https://github.com/KunalKatariya/koescript.git
   cd koescript
   pip install .
   ```

3. **First-time Setup:**
   ```bash
   koescript init  # Auto-installs VB-Cable and builds whisper.cpp
   ```

4. **CUDA Setup (Optional, for GPU acceleration):**
   - Install NVIDIA drivers from [nvidia.com](https://www.nvidia.com/drivers)
   - Install CUDA Toolkit 11.x or 12.x
   - Restart system

### Linux

1. **Python 3.11+ Installation:**
   ```bash
   # Ubuntu/Debian
   sudo apt install python3.11 python3.11-venv python3-pip

   # Fedora
   sudo dnf install python3.11

   # Arch Linux
   sudo pacman -S python
   ```

2. **Koescript Installation:**
   ```bash
   # Via pip (recommended)
   pip install koescript

   # From source
   git clone https://github.com/KunalKatariya/koescript.git
   cd koescript
   pip install .
   ```

3. **PulseAudio Setup:**
   ```bash
   # Usually pre-installed, if not:
   sudo apt install pulseaudio  # Ubuntu/Debian
   sudo dnf install pulseaudio  # Fedora
   sudo pacman -S pulseaudio    # Arch Linux
   ```

4. **First-time Setup:**
   ```bash
   koescript init  # Auto-configures PulseAudio and builds whisper.cpp
   ```

5. **CUDA Setup (Optional, for GPU acceleration):**
   ```bash
   # Ubuntu/Debian
   # Follow NVIDIA's official guide: https://developer.nvidia.com/cuda-downloads

   # Fedora (RPM Fusion)
   sudo dnf install cuda

   # Arch Linux (AUR)
   yay -S cuda
   ```

## Troubleshooting by Platform

### macOS

**Issue: BlackHole not detected**
- Verify installation: `brew list blackhole-2ch`
- Check Audio MIDI Setup for Multi-Output Device
- Ensure BlackHole is checked in Multi-Output Device

**Issue: No audio output**
- Verify speakers are Master Device in Audio MIDI Setup
- Check System Settings → Sound → Output

**Issue: Metal acceleration not working**
- Update to macOS 12.3+ for best Metal support
- Verify with: `system_profiler SPDisplaysDataType | grep Metal`

### Windows

**Issue: VB-Cable not detected**
- Restart computer after installation
- Verify in Device Manager → Sound, video and game controllers
- Check: `koescript devices`

**Issue: No audio from applications**
- Route app audio to VB-Cable in Sound Settings
- Check Sound Settings → App volume and device preferences

**Issue: CUDA not working**
- Install CUDA Toolkit from NVIDIA
- Verify with: `nvidia-smi`
- Ensure environment variable CUDA_PATH is set

### Linux

**Issue: PulseAudio module not loading**
- Check PulseAudio is running: `pulseaudio --check`
- Start manually: `pulseaudio --start`
- Verify: `pactl list modules | grep loopback`

**Issue: Permission errors**
- Add user to audio group: `sudo usermod -a -G audio $USER`
- Log out and back in

**Issue: CUDA not working**
- Verify NVIDIA driver: `nvidia-smi`
- Check CUDA installation: `nvcc --version`
- Ensure LD_LIBRARY_PATH includes CUDA libraries

## Roadmap

### v0.3.0 (Current)
- ✅ macOS support with Metal GPU acceleration
- ✅ Windows support with CUDA GPU acceleration
- ✅ Linux support with CUDA GPU acceleration
- ✅ Cross-platform audio backends
- ✅ Auto-install virtual audio drivers

### v1.0.0 (Next)
- 🔄 DirectML support for Windows (AMD/Intel GPUs)
- 🔄 ROCm support for Linux (AMD GPUs)
- 🔄 Pre-built Windows binaries
- 🔄 Improved Windows build-from-source experience
- 🔄 Enhanced GPU detection and fallback

### v1.1.0 (Future)
- 📋 ASIO support for Windows (professional audio)
- 📋 Jack support for Linux (professional audio)
- 📋 Multi-channel audio support
- 📋 Hardware acceleration on Intel integrated GPUs
- 📋 ARM64 Linux support (Raspberry Pi, etc.)

## Support

For platform-specific issues, see:
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Detailed troubleshooting guide
- **[GitHub Issues](https://github.com/KunalKatariya/koescript/issues)** - Report bugs or request features
- **[README.md](README.md)** - Quick start and installation guide
