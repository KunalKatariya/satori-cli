# Satori CLI Usage Guide

Complete guide for using Satori CLI commands and features.

## Table of Contents

- [Commands Overview](#commands-overview)
- [satori init](#satori-init)
- [satori translate](#satori-translate)
- [satori devices](#satori-devices)
- [satori config](#satori-config)
- [Common Use Cases](#common-use-cases)

## Commands Overview

```bash
satori --help              # Show all commands
satori --version           # Show version
satori init                # First-time setup
satori devices             # List audio devices
satori translate           # Start transcription/translation
satori config              # Manage configuration
```

## satori init

Initialize Satori for first-time use.

### What It Does

1. Checks for system dependencies (BlackHole, whisper.cpp)
2. Offers to automatically install missing dependencies with your consent
3. Creates necessary directories (`~/.satori/models/`, `~/.satori/logs/`)
4. Downloads initial Whisper model (optional)
5. Verifies audio device availability
6. Provides setup guidance

### Usage

```bash
# Standard initialization with auto-install (recommended)
satori init

# Skip dependency auto-install
satori init --skip-deps

# Skip model download (models will auto-download when needed)
satori init --skip-download

# Download a specific model size during init
satori init --model tiny      # 75 MB - fastest
satori init --model base      # 142 MB - good balance
satori init --model small     # 466 MB - better quality
satori init --model medium    # 1.5 GB - high accuracy
satori init --model large     # 1.5 GB - best quality
```

### Automatic Dependency Installation

When you run `satori init` without `--skip-deps`, it will:

1. **Check for BlackHole**: If not found, offers to install via Homebrew
   - Runs: `brew install blackhole-2ch`
   - Required for system audio capture (YouTube, Spotify, etc.)

2. **Check for whisper.cpp**: If not found, offers to clone and build
   - Clones: `git clone https://github.com/ggerganov/whisper.cpp.git ~/whisper.cpp`
   - Builds with Metal GPU support: `WHISPER_METAL=1 make`
   - Build takes 3-5 minutes
   - Provides 30x faster transcription

You will be prompted before each installation - nothing happens without your consent.

### When to Run

- **Required**: Before using Satori for the first time
- **Optional**: After upgrading to a new version
- **Optional**: To download additional models

## satori translate

Start live transcription and translation session.

### Basic Usage

```bash
# Start with default settings (medium model, microphone input)
satori translate

# Fast transcription with small model
satori translate --model small

# Best quality with large model
satori translate --model large
```

### Audio Source Options

```bash
# Use microphone (default)
satori translate

# Auto-select loopback device for system audio (YouTube, Spotify, etc.)
satori translate --loopback

# Specify exact audio device
satori translate --device "BlackHole 2ch"
satori translate --device "MacBook Pro Microphone"
```

### Translation Options

```bash
# Transcribe only (no translation)
satori translate

# Translate Japanese to English
satori translate --language ja --translate-to en

# Translate Hindi to English
satori translate --language hi --translate-to en

# Auto-detect language and translate to English
satori translate --language auto --translate-to en

# Translate English to Japanese
satori translate --language en --translate-to ja
```

### Combined Examples

```bash
# YouTube transcription with high quality
satori translate --loopback --model large

# Japanese YouTube to English translation
satori translate --loopback --language ja --translate-to en --model medium

# Hindi podcast to English with specific device
satori translate --device "BlackHole 2ch" --language hi --translate-to en --model small

# Quick test with tiny model
satori translate --model tiny
```

### Keyboard Controls

During transcription:
- `Ctrl+C` - Stop recording and exit
- `Ctrl+R` - Reset transcription
- `?` - Show help

### Model Selection Guide

| Model | Size | Speed | Accuracy | Best For |
|-------|------|-------|----------|----------|
| `tiny` | 75 MB | Fastest | Lower | Quick tests, low-resource systems |
| `base` | 142 MB | Very fast | Good | Quick transcription, real-time use |
| `small` | 466 MB | Fast | Better | Daily use, good balance |
| `medium` | 1.5 GB | Moderate | High | Important work, better accuracy (default) |
| `large` | 1.5 GB | Slower | Best | Critical content, maximum quality |

**Performance Notes:**
- **With whisper.cpp GPU acceleration (Required)**: Even `large` model runs at ~10x real-time
- **Translation quality**: Improves significantly with larger models
- **Download once**: Models are cached for future use

### Supported Languages

**Transcription (--language):**
- `en` - English
- `ja` - Japanese
- `hi` - Hindi
- `auto` - Auto-detect (multilingual model required)

**Translation (--translate-to):**
- `en` - English
- `ja` - Japanese
- `hi` - Hindi

## satori devices

List all available audio devices for transcription.

### Usage

```bash
satori devices
```

### Output Example

```
Available Audio Devices:

  1. MacBook Pro Microphone
  2. BlackHole 2ch (System Audio/Loopback)
  3. External Microphone

Tip: Use loopback devices to capture YouTube, Spotify, etc.
Example: satori translate --device "BlackHole 2ch"
```

### Device Types

- **Microphones**: Built-in or external microphones
- **Loopback devices**: Virtual devices for system audio (BlackHole, Loopback, Soundflower)
- **Aggregate devices**: Combined input/output devices

## satori config

Manage Satori configuration settings.

### Usage

```bash
satori config
```

### Configuration Options

- Audio device selection
- Whisper model size preferences
- Language preferences
- Translation provider settings
- Log directory location

### Configuration Files

User configuration is stored in `~/.satori/`:

```
~/.satori/
├── models/                  # Downloaded models
│   └── whisper/
│       ├── ggml-base.en.bin
│       ├── ggml-medium.en.bin
│       └── ggml-large.bin
├── logs/                    # Application logs
│   └── satori.log
├── config.json             # Main configuration (future)
└── devices.json            # Audio device settings (future)
```

## Common Use Cases

### 1. Transcribe YouTube Videos

```bash
# Set up (one-time)
brew install blackhole-2ch
# Configure system audio to route through BlackHole

# Start transcription
satori translate --loopback --model medium
```

### 2. Translate Japanese Anime in Real-Time

```bash
# Use large model for best accuracy
satori translate --loopback --language ja --translate-to en --model large
```

### 3. Transcribe Podcast from Spotify

```bash
# Use small model for good balance
satori translate --loopback --model small
```

### 4. Live Meeting Transcription

```bash
# Use built-in microphone with medium model
satori translate --model medium
```

### 5. Transcribe Hindi News

```bash
# Translate Hindi to English
satori translate --loopback --language hi --translate-to en --model medium
```

### 6. Quick Audio Test

```bash
# Use tiny model for fastest results
satori translate --model tiny
```

### 7. Offline Translation (No Internet)

```bash
# All processing is local - works without internet
satori translate --loopback --language ja --translate-to en --model large
```

### 8. Multiple Languages in Same Session

```bash
# Use auto-detect with multilingual model
satori translate --loopback --language auto --translate-to en --model large
```

## Tips and Best Practices

### For Best Accuracy
- Use `medium` or `large` models
- Ensure good audio quality (clear, minimal background noise)
- Use loopback devices for digital audio (YouTube, Spotify)
- Position microphone 6-12 inches from mouth for speech

### For Best Performance
- Install whisper.cpp with GPU support (30-50x faster)
- Use `small` or `base` models if you don't have whisper.cpp
- Close unnecessary applications during transcription

### For Translation
- Larger models produce significantly better translations
- Use `--language` to specify source language for better accuracy
- Auto-detect works but may be less accurate

### Managing Disk Space

Models are downloaded to `~/.satori/models/whisper/`:

```bash
# View model sizes
ls -lh ~/.satori/models/whisper/

# Remove unused models
rm ~/.satori/models/whisper/ggml-tiny.en.bin

# Models will be re-downloaded when needed
```

## Environment Variables

You can customize Satori behavior with environment variables:

```bash
# Custom models directory
export SATORI_MODELS_DIR="$HOME/custom/models"

# Custom log directory
export SATORI_LOG_DIR="$HOME/custom/logs"

# Enable debug logging
export SATORI_DEBUG=1
```

## Logs and Debugging

View logs for troubleshooting:

```bash
# View recent logs
tail -f ~/.satori/logs/satori.log

# View all logs
cat ~/.satori/logs/satori.log

# Clear logs
rm ~/.satori/logs/satori.log
```

## Advanced Usage

### Custom Binary Path

If whisper.cpp is installed in a custom location:

```bash
export WHISPER_CPP_BINARY="/custom/path/to/whisper-cli"
satori translate
```

### Testing Different Settings

```bash
# Compare model sizes
satori translate --model small   # Note the quality
satori translate --model medium  # Compare difference
satori translate --model large   # Best quality
```

## Next Steps

- See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues
- See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup
- See [ROADMAP.md](ROADMAP.md) for planned features
