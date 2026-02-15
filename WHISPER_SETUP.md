# whisper.cpp Setup Guide

Satori CLI uses whisper.cpp for fast, GPU-accelerated transcription. This guide helps you install it.

## Quick Install

### macOS / Linux

```bash
# 1. Clone whisper.cpp
cd ~
git clone https://github.com/ggerganov/whisper.cpp.git
cd whisper.cpp

# 2. Build with GPU support

# For Apple Silicon (M1/M2/M3/M4):
WHISPER_METAL=1 make

# For NVIDIA GPUs:
WHISPER_CUDA=1 make

# For CPU only:
make

# 3. Test it works
./build/bin/whisper-cli --version
```

## Installation Locations

Satori searches for whisper.cpp in these locations:
1. `~/whisper.cpp/build/bin/whisper-cli`
2. `~/whisper.cpp/main`
3. `/usr/local/bin/whisper-cli`
4. `/usr/bin/whisper-cli`
5. Anywhere in your `$PATH`

## Verify Installation

```bash
# Check if satori can find whisper.cpp
satori translate

# Should show:
# ✓ Using GPU-accelerated whisper.cpp
```

## Troubleshooting

### Binary not found

If you see "whisper.cpp binary not found":

1. Check installation:
   ```bash
   ls -la ~/whisper.cpp/build/bin/whisper-cli
   ```

2. Verify it runs:
   ```bash
   ~/whisper.cpp/build/bin/whisper-cli --version
   ```

3. Add to PATH (optional):
   ```bash
   echo 'export PATH="$HOME/whisper.cpp/build/bin:$PATH"' >> ~/.zshrc
   source ~/.zshrc
   ```

### Build fails

**macOS**: Install Xcode Command Line Tools
```bash
xcode-select --install
```

**Linux**: Install build dependencies
```bash
sudo apt install build-essential
```

## Alternative: Use CPU Backend

If whisper.cpp installation fails, satori automatically falls back to CPU-based transcription:

```bash
satori translate --backend faster-whisper
```

This works but is ~30x slower.

## Model Management

Models are managed automatically by satori:
- Downloaded on first use
- Stored in `~/.satori/models/whisper/`
- No manual model setup required

## Performance

| Backend | Speed | Quality |
|---------|-------|---------|
| whisper.cpp (GPU) | ~10x real-time | Excellent |
| faster-whisper (CPU) | ~0.3x real-time | Excellent |

**Recommendation**: Use whisper.cpp with GPU for best experience.
