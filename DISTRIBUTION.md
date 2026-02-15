# Distribution Guide

## How to Publish Satori CLI

### 1. Prepare for Distribution

The CLI is designed to be lightweight (~50KB) - models download automatically on first use.

**What gets packaged:**
- Python source code
- Configuration templates
- Documentation

**What doesn't get packaged:**
- AI models (auto-download on first use)
- User data
- Logs

### 2. Update Version

Edit `pyproject.toml`:
```toml
[tool.poetry]
version = "0.2.0"  # Update this
```

### 3. Build the Package

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build with poetry
poetry build

# This creates:
# dist/satori_cli-0.2.0-py3-none-any.whl
# dist/satori_cli-0.2.0.tar.gz
```

### 4. Test Locally

```bash
# Create test environment
python3 -m venv test_env
source test_env/bin/activate

# Install from wheel
pip install dist/satori_cli-0.2.0-py3-none-any.whl

# Test it works
satori --help
satori translate

# Clean up
deactivate
rm -rf test_env
```

### 5. Publish to PyPI

```bash
# Install twine
poetry add --dev twine

# Upload to TestPyPI first (recommended)
poetry run twine upload --repository testpypi dist/*

# Test install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ satori-cli

# If everything works, upload to real PyPI
poetry run twine upload dist/*
```

### 6. Post-Release

Update GitHub:
```bash
git tag v0.2.0
git push origin v0.2.0
```

Create GitHub release with changelog.

## Model Download Flow

When users run `satori translate` for the first time:

1. **Check for models**: Looks in `~/.satori/models/whisper/`
2. **Request consent**: Shows model size and asks permission
3. **Download**: Downloads from HuggingFace with progress bar
4. **Cache**: Stores locally for future use
5. **Never downloads again**: Unless model is deleted

Example user experience:
```
$ satori translate --model medium

Model Required: Whisper medium.en model
Size: 1.5 GB
Location: /Users/username/.satori/models/whisper

This is a one-time download. The model will be cached for future use.

Download model now? [Y/n]: y

Downloading medium.en model...
Downloaded: 850.3 / 1500.0 MB (56.7%)
...
✓ Model medium.en downloaded successfully
✓ Using GPU-accelerated whisper.cpp (English-only)
```

## User Installation

Users install with:
```bash
pip install satori-cli
```

On first run:
- Models auto-download with consent
- Takes ~10 minutes for large models
- Subsequent runs are instant

## Distribution Checklist

- [ ] Update version in `pyproject.toml`
- [ ] Update CHANGELOG.md
- [ ] Run tests: `poetry run pytest`
- [ ] Build package: `poetry build`
- [ ] Test locally
- [ ] Upload to TestPyPI
- [ ] Test install from TestPyPI
- [ ] Upload to PyPI
- [ ] Create Git tag
- [ ] Create GitHub release
- [ ] Announce on social media

## Package Size Comparison

| Component | Size | Bundled |
|-----------|------|---------|
| Source code | ~50 KB | ✅ Yes |
| Dependencies | ~200 MB | ✅ Auto-install |
| Whisper base | 142 MB | ❌ Auto-download |
| Whisper medium | 1.5 GB | ❌ Auto-download |
| NLLB-1.3B | 2.7 GB | ❌ Auto-download |

**Total package size on PyPI**: ~50 KB
**User disk usage after first run**: ~4-5 GB (with models)

## Security Notes

- Models download via HTTPS from HuggingFace
- No telemetry or tracking
- All processing is local/offline
- User consent required before downloads
- Models verified by file size check

## Support & Issues

Users can report issues at: https://github.com/yourusername/satori-cli/issues

Include in issue template:
- OS and version
- Python version
- Model being used
- Error logs from `~/.satori/logs/satori.log`
