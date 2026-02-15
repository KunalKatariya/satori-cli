# Satori CLI v0.1.1 Release Notes

**Release Date:** February 15, 2025

## What's New

This maintenance release improves the installation experience and fixes several issues with the Homebrew formula and whisper.cpp setup.

## Bug Fixes

### Homebrew Installation
- **Fixed Homebrew formula installation issues** - Resolved virtualenv creation that was causing pip installation failures
- **Removed unnecessary ffmpeg dependency** - Significantly reduced installation size by removing ffmpeg and its codec dependencies (dav1d, lame, libvpx, opus, sdl2, svt-av1, x264, x265)
- **Installation now only requires:** python@3.11 and portaudio (saves ~80-90MB)

### whisper.cpp Setup
- **Improved detection logic** - Now properly detects when whisper.cpp directory exists but binary hasn't been built
- **Better error messages** - Clearer messaging about what's missing (directory vs compiled binary)
- **Smarter installation flow** - Offers to build from existing clone instead of forcing re-clone
- **Skips re-cloning** - If directory already exists, proceeds directly to building

## Documentation
- Updated README description for clarity

## Installation

### Homebrew (Recommended)
```bash
brew tap KunalKatariya/satori-cli
brew install satori-cli
```

### Upgrading from v0.1.0
```bash
brew update
brew upgrade satori-cli
```

### From Source
```bash
git clone https://github.com/KunalKatariya/satori-cli.git
cd satori-cli
poetry install
```

## Full Changelog

- `1ee6908` - Improve whisper.cpp detection and build logic
- `6e986ea` - Remove unnecessary ffmpeg dependency
- `fa957c6` - Revise README description for clarity
- `90475d8` - Fix virtualenv creation to include pip
- `da82631` - Fix formula to install all dependencies properly
- `401f557` - Fix Homebrew formula to use standard virtualenv installation
- `c1ce36d` - Add Homebrew formula with stable release URL

**View full diff:** https://github.com/KunalKatariya/satori-cli/compare/v0.1.0...v0.1.1

---

## System Requirements

- **OS:** macOS 12+ (Monterey or later)
- **Python:** 3.11+
- **Hardware:** Apple Silicon (M1/M2/M3) or Intel processors
- **For GPU acceleration:** Apple Silicon Mac with Metal support

## Known Issues

None reported for this release.

## Getting Help

- **Issues:** https://github.com/KunalKatariya/satori-cli/issues
- **Documentation:** See README.md and USAGE.md in the repository

## Credits

Built with whisper.cpp, Meta NLLB-200, and the Textual TUI framework.
