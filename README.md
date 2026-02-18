# Koescript

A cross-platform live translation CLI tool. Capture system audio in real-time, transcribe with Whisper, and translate using a beautiful TUI interface.

**Supports:** macOS • Windows • Linux

<img width="708" height="270" alt="image" src="https://github.com/user-attachments/assets/81218507-69c7-4895-ae0c-b7e7f652f4de" />


## Features

- 🎤 **Live Audio Capture** - Cross-platform audio capture with virtual audio device support
- 🤖 **GPU-Accelerated Transcription** - whisper.cpp with Metal (macOS), CUDA (Windows/Linux), or CPU fallback
- 🌍 **Offline Translation** - Meta NLLB-200 for Japanese ↔ English ↔ Hindi translation
- 🖥️ **Beautiful TUI** - Modern terminal interface with Textual framework
- ⚙️ **High Performance** - Real-time transcription with minimal latency
- 🔧 **Professional Stack** - Poetry, Ruff, MyPy, Pre-commit hooks
- 🌐 **Cross-Platform** - Works seamlessly on macOS, Windows, and Linux

## Tech Stack

- **Language**: Python 3.11+
- **Audio Capture**: SoundCard (macOS/Linux) + PyAudio/WASAPI (Windows)
- **Virtual Audio**: BlackHole (macOS), VB-Cable (Windows), PulseAudio (Linux)
- **AI Engine**: whisper.cpp with GPU acceleration
  - Metal for Apple Silicon Macs (30-50x faster)
  - CUDA for NVIDIA GPUs on Windows/Linux
  - CPU fallback for all platforms
- **Translation**: Meta NLLB-200 (1.3B multilingual model)
- **UI Framework**: Textual
- **Packaging**: Poetry
- **Code Quality**: Ruff + MyPy + Pre-commit

## Installation

### macOS

**Option 1: Homebrew (Recommended)**

```bash
brew tap KunalKatariya/koescript
brew install koescript
```

After installation, the `koescript` command will be available globally.

**Option 2: From Source**

```bash
# Clone the repository
git clone https://github.com/KunalKatariya/koescript.git
cd koescript

# Install with Poetry
poetry install

# Run with poetry run prefix
poetry run koescript --help
```

### Windows

**Option 1: pip (Recommended)**

```bash
# Install from PyPI
pip install koescript

# Or install from source
git clone https://github.com/KunalKatariya/koescript.git
cd koescript
pip install .
```

**Option 2: Poetry (For Development)**

```bash
git clone https://github.com/KunalKatariya/koescript.git
cd koescript
poetry install
poetry run koescript --help
```

### Linux

**Option 1: pip (Recommended)**

```bash
# Install from PyPI
pip install koescript

# Or install from source
git clone https://github.com/KunalKatariya/koescript.git
cd koescript
pip install .
```

**Option 2: Poetry (For Development)**

```bash
git clone https://github.com/KunalKatariya/koescript.git
cd koescript
poetry install
poetry run koescript --help
```

### Prerequisites

**All Platforms:**
- **Python 3.11 or higher**
- **Poetry** (for development only)
- **whisper.cpp** for GPU acceleration (can be auto-installed via `koescript init`)

**Platform-Specific:**
- **macOS**: BlackHole for system audio capture (auto-installed)
- **Windows**: VB-Cable for system audio capture (auto-installed with Chocolatey)
- **Linux**: PulseAudio loopback module (built-in, auto-configured)

## Quick Start

### 1. First-Time Setup

Run initialization - this will automatically offer to install dependencies:

```bash
koescript init
```

This will:
- **Automatically install virtual audio driver** (with your consent)
  - macOS: BlackHole via Homebrew
  - Windows: VB-Cable via Chocolatey (or manual download)
  - Linux: Configure PulseAudio loopback module
- **Automatically build whisper.cpp** (with your consent) for GPU acceleration
- Create necessary directories (`~/.koescript/`)
- Download initial Whisper model (base by default - multilingual)
- Verify audio device availability

**Skip automatic installation:**
```bash
koescript init --skip-deps  # Install dependencies manually
```

**Options:**

```bash
# Skip model download
koescript init --skip-download

# Download specific model
koescript init --model small     # 466 MB
koescript init --model medium    # 1.5 GB (recommended)
koescript init --model large     # 1.5 GB (best quality)
```

### 2. Configure Virtual Audio (For System Audio Capture)

To capture system audio (YouTube, Spotify, games, etc.), you need to configure a virtual audio device on your platform.

#### macOS: BlackHole Configuration

After installing BlackHole, configure your audio routing:

**Step 1: Create Multi-Output Device**

1. Open **Audio MIDI Setup** (Applications → Utilities → Audio MIDI Setup)
2. Click the **"+"** button at the bottom left and select **"Create Multi-Output Device"**
3. In the Multi-Output Device settings:
   - ✅ Check **your speakers/headphones** (e.g., "MacBook Pro Speakers" or "External Headphones")
   - ✅ Check **"BlackHole 2ch"**
   - Set your speakers as the **Master Device** (right-click → Use This Device For Sound Output)
4. Rename it to something memorable like **"Speakers + BlackHole"** (double-click the name)

**Step 2: Configure System Settings**

1. Open **System Settings** (System Preferences on older macOS)
2. Go to **Sound** → **Output**
3. Select your **Multi-Output Device** (e.g., "Speakers + BlackHole")

**Troubleshooting:**
- If you don't hear audio: Check that your speakers are set as Master Device in Audio MIDI Setup
- If Koescript doesn't see BlackHole: Make sure BlackHole is checked in your Multi-Output Device
- To switch back to normal audio: Go to System Settings → Sound → Output and select your regular speakers

#### Windows: VB-Cable Configuration

After installing VB-Cable:

**Step 1: Install VB-Cable**

If not auto-installed via Chocolatey, download and install manually:
1. Download VB-Cable from https://vb-audio.com/Cable/
2. Extract the ZIP file
3. Right-click `VBCABLE_Setup_x64.exe` and select **"Run as Administrator"**
4. Click **Install Driver**
5. **Restart your computer** for the driver to take effect

**Step 2: Configure Playback**

1. Right-click the **Speaker icon** in system tray → **Open Sound Settings**
2. Under **Output**, select your **speakers/headphones** as default
3. **Note**: When using `--loopback`, Koescript will automatically detect VB-Cable

**Step 3: Route Application Audio (Optional)**

To route specific application audio to VB-Cable:
1. Right-click **Speaker icon** → **Open Sound Settings** → **App volume and device preferences**
2. For each app you want to capture, set **Output** to **CABLE Input (VB-Audio Virtual Cable)**

**Troubleshooting:**
- If Koescript doesn't detect VB-Cable: Restart your computer after installation
- If no audio plays: Make sure your regular speakers are still set as default output
- For multiple applications: Use Sound Settings → App volume preferences

#### Linux: PulseAudio Configuration

PulseAudio loopback module is built-in - Koescript will auto-configure it.

**Manual Configuration (if needed):**

```bash
# Load loopback module
pactl load-module module-loopback latency_msec=1

# List modules to verify
pactl list modules | grep loopback

# Unload module (when done)
pactl unload-module module-loopback
```

**Step 3: Use in Koescript**

On all platforms, use the `--loopback` flag to capture system audio:

```bash
# Transcribe system audio (YouTube, Spotify, etc.)
koescript translate --loopback

# With translation
koescript translate --loopback --language ja --translate-to en
```

Verify your virtual audio device is detected:
```bash
koescript devices
```

### 3. Start Transcribing

```bash
# Basic transcription from microphone
koescript translate

# Transcribe system audio (requires virtual audio setup)
koescript translate --loopback

# Translate Japanese to English in real-time
koescript translate --loopback --language ja --translate-to en --model medium

# Translate Hindi to English
koescript translate --loopback --language hi --translate-to en --model large
```

### 4. List Audio Devices

```bash
koescript devices
```

### 5. Get Help

```bash
koescript --help
koescript translate --help
```

## Model Selection Guide

Choose the right model based on your needs:

| Model | Size | Speed | Accuracy | Best For |
|-------|------|-------|----------|----------|
| `tiny` | 75 MB | Fastest | Lower | Quick tests, low-resource systems |
| `base` | 142 MB | Very fast | Good | Quick transcription, real-time use |
| `small` | 466 MB | Fast | Better | Daily use, good balance |
| `medium` | 1.5 GB | Moderate | High | Important work, better accuracy (default) |
| `large` | 1.5 GB | Slower | Best | Critical content, maximum quality |

### Usage Examples:

```bash
# Fast transcription for quick tests
koescript translate --model small

# Better accuracy for important work (default)
koescript translate --model medium

# Best quality for critical content
koescript translate --model large
```

### Performance Notes:

**With GPU acceleration:**
- **macOS (Metal)**: 30-50x real-time speed on Apple Silicon
- **Windows/Linux (CUDA)**: 10-20x real-time speed on NVIDIA GPUs
- **CPU fallback**: Works on all systems, ~1-5x real-time speed

**Recommendations:**
- Real-time transcription works well even on CPU-only systems with `small` or `base` models
- GPU acceleration highly recommended for `medium` and `large` models
- Run `koescript init` to automatically detect and configure GPU support
- Models are downloaded once and cached in `~/.koescript/models/`

## Common Use Cases

### macOS
```bash
# Transcribe YouTube videos (requires BlackHole setup)
koescript translate --loopback --model medium

# Translate Japanese anime in real-time
koescript translate --loopback --language ja --translate-to en --model large

# Live meeting transcription (microphone input)
koescript translate --model medium
```

### Windows
```bash
# Transcribe YouTube videos (requires VB-Cable setup)
koescript translate --loopback --model medium

# Translate Hindi news to English
koescript translate --loopback --language hi --translate-to en --model large

# Transcribe Zoom meetings (route Zoom audio to VB-Cable)
koescript translate --loopback --model small
```

### Linux
```bash
# Transcribe Spotify podcasts (PulseAudio loopback)
koescript translate --loopback --model small

# Translate foreign language streams
koescript translate --loopback --language ja --translate-to en --model medium

# Transcribe system audio with GPU acceleration
koescript translate --loopback --model large
```

## Documentation

- **[USAGE.md](USAGE.md)** - Complete command reference and usage guide
- **[PLATFORM_SUPPORT.md](PLATFORM_SUPPORT.md)** - Platform compatibility matrix and features
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Solutions to common issues
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Development setup and guidelines
- **[WHISPER_SETUP.md](WHISPER_SETUP.md)** - Detailed whisper.cpp installation
- **[ROADMAP.md](ROADMAP.md)** - Planned features and development progress

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/koescript/issues)
- **Troubleshooting**: See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Platform Support**: See [PLATFORM_SUPPORT.md](PLATFORM_SUPPORT.md)
- **Questions**: Check [USAGE.md](USAGE.md) for detailed usage guide

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Development setup
- Code style guidelines
- Testing requirements
- Pull request process

## License

MIT License - See [LICENSE](LICENSE) file for details.

## Acknowledgments

- [whisper.cpp](https://github.com/ggerganov/whisper.cpp) - Fast Whisper implementation with GPU support
- [Meta NLLB](https://ai.meta.com/research/no-language-left-behind/) - Multilingual translation model
- [BlackHole](https://existential.audio/blackhole/) - Virtual audio driver for macOS
- [VB-Cable](https://vb-audio.com/Cable/) - Virtual audio driver for Windows
- [PulseAudio](https://www.freedesktop.org/wiki/Software/PulseAudio/) - Sound system for Linux
