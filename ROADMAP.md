# Satori CLI - Development Roadmap

## Project Overview
Satori is a professional live translation CLI tool for macOS. It captures audio from a virtual audio input (BlackHole), processes it with Faster Whisper, and displays real-time translations through an intuitive TUI interface.

## Tech Stack
- **Language**: Python 3.11+
- **Audio Capture**: SoundCard + BlackHole
- **AI Engine**: Faster Whisper (base/small model)
- **UI Framework**: Textual
- **Packaging**: Poetry
- **Linting**: ruff + mypy
- **Quality**: pre-commit hooks

---

## Progress Tracking

### Phase 1: Project Setup ✅ DONE
- [x] Create professional project structure
- [x] Set up basic CLI with Click framework
- [x] Create gradient logo (blue-to-purple)
- [x] Establish package structure

### Phase 2: Project Configuration ✅ DONE
- [x] Convert to Poetry from pyproject.toml
- [x] Update dependencies (Textual, SoundCard, Faster Whisper)
- [x] Configure ruff for linting
- [x] Configure mypy for type checking
- [x] Set up pre-commit hooks
- [x] Initialize git repository

### Phase 3: Audio Capture Module ✅ DONE
- [x] Create audio capture utilities with SoundCard
- [x] Implement device management with Pydantic
- [x] Create AudioCapture class with device detection
- [x] Add sample rate and channel configuration

### Phase 4: Textual UI Implementation ✅ DONE
- [x] Create Textual TUI framework
- [x] Build StatusBar widget
- [x] Implement TranscriptionDisplay widget
- [x] Implement TranslationDisplay widget
- [x] Add blue-to-purple theme

### Phase 4.5: Configuration Module ✅ DONE
- [x] Create Pydantic models for Whisper config
- [x] Create Pydantic models for Translation config
- [x] Implement ConfigManager for persistent settings
- [x] Add device configuration management

### Phase 5: AI Integration ✅ DONE
- [x] Create WhisperTranscriber wrapper service
- [x] Implement lazy model loading with caching
- [x] Add async audio capture loop to SatoriApp
- [x] Integrate real-time transcription with UI updates
- [x] Add CLI options for device, model, and language
- [x] Implement graceful shutdown and error handling
- [x] All code passes ruff, mypy, and pre-commit checks

### Phase 6: Advanced Features
- [ ] Multiple language support
- [ ] Configuration management (settings, shortcuts)
- [ ] Log file management
- [ ] Error handling and recovery
- [ ] Performance monitoring

### Phase 7: Testing & Documentation
- [ ] Unit tests for core modules
- [ ] Integration tests for audio/AI pipeline
- [ ] User documentation
- [ ] Installation guide for BlackHole setup
- [ ] Troubleshooting guide

### Phase 8: Release & Distribution
- [ ] Version bumping
- [ ] Build and packaging with Poetry
- [ ] Create PyPI distribution
- [ ] GitHub releases
- [ ] Installation via pip/homebrew

---

## Current Status

### ✅ Completed (Phases 1-4.5)
- Basic CLI structure with gradient logo
- Click-based command framework
- Professional package layout
- Poetry configuration with all dependencies
- Ruff, MyPy, Pre-commit hooks setup
- Git repository initialized
- SoundCard audio capture module
- Device management with Pydantic
- Textual TUI framework with widgets
- Configuration management system
- Documentation (README, SETUP, ROADMAP)

### 🔄 In Progress
Phase 5: AI Integration - Faster Whisper integration and real-time transcription

### 📌 Next Up
- Implement Faster Whisper integration
- Create real-time transcription pipeline
- Add translation engine support
- Build audio streaming logic

---

## Dependencies Overview

### Core Dependencies
```
textual          # TUI Framework
soundcard        # Audio capture
faster-whisper   # Speech recognition AI
pydantic         # Configuration management
```

### Development Dependencies
```
ruff             # Fast linting
mypy             # Type checking
pytest           # Testing
pre-commit       # Git hooks
```

---

## Architecture

```
satori/
├── src/satori/
│   ├── audio/              # Audio capture & processing
│   │   ├── capture.py     # SoundCard integration
│   │   └── devices.py     # Device management
│   ├── ai/                # AI & transcription
│   │   ├── transcriber.py # Faster Whisper wrapper
│   │   └── translator.py  # Translation engine
│   ├── ui/                # Textual UI
│   │   ├── app.py        # Main TUI application
│   │   ├── widgets/      # Custom widgets
│   │   └── screens/      # UI screens
│   ├── config/            # Configuration
│   │   └── settings.py    # Settings management
│   ├── cli.py             # CLI entry point (Click)
│   └── __init__.py        # Package init
├── tests/                 # Test suite
├── pyproject.toml         # Poetry configuration
├── ruff.toml              # Ruff linting config
├── mypy.ini               # MyPy type checking config
├── .pre-commit-config.yaml # Pre-commit hooks
└── ROADMAP.md             # This file
```

---

## Notes & Considerations

### M4 MacBook Air Optimization
- Base Whisper model (~140M params) recommended for real-time performance
- Small model (244M) possible but may add latency
- GPU acceleration available via MLX framework (future enhancement)

### Audio Setup
- Requires BlackHole virtual audio device installation
- User needs to set BlackHole as audio input source
- Setup guide will be included in documentation

### Real-time Translation
- Streaming transcription for low latency
- Display updates as partial results come in
- Final text confirmation on speech pause detection

---

## Commands & Usage

### Planned CLI Commands
```
satori translate    # Start live translation session
satori config       # Manage settings
satori devices      # List audio devices
satori logs         # View translation logs
satori --version    # Show version
```

---

## Timeline Notes
- No specific deadlines set; development is feature-driven
- Focus on stability and performance over speed
- Community feedback will drive feature prioritization
