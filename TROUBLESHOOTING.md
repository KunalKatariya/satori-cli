# Troubleshooting Guide

Solutions to common issues with Koescript across macOS, Windows, and Linux.

## Table of Contents

- [Installation Issues](#installation-issues)
- [Audio Issues](#audio-issues)
  - [macOS: BlackHole Issues](#macos-blackhole-issues)
  - [Windows: VB-Cable Issues](#windows-vb-cable-issues)
  - [Linux: PulseAudio Issues](#linux-pulseaudio-issues)
- [Transcription Issues](#transcription-issues)
- [Translation Issues](#translation-issues)
- [Performance Issues](#performance-issues)
- [Model Issues](#model-issues)
- [Platform-Specific Issues](#platform-specific-issues)
  - [macOS Issues](#macos-issues)
  - [Windows Issues](#windows-issues)
  - [Linux Issues](#linux-issues)

## Installation Issues

### Command Not Found: koescript

**If you installed from PyPI:**

```bash
# Check if installed
pip list | grep koescript

# Reinstall
pip install --upgrade koescript

# Check Python bin directory is in PATH
echo $PATH | grep -o "[^:]*python[^:]*"
```

**If you installed from source:**

```bash
# Option 1: Install in editable mode
cd /path/to/koescript
pip install -e .

# Option 2: Use Poetry shell
poetry shell
koescript --help

# Option 3: Use poetry run prefix
poetry run koescript --help
```

**macOS specific:**

```bash
# Ensure pip install location is in PATH
export PATH="$HOME/.local/bin:$PATH"
export PATH="$HOME/Library/Python/3.11/bin:$PATH"

# Add to ~/.zshrc to make permanent
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

**Windows specific:**

```powershell
# Check if Python Scripts folder is in PATH
echo $env:PATH

# Add to PATH temporarily
$env:PATH += ";$env:APPDATA\Python\Python311\Scripts"

# Add permanently via System Properties:
# 1. Search "Environment Variables" in Windows
# 2. Edit PATH variable
# 3. Add: C:\Users\<YourUser>\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.11_...\LocalCache\local-packages\Python311\Scripts
```

**Linux specific:**

```bash
# Ensure pip install location is in PATH
export PATH="$HOME/.local/bin:$PATH"

# Add to ~/.bashrc to make permanent
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Poetry Not Found

```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Add to PATH
export PATH="$HOME/.local/bin:$PATH"

# Verify installation
poetry --version
```

### Permission Denied Errors

```bash
# Use user installation (don't use sudo with pip)
pip install --user koescript

# Check file permissions
ls -la ~/.koescript/

# Fix permissions if needed
chmod -R u+w ~/.koescript/
```

## Audio Issues

### General Audio Troubleshooting

#### No Audio Devices Found

```bash
# List all available devices
koescript devices

# Test with specific device index or name
koescript translate --device <device_name>
```

**Check system permissions:**
- **macOS**: System Settings > Privacy & Security > Microphone
- **Windows**: Settings > Privacy > Microphone
- **Linux**: Usually no permission needed, check PulseAudio is running

#### Audio Recording Fails

```bash
# Verify device exists
koescript devices

# Close other apps using audio (Zoom, Discord, OBS, etc.)

# Test from Python
python3 << EOF
from koescript.audio import AudioCapture
ac = AudioCapture()
print(ac.get_available_devices())
EOF
```

### macOS: BlackHole Issues

#### BlackHole Not Detected

**Try automatic installation first (easiest):**
```bash
koescript init  # Will offer to install BlackHole automatically
```

**Verify BlackHole is installed:**
```bash
# Check if installed via Homebrew
brew list | grep blackhole

# Check system audio devices
system_profiler SPAudioDataType

# List devices with Koescript
koescript devices
```

**Reinstall BlackHole:**
```bash
# Via Homebrew
brew uninstall blackhole-2ch
brew install blackhole-2ch

# Or download manually from https://existential.audio/blackhole/
```

**Configure macOS Audio:**
1. Open **Audio MIDI Setup** (Applications > Utilities)
2. Click **"+"** and select **"Create Multi-Output Device"**
3. In the Multi-Output Device settings:
   - ✅ Check **your speakers/headphones**
   - ✅ Check **"BlackHole 2ch"**
   - Right-click your speakers → **"Use This Device For Sound Output"** (set as Master)
4. Open **System Settings > Sound > Output**
5. Select your **Multi-Output Device**

#### BlackHole No Audio Output

**Problem:** BlackHole is capturing but you can't hear audio

**Solution:**
1. Open **Audio MIDI Setup**
2. Select your **Multi-Output Device**
3. Right-click your **speakers** (not BlackHole)
4. Select **"Use This Device For Sound Output"** to set as Master Device
5. Verify both devices are checked in the Multi-Output Device

#### Loopback Not Working on macOS

```bash
# Play test sound
afplay /System/Library/Sounds/Glass.aiff

# Run Koescript in loopback mode
koescript translate --loopback

# Should capture the test sound if Multi-Output Device is configured correctly
```

### Windows: VB-Cable Issues

#### VB-Cable Not Detected

**Try automatic installation first (easiest):**
```bash
koescript init  # Will offer to install VB-Cable automatically
```

**Verify VB-Cable is installed:**
```powershell
# List audio devices
koescript devices

# Check Device Manager
devmgmt.msc
# Look under: Sound, video and game controllers → VB-Audio Virtual Cable
```

**Reinstall VB-Cable:**
```bash
# Via Chocolatey (requires admin)
choco install vb-cable

# Or manual installation:
# 1. Download from https://vb-audio.com/Cable/
# 2. Extract ZIP file
# 3. Right-click VBCABLE_Setup_x64.exe → Run as Administrator
# 4. Click "Install Driver"
# 5. Restart computer
```

**Important:** Reboot is required after VB-Cable installation!

#### VB-Cable No Audio Capture

**Problem:** VB-Cable installed but Koescript doesn't capture any audio

**Solution - Route application audio to VB-Cable:**
1. Right-click **Speaker icon** in system tray
2. Select **"Open Sound Settings"**
3. Scroll down to **"Advanced sound options"**
4. Click **"App volume and device preferences"**
5. For each app you want to capture (Chrome, Spotify, etc.):
   - Set **Output** to **"CABLE Input (VB-Audio Virtual Cable)"**
6. Keep your **System default output** as your regular speakers

```bash
# Now run Koescript in loopback mode
koescript translate --loopback
```

#### Windows No Audio Output

**Problem:** Audio routing to VB-Cable but can't hear anything

**Solution:**
- Keep **System Settings > Sound > Output** set to your regular speakers/headphones
- Only route **individual applications** to VB-Cable via App volume preferences
- This way you hear audio while Koescript captures from VB-Cable

#### VB-Cable Requires Restart

If VB-Cable was just installed and not detected:
```powershell
# Check if driver loaded
devmgmt.msc

# If not visible, restart computer
shutdown /r /t 0
```

### Linux: PulseAudio Issues

#### PulseAudio Not Running

```bash
# Check if PulseAudio is running
pulseaudio --check

# Start PulseAudio
pulseaudio --start

# Or restart
pulseaudio -k && pulseaudio --start
```

#### PulseAudio Loopback Module Not Loading

**Try automatic configuration first:**
```bash
koescript init  # Will configure PulseAudio automatically
```

**Manual loopback module control:**
```bash
# Load loopback module
pactl load-module module-loopback latency_msec=1

# Check if loaded
pactl list modules | grep loopback

# Unload module (when done)
pactl unload-module module-loopback

# Or unload by ID
pactl list short modules | grep loopback  # Note the ID number
pactl unload-module <ID>
```

#### PipeWire Users (Modern Linux Distributions)

**PipeWire compatibility:**
- Most modern distros (Fedora 34+, Ubuntu 22.10+) use PipeWire
- PipeWire has PulseAudio compatibility layer
- Koescript works with PipeWire via PulseAudio commands

**If issues occur:**
```bash
# Install PipeWire PulseAudio module
sudo apt install pipewire-pulse  # Ubuntu/Debian
sudo dnf install pipewire-pulseaudio  # Fedora

# Restart PipeWire
systemctl --user restart pipewire pipewire-pulse

# Test loopback
pw-loopback
```

#### ALSA-Only Systems

```bash
# Install PulseAudio
sudo apt install pulseaudio  # Ubuntu/Debian
sudo dnf install pulseaudio  # Fedora
sudo pacman -S pulseaudio    # Arch Linux

# Start PulseAudio
pulseaudio --start

# Verify
pulseaudio --check
```

#### Permission Denied on Linux

```bash
# Add user to audio group
sudo usermod -a -G audio $USER

# Log out and back in for changes to take effect

# Verify group membership
groups | grep audio
```

#### Loopback Not Working on Linux

```bash
# Test with speaker-test
speaker-test -t sine -f 440 &
SPEAKER_PID=$!

# Run Koescript
koescript translate --loopback

# Should capture the test tone
kill $SPEAKER_PID
```

## Transcription Issues

###whisper.cpp Binary Not Found

**Try automatic installation first (easiest):**
```bash
koescript init  # Will offer to build whisper.cpp automatically
```

**Check if installed:**
```bash
# macOS/Linux
ls ~/whisper.cpp/build/bin/whisper-cli
ls ~/whisper.cpp/main
which whisper-cli

# Windows
dir %USERPROFILE%\whisper.cpp\build\bin\whisper-cli.exe
where whisper-cli
```

**Install whisper.cpp manually:**

**macOS:**
```bash
cd ~
git clone https://github.com/ggerganov/whisper.cpp.git
cd whisper.cpp

# For Apple Silicon (Metal GPU acceleration)
WHISPER_METAL=1 make

# Verify
./build/bin/whisper-cli --version
```

**Windows:**
```bash
cd %USERPROFILE%
git clone https://github.com/ggerganov/whisper.cpp.git
cd whisper.cpp

# For NVIDIA GPUs (CUDA acceleration)
set WHISPER_CUDA=1
make

# Or for CPU only
make

# Verify
build\bin\Release\whisper-cli.exe --version
```

**Linux:**
```bash
cd ~
git clone https://github.com/ggerganov/whisper.cpp.git
cd whisper.cpp

# Install build essentials first
sudo apt install build-essential  # Ubuntu/Debian
sudo dnf install gcc gcc-c++ make  # Fedora

# For NVIDIA GPUs (CUDA acceleration)
WHISPER_CUDA=1 make

# Or for CPU only
make

# Verify
./build/bin/whisper-cli --version
```

### Transcription is Empty or Garbled

**Check audio levels:**
- Audio might be too quiet
- Increase system volume
- Move microphone closer
- For loopback: Ensure virtual audio device is routing correctly

**Check language setting:**
```bash
# Specify correct language
koescript translate --language ja  # For Japanese
koescript translate --language hi  # For Hindi
koescript translate --language en  # For English
```

**Try different model:**
```bash
# Use larger model for better accuracy
koescript translate --model large
```

**Check model file:**
```bash
# Verify model was downloaded correctly
ls -lh ~/.koescript/models/whisper/  # macOS/Linux
dir %USERPROFILE%\.koescript\models\whisper\  # Windows

# Re-download model
rm ~/.koescript/models/whisper/ggml-medium.en.bin  # macOS/Linux
del %USERPROFILE%\.koescript\models\whisper\ggml-medium.en.bin  # Windows

koescript init --model medium
```

### Transcription Too Slow

**Enable GPU acceleration:**

**macOS (Metal):**
```bash
cd ~/whisper.cpp
WHISPER_METAL=1 make

# Verify GPU is being used
koescript translate
# Should see: "✓ Using GPU-accelerated whisper.cpp"
# Expected: 30-50x real-time speed on Apple Silicon
```

**Windows (CUDA - NVIDIA GPUs only):**
```powershell
# Install CUDA Toolkit first
# Download from: https://developer.nvidia.com/cuda-downloads

# Verify NVIDIA GPU
nvidia-smi

# Build with CUDA
cd %USERPROFILE%\whisper.cpp
set WHISPER_CUDA=1
make

# Expected: 10-20x real-time speed with CUDA
```

**Linux (CUDA - NVIDIA GPUs only):**
```bash
# Install CUDA Toolkit
# Ubuntu: https://developer.nvidia.com/cuda-downloads
sudo apt install nvidia-cuda-toolkit  # May be outdated, use NVIDIA's repo

# Verify NVIDIA GPU
nvidia-smi

# Build with CUDA
cd ~/whisper.cpp
WHISPER_CUDA=1 make

# Expected: 10-20x real-time speed with CUDA
```

**Use smaller model:**
```bash
# For CPU-only systems or slower GPUs
koescript translate --model small    # Good balance (~3x real-time on CPU)
koescript translate --model base     # Faster (~5x real-time on CPU)
koescript translate --model tiny     # Fastest (~10x real-time on CPU)
```

**Check system resources:**
```bash
# macOS
top -o cpu

# Windows
taskmgr  # Task Manager

# Linux
top -o %CPU
htop  # More user-friendly (install with: sudo apt install htop)
```

## Translation Issues

### Translation Not Working

**Check language pair:**

```bash
# Ensure source and target languages are different
koescript translate --language ja --translate-to en  # ✓ Good
koescript translate --language en --translate-to en  # ✗ Won't translate
```

**Verify multilingual model:**

```bash
# Translation requires multilingual model (not .en)
# This is automatic, but verify:
ls ~/.koescript/models/whisper/ | grep -v ".en"

# Should see: ggml-medium.bin, ggml-large.bin (without .en suffix)
```

**Check NLLB model download:**

```bash
# Translation model downloads on first use
# Check HuggingFace cache
ls ~/.cache/huggingface/hub/ | grep nllb

# If missing, will download automatically on next run
```

### Translation Quality is Poor

**Use larger Whisper model:**

```bash
# Better transcription = better translation
koescript translate --model large --language ja --translate-to en
```

**Ensure correct source language:**

```bash
# Don't use auto-detect for best results
koescript translate --language ja --translate-to en  # ✓ Specify
koescript translate --language auto --translate-to en  # ✗ May be less accurate
```

## Performance Issues

### GPU Acceleration Not Working

**macOS (Metal):**
```bash
# Verify whisper.cpp is using Metal
koescript translate
# During startup, should see: "Using GPU-accelerated whisper.cpp"

# Rebuild with Metal
cd ~/whisper.cpp
make clean
WHISPER_METAL=1 make

# Test
./build/bin/whisper-cli --version
# Should mention Metal support
```

**Windows (CUDA):**
```powershell
# Verify NVIDIA GPU is detected
nvidia-smi

# Check CUDA installation
nvcc --version

# Rebuild whisper.cpp with CUDA
cd %USERPROFILE%\whisper.cpp
make clean
set WHISPER_CUDA=1
make
```

**Linux (CUDA):**
```bash
# Verify NVIDIA GPU is detected
nvidia-smi

# Check CUDA installation
nvcc --version

# Rebuild whisper.cpp with CUDA
cd ~/whisper.cpp
make clean
WHISPER_CUDA=1 make
```

### Expected Performance

**With GPU acceleration:**
- **macOS (Metal)**: 30-50x real-time on Apple Silicon
- **Windows/Linux (CUDA)**: 10-20x real-time with NVIDIA GPUs

| Model | macOS (Metal) | Windows/Linux (CUDA) | CPU Only |
|-------|---------------|----------------------|----------|
| tiny | 50x real-time | 25x real-time | 10x real-time |
| base | 30x real-time | 18x real-time | 5x real-time |
| small | 20x real-time | 12x real-time | 3x real-time |
| medium | 10x real-time | 8x real-time | 2x real-time |
| large | 10x real-time | 7x real-time | 1-1.5x real-time |

**Note:** Performance varies by GPU model and system load.

### High Memory Usage

**Normal memory usage:**
- tiny/base model: ~500 MB
- small model: ~1.2 GB
- medium model: ~2.5 GB
- large model: ~3.5 GB
- With translation: +3 GB for NLLB model

**If exceeding this:**
```bash
# Close other applications
# Use smaller models
koescript translate --model small

# Monitor memory
# macOS:
top -o mem

# Windows:
taskmgr  # Task Manager

# Linux:
top -o %MEM
htop  # Install with: sudo apt install htop
```

### High CPU Usage

**With GPU acceleration:**
- CPU usage should be LOW (5-15%)
- GPU doing most of the work

**If CPU is high (>50%):**

**macOS:**
```bash
# Check if GPU is actually being used
# Should see Metal support message

# Monitor GPU usage
sudo powermetrics --samplers gpu_power

# Rebuild whisper.cpp with Metal
cd ~/whisper.cpp
make clean
WHISPER_METAL=1 make
```

**Windows:**
```powershell
# Check GPU usage in Task Manager
taskmgr
# Go to Performance tab → GPU

# Verify CUDA is working
nvidia-smi

# Rebuild with CUDA if needed
cd %USERPROFILE%\whisper.cpp
make clean
set WHISPER_CUDA=1
make
```

**Linux:**
```bash
# Monitor NVIDIA GPU usage
nvidia-smi -l 1  # Refresh every second

# Or use watch
watch -n 1 nvidia-smi

# Rebuild with CUDA if needed
cd ~/whisper.cpp
make clean
WHISPER_CUDA=1 make
```

## Model Issues

### Model Download Fails

**Check internet connection:**

```bash
# Test HuggingFace access
curl -I https://huggingface.co

# Try manual download with curl
cd ~/.koescript/models/whisper/
curl -L -o ggml-base.en.bin \
  "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin"
```

**Check disk space:**

```bash
# Check available space
df -h ~/.koescript

# Models are large:
# - base: 142 MB
# - medium: 1.5 GB
# - large: 1.5 GB
```

**Use alternative download method:**

```bash
# Download directly with wget
cd ~/.koescript/models/whisper/
wget https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin
```

### Wrong Model Downloaded

**Check model files:**

```bash
ls -lh ~/.koescript/models/whisper/

# English-only models: ggml-{size}.en.bin
# Multilingual models: ggml-{size}.bin
```

**Delete and re-download:**

```bash
rm ~/.koescript/models/whisper/ggml-medium.bin
koescript init --model medium
```

### Model Verification Fails

**Re-download model:**

```bash
# Remove corrupted model
rm ~/.koescript/models/whisper/ggml-base.en.bin

# Try download again
koescript init --model base
```

## Platform-Specific Issues

### macOS Issues

#### macOS Catalina or Older

```bash
# Python 3.11 may not be available on older macOS
# Use Python 3.9 or 3.10, or install via pyenv

# Install pyenv
brew install pyenv

# Install Python 3.11
pyenv install 3.11.7
pyenv global 3.11.7

# Verify
python3 --version
```

#### Apple Silicon (M1/M2/M3/M4) Issues

**GPU not detected:**
```bash
# Ensure Xcode Command Line Tools installed
xcode-select --install

# Rebuild whisper.cpp with Metal
cd ~/whisper.cpp
make clean
WHISPER_METAL=1 make

# Verify Metal support
./build/bin/whisper-cli --version
# Should mention Metal/GPU support
```

**Rosetta 2 performance issues:**
```bash
# Check if running under Rosetta
arch
# Should output: arm64 (native), i386 (Rosetta)

# If under Rosetta, install native Python
arch -arm64 brew install python@3.11

# Use native terminal (not Rosetta)
# Right-click Terminal.app → Get Info → Uncheck "Open using Rosetta"
```

#### Intel Mac Issues

**Slower performance is expected:**
- Metal GPU acceleration less effective than Apple Silicon
- Use `small` or `base` models for better real-time performance
- CPU-only build works but slower

```bash
# Build for Intel Macs
cd ~/whisper.cpp
make clean
make  # CPU-only is usually best for Intel

# Or try Metal (may help on some Intel Macs with discrete GPU)
WHISPER_METAL=1 make
```

#### Homebrew-Related Issues

```bash
# Update Homebrew
brew update && brew upgrade

# Fix Homebrew permissions
sudo chown -R $(whoami) /usr/local/Cellar /usr/local/Homebrew

# Reinstall koescript
brew uninstall koescript
brew install koescript
```

### Windows Issues

#### Build Tools Missing

**Problem:** "make: command not found" or build failures

**Solution:**
```powershell
# Option 1: Install via Chocolatey (easier)
choco install make

# Option 2: Install MinGW-w64
# Download from: https://www.mingw-w64.org/
# Or via Chocolatey:
choco install mingw

# Option 3: Install Visual Studio Build Tools (large, ~7GB)
# Download from: https://visualstudio.microsoft.com/downloads/
# Select: Desktop development with C++
```

#### CUDA Installation Issues

**Problem:** CUDA not found or nvcc missing

**Solution:**
```powershell
# Install CUDA Toolkit from NVIDIA
# Download from: https://developer.nvidia.com/cuda-downloads

# Add CUDA to PATH (if not automatic)
$env:PATH += ";C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.x\bin"

# Verify installation
nvcc --version
nvidia-smi
```

#### Permission Errors

**Problem:** "Access denied" or administrator rights required

**Solution:**
```powershell
# Run PowerShell as Administrator
# Right-click PowerShell → "Run as Administrator"

# Or install for current user only
pip install --user koescript
```

#### VB-Cable Audio Glitches

**Problem:** Crackling, popping, or distorted audio

**Solution:**
1. Open **Device Manager**
2. Find **VB-Audio Virtual Cable** under "Sound, video and game controllers"
3. Right-click → **Properties**
4. Go to **Advanced** tab
5. Try different sample rates: 44100 Hz or 48000 Hz
6. Restart applications

#### Windows Firewall Blocking

**Problem:** Model downloads fail or timeout

**Solution:**
```powershell
# Allow Python through firewall
# Settings → Windows Security → Firewall → Allow an app

# Or temporarily disable (not recommended)
# Windows Security → Firewall → Turn off
```

### Linux Issues

#### Build Essentials Missing

**Problem:** "gcc: command not found" or build failures

**Solution:**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install build-essential git cmake

# Fedora/RHEL/CentOS
sudo dnf install gcc gcc-c++ make git cmake

# Arch Linux
sudo pacman -S base-devel git cmake
```

#### CUDA Installation Issues (NVIDIA GPUs)

**Ubuntu/Debian:**
```bash
# Add NVIDIA repository
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.0-1_all.deb
sudo dpkg -i cuda-keyring_1.0-1_all.deb
sudo apt update
sudo apt install cuda

# Add to PATH and LD_LIBRARY_PATH
echo 'export PATH=/usr/local/cuda/bin:$PATH' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
source ~/.bashrc

# Verify
nvidia-smi
nvcc --version
```

**Fedora:**
```bash
# Install from RPM Fusion
sudo dnf install cuda

# Or follow NVIDIA's official guide
# https://developer.nvidia.com/cuda-downloads
```

**Arch Linux:**
```bash
# Install CUDA from official repos
sudo pacman -S cuda

# Or from AUR
yay -S cuda
```

#### PulseAudio vs PipeWire Conflicts

**Problem:** Audio not working on modern distros

**Solution:**
```bash
# Check which audio system is running
pactl info | grep "Server Name"

# If PipeWire, ensure PulseAudio compatibility
sudo apt install pipewire-pulse  # Ubuntu
sudo dnf install pipewire-pulseaudio  # Fedora

# Restart audio services
systemctl --user restart pipewire pipewire-pulse
```

#### Dependencies Not Found

**Problem:** "ImportError" or missing Python packages

**Solution:**
```bash
# Install Python development packages
# Ubuntu/Debian
sudo apt install python3-dev python3-pip

# Fedora
sudo dnf install python3-devel python3-pip

# Arch Linux
sudo pacman -S python python-pip

# Reinstall koescript
pip install --force-reinstall koescript
```

#### SELinux Blocking (Fedora/RHEL)

**Problem:** Permission denied errors on Fedora/RHEL

**Solution:**
```bash
# Check SELinux status
sestatus

# Temporary: Set to permissive
sudo setenforce 0

# Permanent: Edit /etc/selinux/config
sudo nano /etc/selinux/config
# Change: SELINUX=permissive

# Or create SELinux policy for koescript
# (Advanced - consult SELinux documentation)
```

## Still Having Issues?

### Enable Debug Logging

**macOS/Linux:**
```bash
# Set environment variable
export KOESCRIPT_DEBUG=1

# Run command
koescript translate

# View logs
tail -f ~/.koescript/logs/koescript.log
```

**Windows:**
```powershell
# Set environment variable
$env:KOESCRIPT_DEBUG = "1"

# Run command
koescript translate

# View logs
type %USERPROFILE%\.koescript\logs\koescript.log
```

### Collect System Information

**macOS:**
```bash
# System information
system_profiler SPSoftwareDataType SPHardwareDataType

# Python and Koescript versions
python3 --version
koescript --version

# List installed packages
pip list | grep -E "(koescript|soundcard|whisper|transformers)"
```

**Windows:**
```powershell
# System information
systeminfo | findstr /B /C:"OS Name" /C:"OS Version"

# Python and Koescript versions
python --version
koescript --version

# List installed packages
pip list | findstr /I "koescript soundcard PyAudio whisper transformers"
```

**Linux:**
```bash
# System information
uname -a
lsb_release -a

# Python and Koescript versions
python3 --version
koescript --version

# List installed packages
pip list | grep -E "(koescript|soundcard|whisper|transformers)"
```

### Get Help

1. Check logs:
   - **macOS/Linux**: `~/.koescript/logs/koescript.log`
   - **Windows**: `%USERPROFILE%\.koescript\logs\koescript.log`

2. Search existing issues: [GitHub Issues](https://github.com/yourusername/koescript/issues)

3. Create new issue with:
   - **Operating System** and version
   - **Python version** (`python3 --version`)
   - **Koescript version** (`koescript --version`)
   - **GPU information** (if applicable)
   - **Virtual audio driver** (BlackHole, VB-Cable, PulseAudio)
   - **Model being used** (tiny, base, small, medium, large)
   - **Commands run**
   - **Error messages** (full traceback)
   - **Log file excerpt**

4. Platform-specific documentation:
   - **[PLATFORM_SUPPORT.md](PLATFORM_SUPPORT.md)** - Platform compatibility details
   - **[README.md](README.md)** - Installation and quick start
   - **[USAGE.md](USAGE.md)** - Complete command reference
