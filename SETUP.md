# Satori CLI - Setup & Development Guide

## Table of Contents

1. [Initial Setup](#initial-setup)
2. [Using Poetry](#using-poetry)
3. [Development Workflow](#development-workflow)
4. [Code Quality](#code-quality)
5. [Testing](#testing)
6. [Troubleshooting](#troubleshooting)

## Initial Setup

### Prerequisites

- Python 3.11 or higher
- macOS (M-series or Intel)
- Poetry package manager (installed automatically if using `pip`)

### Step 1: Clone and Navigate

```bash
cd /path/to/satori
```

### Step 2: Create Virtual Environment (Optional)

Poetry manages its own virtual environments, but you can create one locally:

```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Poetry (if not already installed)

```bash
curl -sSL https://install.python-poetry.org | python3 -
export PATH="$HOME/.local/bin:$PATH"
```

### Step 4: Install Dependencies

```bash
# Install all dependencies including dev tools
poetry install

# Or activate Poetry's virtual environment
poetry shell
```

## Using Poetry

### Basic Commands

```bash
# Install dependencies
poetry install

# Add a new dependency
poetry add package-name

# Add a development dependency
poetry add --group dev package-name

# Update dependencies
poetry update

# Show installed packages
poetry show

# Run a command in the Poetry environment
poetry run <command>

# Activate the Poetry environment
poetry shell
```

### Running Satori Commands with Poetry

```bash
# Show CLI help
poetry run satori --help

# Start live translation
poetry run satori translate

# View version
poetry run satori --version
```

### Poetry Configuration

The project dependencies are managed in `pyproject.toml`:

**Core Dependencies:**
- click - CLI framework
- rich - Terminal output styling
- textual - TUI framework
- soundcard - Audio capture
- faster-whisper - Speech recognition
- pydantic - Configuration validation

**Development Dependencies:**
- ruff - Unified linting and formatting
- mypy - Static type checking
- pytest - Testing framework
- pre-commit - Git hooks

## Development Workflow

### Recommended Setup

```bash
# 1. Install with dev dependencies
poetry install

# 2. Activate environment
poetry shell

# 3. Initialize pre-commit hooks
pre-commit install

# 4. Start coding!
```

### File Structure Overview

```
src/satori/
├── cli.py                   # Main CLI entry point
├── audio/                   # Audio capture module
│   ├── capture.py          # SoundCard integration
│   └── devices.py          # Device configuration
├── ui/                      # Textual TUI components
│   ├── app.py              # Main application
│   └── widgets/            # Custom widgets
├── config/                  # Configuration management
│   └── settings.py         # Pydantic models
└── utils/                   # Utilities
    └── logger.py           # Logging
```

## Code Quality

### Ruff - Unified Linting & Formatting

Ruff is configured in `ruff.toml` and handles both linting and formatting.

```bash
# Check code for linting issues
poetry run ruff check src/

# Fix linting issues automatically
poetry run ruff check --fix src/

# Format code
poetry run ruff format src/

# Check specific file
poetry run ruff check src/satori/cli.py
```

### MyPy - Static Type Checking

MyPy is configured in `mypy.ini`.

```bash
# Type check entire project
poetry run mypy src/

# Type check specific file
poetry run mypy src/satori/cli.py
```

### Pre-commit Hooks

Pre-commit hooks run automatically on every commit:

```bash
# Initialize hooks (one-time)
poetry run pre-commit install

# Manually run hooks on all files
poetry run pre-commit run --all-files

# Skip hooks for a specific commit
git commit --no-verify
```

## Testing

### Run Tests

```bash
# Run all tests
poetry run pytest

# Run tests with coverage
poetry run pytest --cov=src/satori

# Run specific test file
poetry run pytest tests/test_audio.py

# Run with verbose output
poetry run pytest -v
```

## Troubleshooting

### Poetry Virtual Environment Issues

```bash
# Check which Python is active
poetry env info

# Use specific Python version
poetry env use /usr/local/bin/python3.11

# Remove and recreate environment
poetry env remove 3.11
poetry install
```

### Command Not Found: poetry

```bash
# Add to PATH
export PATH="$HOME/.local/bin:$PATH"
```

### Dependency Conflicts

```bash
# Update all dependencies
poetry update

# Check for conflicts
poetry check
```

### Pre-commit Hooks Failing

```bash
# View hook output
poetry run pre-commit run --all-files -v

# Fix common issues
poetry run ruff check --fix src/
poetry run ruff format src/
```

### Audio Issues

```bash
# Test audio capture manually
poetry run python -c "
from satori.audio import AudioCapture
ac = AudioCapture()
devices = ac.get_available_devices()
for d in devices:
    print(f'Device: {d.name}')
"
```

## Configuration Files

- **pyproject.toml** - Poetry configuration and dependencies
- **ruff.toml** - Ruff linter and formatter configuration
- **mypy.ini** - MyPy type checker configuration
- **.pre-commit-config.yaml** - Pre-commit hook definitions
