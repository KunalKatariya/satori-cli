# Contributing to Satori CLI

Thank you for your interest in contributing to Satori CLI! This guide will help you get started with development.

## Project Structure

```
satori/
├── src/satori/
│   ├── __init__.py              # Package initialization
│   ├── __main__.py              # Module entry point
│   ├── cli.py                   # Main CLI with Click
│   ├── audio/                   # Audio capture module
│   │   ├── capture.py          # SoundCard integration
│   │   ├── devices.py          # Device management
│   │   └── __init__.py
│   ├── ai/                      # AI and transcription
│   │   ├── transcriber.py      # Faster Whisper wrapper
│   │   ├── whisper_cpp.py      # whisper.cpp wrapper
│   │   ├── translator.py       # Meta NLLB translation
│   │   └── __init__.py
│   ├── ui/                      # Textual TUI components
│   │   ├── app.py              # Main TUI application
│   │   ├── widgets/            # Custom widgets
│   │   └── __init__.py
│   ├── config/                  # Configuration management
│   │   ├── settings.py         # Pydantic models
│   │   └── __init__.py
│   ├── models/                  # Model management
│   │   ├── downloader.py       # Model download with consent
│   │   └── __init__.py
│   └── utils/                   # Utility functions
│       ├── logger.py           # Logging utilities
│       └── __init__.py
├── tests/                       # Test suite
├── .git/                        # Git repository
├── .gitignore                   # Git ignore rules
├── .pre-commit-config.yaml      # Pre-commit hooks
├── pyproject.toml               # Poetry configuration
├── ruff.toml                    # Ruff linting config
├── mypy.ini                     # MyPy type checking
└── README.md                    # Main documentation
```

## Development Setup

### Prerequisites

- Python 3.11 or higher
- macOS (M-series or Intel)
- Poetry package manager
- Git

### Initial Setup

1. **Fork and clone the repository:**
   ```bash
   git clone https://github.com/yourusername/satori-cli.git
   cd satori-cli
   ```

2. **Install dependencies:**
   ```bash
   # Install Poetry if you haven't already
   curl -sSL https://install.python-poetry.org | python3 -
   export PATH="$HOME/.local/bin:$PATH"

   # Install all dependencies including dev tools
   poetry install
   ```

3. **Activate the Poetry environment:**
   ```bash
   poetry shell
   ```

4. **Initialize pre-commit hooks:**
   ```bash
   pre-commit install
   ```

5. **Verify installation:**
   ```bash
   satori --help
   ```

### Development Workflow

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/amazing-feature
   ```

2. **Make your changes:**
   - Follow the existing code style
   - Add tests for new functionality
   - Update documentation as needed

3. **Run quality checks:**
   ```bash
   # Lint and format code
   poetry run ruff check --fix src/
   poetry run ruff format src/

   # Type checking
   poetry run mypy src/

   # Run tests
   poetry run pytest

   # Run tests with coverage
   poetry run pytest --cov=src/satori
   ```

4. **Commit your changes:**
   ```bash
   git add .
   git commit -m "Add amazing feature"
   ```

   Pre-commit hooks will automatically run. If they fail, fix the issues and commit again.

5. **Push to your fork:**
   ```bash
   git push origin feature/amazing-feature
   ```

6. **Create a Pull Request:**
   - Go to the main repository on GitHub
   - Click "New Pull Request"
   - Select your branch
   - Describe your changes
   - Submit the PR

## Code Quality Standards

### Linting and Formatting

We use Ruff for both linting and formatting:

```bash
# Check for linting issues
poetry run ruff check src/

# Auto-fix linting issues
poetry run ruff check --fix src/

# Format code
poetry run ruff format src/
```

Configuration is in `ruff.toml`.

### Type Checking

We use MyPy for static type checking:

```bash
# Type check the entire project
poetry run mypy src/

# Type check specific file
poetry run mypy src/satori/cli.py
```

Configuration is in `mypy.ini`.

### Pre-commit Hooks

Pre-commit hooks run automatically on every commit:

```bash
# Manually run hooks on all files
poetry run pre-commit run --all-files

# Skip hooks for a specific commit (not recommended)
git commit --no-verify
```

Configuration is in `.pre-commit-config.yaml`.

## Testing

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run specific test file
poetry run pytest tests/test_audio.py

# Run with verbose output
poetry run pytest -v

# Run with coverage report
poetry run pytest --cov=src/satori --cov-report=term-missing
```

### Writing Tests

- Place tests in the `tests/` directory
- Name test files with `test_` prefix
- Use descriptive test names that explain what is being tested
- Mock external dependencies (APIs, file system, etc.)

## Architecture Guidelines

### Audio Module (`src/satori/audio/`)

Handles audio capture using SoundCard library:
- `capture.py` - Main audio capture logic
- `devices.py` - Device enumeration and selection

### AI Module (`src/satori/ai/`)

Handles transcription and translation:
- `transcriber.py` - Faster Whisper (CPU-based)
- `whisper_cpp.py` - whisper.cpp wrapper (GPU-accelerated)
- `translator.py` - Meta NLLB translation

### UI Module (`src/satori/ui/`)

Textual-based TUI:
- `app.py` - Main application loop with VAD and phrase detection
- `widgets/` - Custom UI components

### Models Module (`src/satori/models/`)

Model management:
- `downloader.py` - Downloads models from HuggingFace with user consent
- Handles caching and verification

## Configuration Files

### `pyproject.toml`
Poetry configuration and dependencies. When adding dependencies:
```bash
# Runtime dependency
poetry add package-name

# Development dependency
poetry add --group dev package-name
```

### `ruff.toml`
Linting and formatting rules. Keep strict but pragmatic.

### `mypy.ini`
Type checking configuration. We allow some flexibility for rapid development.

### `.pre-commit-config.yaml`
Pre-commit hooks configuration. Runs ruff and mypy automatically.

## Commit Message Guidelines

Follow conventional commits format:

```
feat: add Hindi language support
fix: correct audio device detection on M4 Macs
docs: update model selection guide
refactor: simplify VAD logic
test: add tests for translator module
```

Types:
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation changes
- `refactor` - Code refactoring
- `test` - Adding or updating tests
- `chore` - Maintenance tasks

## Pull Request Guidelines

1. **Title**: Clear, descriptive summary of changes
2. **Description**: Explain what changes were made and why
3. **Testing**: Describe how you tested the changes
4. **Screenshots**: Include for UI changes
5. **Breaking Changes**: Clearly document any breaking changes
6. **Issue Reference**: Link to related issues if applicable

## Code Style

- **Formatting**: Handled by Ruff (Black-compatible)
- **Line length**: 100 characters
- **Imports**: Sorted with isort (via Ruff)
- **Docstrings**: Google style
- **Type hints**: Use type hints for function signatures

### Example:

```python
def transcribe_audio(
    audio: np.ndarray,
    sample_rate: int = 16000,
    language: Optional[str] = None
) -> str:
    """Transcribe audio using Whisper.

    Args:
        audio: Audio data as numpy array
        sample_rate: Sample rate in Hz
        language: Language code (None for auto-detect)

    Returns:
        Transcribed text

    Raises:
        RuntimeError: If transcription fails
    """
    # Implementation
    pass
```

## Getting Help

- **Documentation**: Check README.md, USAGE.md, and TROUBLESHOOTING.md
- **Issues**: Search existing issues or create a new one
- **Discussions**: Use GitHub Discussions for questions
- **Code Review**: Don't hesitate to ask for clarification in PRs

## Areas for Contribution

We welcome contributions in these areas:

### High Priority
- [ ] Unit tests for audio capture
- [ ] Integration tests for transcription pipeline
- [ ] Performance benchmarks and optimization
- [ ] Windows and Linux support

### Features
- [ ] More language pairs for translation
- [ ] Real-time translation streaming
- [ ] Export transcriptions to file
- [ ] Configuration UI/wizard

### Documentation
- [ ] Video tutorials
- [ ] Usage examples
- [ ] API documentation
- [ ] Troubleshooting guides

### Quality
- [ ] Error handling improvements
- [ ] Logging enhancements
- [ ] Progress indicators for long operations

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

Feel free to open an issue or start a discussion if you need help getting started!
