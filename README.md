# Koescript

A live translation CLI tool for macOS. Capture system audio in real-time, transcribe with Whisper, and translate using a beautiful TUI interface.

<img width="708" height="270" alt="image" src="https://github.com/user-attachments/assets/81218507-69c7-4895-ae0c-b7e7f652f4de" />


## Features

- 🎤 **Live Audio Capture** - Seamless integration with SoundCard and BlackHole virtual audio
- 🤖 **GPU-Accelerated Transcription** - whisper.cpp with Metal support for M-series Macs (30x faster)
- 🌍 **Offline Translation** - Meta NLLB-200 for Japanese ↔ English ↔ Hindi translation
- 🖥️ **Beautiful TUI** - Modern terminal interface with Textual framework
- ⚙️ **High Performance** - Real-time transcription with minimal latency
- 🔧 **Professional Stack** - Poetry, Ruff, MyPy, Pre-commit hooks

## Tech Stack

- **Language**: Python 3.11+
- **Audio Capture**: SoundCard + BlackHole
- **AI Engine**: whisper.cpp with Metal GPU acceleration (30-50x faster)
- **Translation**: Meta NLLB-200 (1.3B multilingual model)
- **UI Framework**: Textual
- **Packaging**: Poetry
- **Code Quality**: Ruff + MyPy + Pre-commit

## Installation

### Option 1: Install from PyPI (Recommended)

```bash
brew tap KunalKatariya/koescript
brew install koescript
```

After installation, the `koescript` command will be available globally.

### Option 2: Install from Source (For Development)

```bash
# Clone the repository
git clone https://github.com/yourusername/koescript.git
cd koescript

# Install with Poetry
poetry install

# Run with poetry run prefix
poetry run koescript --help

# Or activate Poetry shell
poetry shell
koescript --help
```

### Prerequisites

- **Python 3.11 or higher**
- **macOS** (M-series or Intel)
- **BlackHole** for system audio capture (can be auto-installed via `koescript init`)
- **whisper.cpp** for GPU acceleration (can be auto-installed via `koescript init`)
- **Poetry** (for development only)

### Install BlackHole (Optional - Auto-installed by `koescript init`)

BlackHole is required for capturing system audio (YouTube, Spotify, etc.).

**Automatic installation (recommended):**
```bash
koescript init  # Will offer to install BlackHole automatically
```

**Manual installation:**

```bash
# Via Homebrew
brew install blackhole-2ch

# Or download from
# https://existential.audio/blackhole/
```

#### Configure Audio Routing (Required for System Audio Capture)

After installing BlackHole, you need to configure your audio routing to capture system audio (YouTube, Spotify, etc.) while still hearing the audio through your speakers/headphones.

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

**Step 3: Use in Koescript**

Now when you run Koescript with the `--loopback` flag, it will capture system audio:

```bash
# Transcribe system audio (YouTube, Spotify, etc.)
koescript translate --loopback

# With translation
koescript translate --loopback --language ja --translate-to en
```

You can verify BlackHole is detected:
```bash
koescript devices
```

**Troubleshooting:**
- If you don't hear audio: Check that your speakers are set as Master Device in Audio MIDI Setup
- If Koescript doesn't see BlackHole: Make sure BlackHole is checked in your Multi-Output Device
- To switch back to normal audio: Go to System Settings → Sound → Output and select your regular speakers

### Install whisper.cpp (Optional - Auto-installed by `koescript init`)

For 30x faster transcription with GPU acceleration.

**Automatic installation (recommended):**
```bash
koescript init  # Will offer to build whisper.cpp automatically
```

**Manual installation:**

```bash
cd ~
git clone https://github.com/ggerganov/whisper.cpp.git
cd whisper.cpp

# For Apple Silicon (M1/M2/M3/M4)
WHISPER_METAL=1 make

# For NVIDIA GPUs
WHISPER_CUDA=1 make

# For CPU only (not recommended)
make
```

## Quick Start

### 1. First-Time Setup

Run initialization - this will automatically offer to install dependencies:

```bash
koescript init
```

This will:
- **Automatically install BlackHole** (with your consent) via Homebrew for system audio capture
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

### 2. Start Transcribing

```bash
# Basic transcription with default settings
koescript translate

# Transcribe YouTube/Spotify (with BlackHole)
koescript translate --loopback

# Translate Japanese to English
koescript translate --loopback --language ja --translate-to en --model medium
```

### 3. List Audio Devices

```bash
koescript devices
```

### 4. Get Help

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

**With whisper.cpp GPU acceleration (Required):**
- All models run at 10x+ real-time speed
- Even `large` model is fast enough for live transcription
- Recommended: `medium` or `large` for best accuracy

**Important:**
- whisper.cpp is **required** for transcription
- Run `koescript init` to automatically install and build with GPU support
- Translation quality improves significantly with larger models
- Models are downloaded once and cached for future use
- You can switch between models anytime

## Common Use Cases

```bash
# Transcribe YouTube videos
koescript translate --loopback --model medium

# Translate Japanese anime in real-time
koescript translate --loopback --language ja --translate-to en --model large

# Transcribe Spotify podcasts
koescript translate --loopback --model small

# Live meeting transcription
koescript translate --model medium

# Translate Hindi news to English
koescript translate --loopback --language hi --translate-to en --model medium
```

## Documentation

- **[USAGE.md](USAGE.md)** - Complete command reference and usage guide
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Solutions to common issues
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Development setup and guidelines
- **[WHISPER_SETUP.md](WHISPER_SETUP.md)** - Detailed whisper.cpp installation
- **[ROADMAP.md](ROADMAP.md)** - Planned features and development progress

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/koescript/issues)
- **Troubleshooting**: See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
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
