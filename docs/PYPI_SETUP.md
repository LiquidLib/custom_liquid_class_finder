# PyPI Publishing Setup Guide

This guide will help you set up your package for publishing to PyPI.

## Prerequisites

1. **PyPI Account**: Create an account on [PyPI](https://pypi.org/account/register/)
2. **TestPyPI Account**: Create an account on [TestPyPI](https://test.pypi.org/account/register/)
3. **API Tokens**: Generate API tokens for both PyPI and TestPyPI

## Step 1: Generate API Tokens

### PyPI API Token
1. Go to [PyPI Account Settings](https://pypi.org/manage/account/)
2. Click "Add API token"
3. Give it a name (e.g., "custom-liquid-class-finder")
4. Select "Entire account (all projects)"
5. Copy the token (it starts with `pypi-`)

### TestPyPI API Token
1. Go to [TestPyPI Account Settings](https://test.pypi.org/manage/account/)
2. Click "Add API token"
3. Give it a name (e.g., "custom-liquid-class-finder-test")
4. Select "Entire account (all projects)"
5. Copy the token (it starts with `pypi-`)

## Step 2: Set Up GitHub Secrets

In your GitHub repository, go to Settings → Secrets and variables → Actions, and add:

- `PYPI_API_TOKEN`: Your PyPI API token
- `TEST_PYPI_API_TOKEN`: Your TestPyPI API token

## Step 3: Local Testing

### Install Build Tools
```bash
pip install build twine
```

### Build Package
```bash
python -m build
```

### Check Package
```bash
twine check dist/*
```

### Test Upload to TestPyPI
```bash
twine upload --repository testpypi dist/*
```

### Test Installation
```bash
pip install --index-url https://test.pypi.org/simple/ custom-liquid-class-finder
```

## Step 4: GitHub Actions Setup

The repository includes several GitHub Actions workflows:

### 1. Pre-commit Checks (`/.github/workflows/pre-commit.yml`)
- Runs on every PR and push to main/develop
- Checks code formatting, linting, and type hints

### 2. CI/CD Pipeline (`/.github/workflows/ci-cd.yml`)
- Runs on PRs, pushes to main/develop, and releases
- Includes linting, testing, building, and publishing

### 3. Release Workflow (`/.github/workflows/release.yml`)
- Runs when you push a tag starting with 'v'
- Automatically publishes to PyPI and creates GitHub release

## Step 5: Publishing Process

### Manual Publishing

1. **Update Version**: Update version in `pyproject.toml`
2. **Update CHANGELOG**: Add release notes to `CHANGELOG.md`
3. **Build**: `python -m build`
4. **Check**: `twine check dist/*`
5. **Upload to TestPyPI**: `twine upload --repository testpypi dist/*`
6. **Test Installation**: `pip install --index-url https://test.pypi.org/simple/ custom-liquid-class-finder`
7. **Upload to PyPI**: `twine upload dist/*`

### Automated Publishing

1. **Create Release**: Go to GitHub → Releases → "Create a new release"
2. **Tag Version**: Use format `v0.1.0`
3. **Release Title**: Use format `v0.1.0`
4. **Description**: Copy from `CHANGELOG.md`
5. **Publish**: Click "Publish release"

The GitHub Actions will automatically:
- Build the package
- Run tests
- Publish to PyPI
- Create GitHub release with assets

## Step 6: Package Configuration

### Key Files

- `pyproject.toml`: Package configuration and metadata
- `MANIFEST.in`: Files to include in distribution
- `CHANGELOG.md`: Release notes
- `README.md`: Package documentation
- `LICENSE`: License file

### Important Configuration

```toml
[project]
name = "custom-liquid-class-finder"  # Must be unique on PyPI
version = "0.1.0"  # Semantic versioning
description = "Liquid Class Calibration with Gradient Descent for Opentrons"
readme = "README.md"
license = {text = "MIT"}
authors = [
    {name = "Roman Gurovich", email = "romangurovich@gmail.com"}
]
keywords = ["opentrons", "liquid-handling", "automation", "calibration"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Scientific/Engineering :: Bio-Informatics",
]
requires-python = ">=3.10"
dependencies = [
    "opentrons>=6.3.0",
    "opentrons-protocol-api>=2.22.0",
]
```

## Step 7: Testing Your Package

### Local Testing
```bash
# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run quality checks
black --check .
flake8 --max-line-length=100 --extend-ignore=E203,W503 .
mypy --ignore-missing-imports .
```

### Package Testing
```bash
# Build and install
python -m build
pip install dist/*.whl

# Test import
python -c "import liquids; print('Success!')"

# Test command line tool
liquid-class-manager --help
```

## Step 8: Troubleshooting

### Common Issues

1. **Package Name Already Taken**
   - Check PyPI for available names
   - Use a more specific name

2. **Build Errors**
   - Check `pyproject.toml` syntax
   - Ensure all dependencies are listed
   - Check `MANIFEST.in` includes all necessary files

3. **Import Errors**
   - Check `__init__.py` files exist
   - Verify package structure
   - Test imports locally first

4. **GitHub Actions Failures**
   - Check secrets are set correctly
   - Verify workflow syntax
   - Check Python version compatibility

### Useful Commands

```bash
# Check package structure
python -c "import liquids; print(liquids.__file__)"

# List installed packages
pip list | grep custom-liquid-class-finder

# Uninstall package
pip uninstall custom-liquid-class-finder

# Check package metadata
python -c "import pkg_resources; print(pkg_resources.get_distribution('custom-liquid-class-finder').metadata)"

# Validate package
twine check dist/*
```

## Step 9: Maintenance

### Version Management
- Use semantic versioning (MAJOR.MINOR.PATCH)
- Update version in `pyproject.toml`
- Update `CHANGELOG.md` with release notes

### Documentation Updates
- Keep README.md up to date
- Update examples and usage
- Add new features to documentation

### Dependency Updates
- Regularly update dependencies
- Test with new versions
- Update version constraints in `pyproject.toml`

## Support

If you encounter issues:
1. Check the [PyPI documentation](https://packaging.python.org/)
2. Review [GitHub Actions documentation](https://docs.github.com/en/actions)
3. Check existing issues in the repository
4. Create a new issue with detailed information
