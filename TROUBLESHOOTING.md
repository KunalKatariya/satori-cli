# Troubleshooting Guide

Solutions to common issues with Satori CLI.

## Table of Contents

- [Installation Issues](#installation-issues)
- [Audio Issues](#audio-issues)
- [Transcription Issues](#transcription-issues)
- [Translation Issues](#translation-issues)
- [Performance Issues](#performance-issues)
- [Model Issues](#model-issues)
- [System-Specific Issues](#system-specific-issues)

## Installation Issues

### Command Not Found: satori

**If you installed from PyPI:**

```bash
# Check if installed
pip list | grep satori-cli

# Reinstall
pip install --upgrade satori-cli

# Check Python bin directory is in PATH
echo $PATH | grep -o "[^:]*python[^:]*"
```

**If you installed from source:**

```bash
# Option 1: Install in editable mode
cd /path/to/satori-cli
pip install -e .

# Option 2: Use Poetry shell
poetry shell
satori --help

# Option 3: Use poetry run prefix
poetry run satori --help
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
pip install --user satori-cli

# Check file permissions
ls -la ~/.satori/

# Fix permissions if needed
chmod -R u+w ~/.satori/
```

## Audio Issues

### BlackHole Not Detected

**Try automatic installation first (easiest):**

```bash
satori init  # Will offer to install BlackHole automatically
```

**Verify BlackHole is installed:**

```bash
# Check if installed via Homebrew
brew list | grep blackhole

# Check system audio devices
system_profiler SPAudioDataType

# List devices with Satori
satori devices
```

**Reinstall BlackHole:**

```bash
# Via Homebrew
brew uninstall blackhole-2ch
brew install blackhole-2ch

# Or download manually
# https://existential.audio/blackhole/
```

**Configure macOS Audio:**

1. Open **System Settings > Sound**
2. Set **Output** to BlackHole 2ch
3. Open **Audio MIDI Setup** (Applications > Utilities)
4. Create a **Multi-Output Device**:
   - Include BlackHole 2ch
   - Include your speakers/headphones
5. Set Multi-Output as default output

### No Audio Devices Found

```bash
# List devices
satori devices

# Check system permissions
# macOS: System Settings > Privacy & Security > Microphone
# Grant permission to Terminal or your terminal app

# Test with Python
python3 << EOF
from satori.audio import AudioCapture
ac = AudioCapture()
print(ac.get_available_devices())
EOF
```

### Audio Recording Fails

**Check permissions:**
1. macOS: System Settings > Privacy & Security > Microphone
2. Ensure Terminal/iTerm has microphone access
3. Restart terminal after granting permission

**Check device:**

```bash
# Verify device exists
satori devices

# Test with specific device
satori translate --device "BlackHole 2ch"
```

**Check for conflicts:**

```bash
# Close other apps using audio
# Examples: Zoom, Discord, OBS, QuickTime

# Kill processes using audio
lsof | grep "coreaudio"
```

### Loopback Not Working

**Multi-Output Device Setup:**

1. Open Audio MIDI Setup
2. Click "+" and create Multi-Output Device
3. Check both:
   - BlackHole 2ch
   - Your speakers/headphones
4. Right-click Multi-Output and "Use This Device For Sound Output"
5. Now play audio (YouTube, Spotify, etc.)
6. Run: `satori translate --loopback`

**Test audio routing:**

```bash
# Play test sound
afplay /System/Library/Sounds/Glass.aiff

# Should see audio in Satori if Multi-Output is configured correctly
```

## Transcription Issues

### whisper.cpp Binary Not Found

**Try automatic installation first (easiest):**

```bash
satori init  # Will offer to build whisper.cpp automatically
```

**Check if installed:**

```bash
# Check common locations
ls ~/whisper.cpp/build/bin/whisper-cli
ls ~/whisper.cpp/main
which whisper-cli
```

**Install whisper.cpp:**

```bash
# Clone and build
cd ~
git clone https://github.com/ggerganov/whisper.cpp.git
cd whisper.cpp

# For Apple Silicon (Metal GPU)
WHISPER_METAL=1 make

# For NVIDIA GPUs (CUDA)
WHISPER_CUDA=1 make

# For CPU only
make

# Verify
./build/bin/whisper-cli --version
```

### Transcription is Empty or Garbled

**Check audio levels:**
- Audio might be too quiet
- Increase system volume
- Move microphone closer

**Check language setting:**

```bash
# Specify correct language
satori translate --language ja  # For Japanese
satori translate --language hi  # For Hindi
satori translate --language en  # For English
```

**Try different model:**

```bash
# Use larger model for better accuracy
satori translate --model large
```

**Check model file:**

```bash
# Verify model was downloaded correctly
ls -lh ~/.satori/models/whisper/

# Re-download model
rm ~/.satori/models/whisper/ggml-medium.en.bin
satori init --model medium
```

### Transcription Too Slow

**Enable GPU acceleration:**

```bash
# Install whisper.cpp with Metal support
cd ~/whisper.cpp
WHISPER_METAL=1 make

# Verify GPU is being used
satori translate
# Should see: "✓ Using GPU-accelerated whisper.cpp"
```

**Use smaller model:**

```bash
# For CPU-only systems
satori translate --model small    # Good balance
satori translate --model base     # Faster
satori translate --model tiny     # Fastest
```

**Check CPU usage:**

```bash
# Monitor during transcription
top -o cpu

# If CPU maxed out, close other applications
```

## Translation Issues

### Translation Not Working

**Check language pair:**

```bash
# Ensure source and target languages are different
satori translate --language ja --translate-to en  # ✓ Good
satori translate --language en --translate-to en  # ✗ Won't translate
```

**Verify multilingual model:**

```bash
# Translation requires multilingual model (not .en)
# This is automatic, but verify:
ls ~/.satori/models/whisper/ | grep -v ".en"

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
satori translate --model large --language ja --translate-to en
```

**Ensure correct source language:**

```bash
# Don't use auto-detect for best results
satori translate --language ja --translate-to en  # ✓ Specify
satori translate --language auto --translate-to en  # ✗ May be less accurate
```

## Performance Issues

### Slow on M-series Macs

**This should NOT happen with GPU. If it's slow:**

```bash
# Verify whisper.cpp is using Metal
# During startup, should see: "Using GPU-accelerated whisper.cpp"

# Rebuild with Metal
cd ~/whisper.cpp
make clean
WHISPER_METAL=1 make

# Test
./build/bin/whisper-cli --version
# Should mention Metal support
```

**Expected performance with GPU:**
- tiny: ~50x real-time
- base: ~30x real-time
- small: ~20x real-time
- medium: ~10x real-time
- large: ~10x real-time

**Note:** GPU acceleration with whisper.cpp is required for Satori. If you don't have whisper.cpp installed, run `satori init` to install it automatically.

### High Memory Usage

**Normal memory usage:**
- Base model: ~500 MB
- Medium model: ~2 GB
- Large model: ~3 GB
- With translation: +3 GB for NLLB model

**If exceeding this:**

```bash
# Close other applications
# Use smaller models
satori translate --model small

# Monitor memory
top -o mem
```

### High CPU Usage

**With whisper.cpp + GPU:**
- CPU usage should be LOW (5-15%)
- GPU doing the work

**If CPU is high (>50%):**

```bash
# Check if GPU is actually being used
# Should see Metal support message

# Rebuild whisper.cpp
cd ~/whisper.cpp
make clean
WHISPER_METAL=1 make
```

## Model Issues

### Model Download Fails

**Check internet connection:**

```bash
# Test HuggingFace access
curl -I https://huggingface.co

# Try manual download with curl
cd ~/.satori/models/whisper/
curl -L -o ggml-base.en.bin \
  "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin"
```

**Check disk space:**

```bash
# Check available space
df -h ~/.satori

# Models are large:
# - base: 142 MB
# - medium: 1.5 GB
# - large: 1.5 GB
```

**Use alternative download method:**

```bash
# Download directly with wget
cd ~/.satori/models/whisper/
wget https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin
```

### Wrong Model Downloaded

**Check model files:**

```bash
ls -lh ~/.satori/models/whisper/

# English-only models: ggml-{size}.en.bin
# Multilingual models: ggml-{size}.bin
```

**Delete and re-download:**

```bash
rm ~/.satori/models/whisper/ggml-medium.bin
satori init --model medium
```

### Model Verification Fails

**Re-download model:**

```bash
# Remove corrupted model
rm ~/.satori/models/whisper/ggml-base.en.bin

# Try download again
satori init --model base
```

## System-Specific Issues

### macOS Catalina or Older

```bash
# Python 3.11 may not be available
# Use Python 3.9 or 3.10

# Install with pyenv
brew install pyenv
pyenv install 3.11.7
pyenv global 3.11.7
```

### Apple Silicon (M1/M2/M3/M4) Issues

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
```

### Intel Mac Issues

**Slower performance is expected on Intel:**
- Use small or base models for better real-time performance
- whisper.cpp with CPU-only build is still required
- GPU acceleration may not be as effective as on Apple Silicon

### Linux Issues

**whisper.cpp build:**

```bash
# Install build tools
sudo apt install build-essential

# For CUDA (NVIDIA)
WHISPER_CUDA=1 make

# For CPU only
make
```

## Still Having Issues?

### Enable Debug Logging

```bash
# Set environment variable
export SATORI_DEBUG=1

# Run command
satori translate

# View logs
tail -f ~/.satori/logs/satori.log
```

### Collect System Information

```bash
# macOS
system_profiler SPSoftwareDataType SPHardwareDataType

# Python version
python3 --version

# Satori version
satori --version

# List installed packages
pip list
```

### Get Help

1. Check logs: `~/.satori/logs/satori.log`
2. Search existing issues: [GitHub Issues](https://github.com/yourusername/satori-cli/issues)
3. Create new issue with:
   - OS and version
   - Python version
   - Satori version
   - Model being used
   - Commands run
   - Error messages
   - Log file excerpt
