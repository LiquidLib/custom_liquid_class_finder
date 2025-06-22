# Development Guide

This document provides detailed information for developers working on the Liquid Class Finder project.

## Table of Contents

- [Environment Setup](#environment-setup)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Testing Strategy](#testing-strategy)
- [Code Quality](#code-quality)
- [Debugging](#debugging)
- [Contributing](#contributing)

## Environment Setup

### Prerequisites

- **Python 3.8+**: Required for modern type hints and features
- **Git**: For version control
- **Opentrons App**: For protocol testing and simulation

### Automated Setup

The easiest way to set up the development environment:

```bash
# Clone the repository
git clone https://github.com/LiquidLib/custom_liquid_class_finder.git
cd custom_liquid_class_finder

# Run automated setup
python scripts/setup_dev.py
```

### Manual Setup

If you prefer manual setup:

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # Unix/macOS
# or
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Verification

After setup, verify everything works:

```bash
# Run all checks
make check

# Run tests
make test

# Check formatting
make format-check
```

## Project Structure

```
liquid-class-finder/
├── protocol.py              # Main Opentrons protocol
├── requirements.txt         # Production dependencies
├── pyproject.toml          # Project configuration
├── Makefile                # Development commands
├── .pre-commit-config.yaml # Pre-commit hooks
├── .gitignore             # Git ignore patterns
├── scripts/               # Development scripts
│   └── setup_dev.py       # Environment setup
├── config/                # Configuration files
│   └── example_config.json
├── tests/                 # Test suite
│   ├── __init__.py
│   └── test_protocol.py
├── docs/                  # Documentation
│   └── DEVELOPMENT.md     # This file
└── README.md              # Project overview
```

## Development Workflow

### 1. Starting Development

```bash
# Ensure you're on the main branch
git checkout main
git pull origin main

# Create a feature branch
git checkout -b feature/your-feature-name
```

### 2. Making Changes

1. **Edit code** following the style guidelines
2. **Add tests** for new functionality
3. **Update documentation** as needed
4. **Run checks** before committing:

```bash
make check
```

### 3. Committing Changes

```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "Add feature: brief description"

# Push to remote
git push origin feature/your-feature-name
```

### 4. Creating Pull Requests

1. Go to GitHub and create a pull request
2. Ensure all CI checks pass
3. Request review from maintainers
4. Address feedback and merge

## Testing Strategy

### Test Structure

Tests are organized in the `tests/` directory:

- **Unit tests**: Test individual functions and components
- **Integration tests**: Test protocol workflow
- **Mock tests**: Test Opentrons API interactions

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_protocol.py

# Run with verbose output
pytest -v

# Run tests in parallel
pytest -n auto
```

### Writing Tests

Follow these guidelines:

1. **Test naming**: Use descriptive test names
2. **Test isolation**: Each test should be independent
3. **Mocking**: Use mocks for external dependencies
4. **Coverage**: Aim for >90% code coverage

Example test:

```python
def test_parameter_constraints():
    """Test that parameters are properly constrained"""
    params = {'aspiration_rate': 1000}  # Out of bounds
    constrained = apply_constraints(params)
    assert constrained['aspiration_rate'] == 500  # Max bound
```

## Code Quality

### Style Guidelines

- **Black**: Automatic code formatting
- **flake8**: Linting with specific exceptions
- **mypy**: Static type checking
- **Docstrings**: Google-style for functions and classes

### Pre-commit Hooks

Hooks run automatically on commit:

- **Trailing whitespace removal**
- **End-of-file fixer**
- **YAML validation**
- **Code formatting**
- **Linting**
- **Type checking**

### Manual Quality Checks

```bash
# Format code
make format

# Check formatting
make format-check

# Run linting
make lint

# Run all checks
make check
```

## Debugging

### Protocol Debugging

1. **Use Opentrons App**:
   - Load protocol in simulation mode
   - Step through execution
   - Check labware positioning

2. **Add debug comments**:
   ```python
   protocol.comment(f"Debug: Current parameters: {params}")
   ```

3. **Use logging**:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

### Test Debugging

```bash
# Run specific test with debug output
pytest tests/test_protocol.py::test_specific_function -v -s

# Run with pdb debugger
pytest --pdb

# Run with coverage for specific file
pytest --cov=protocol --cov-report=term-missing
```

### Common Issues

1. **Import errors**: Ensure virtual environment is activated
2. **Opentrons API changes**: Check API version compatibility
3. **Test failures**: Verify mock objects are properly configured

## Contributing

### Before Contributing

1. **Read the documentation**
2. **Check existing issues** and pull requests
3. **Discuss major changes** in an issue first

### Contribution Guidelines

1. **Follow the code style** (Black + flake8)
2. **Add tests** for new functionality
3. **Update documentation** as needed
4. **Use descriptive commit messages**
5. **Keep changes focused** and small

### Commit Message Format

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Maintenance tasks

Examples:
```
feat(optimization): add new gradient descent algorithm
fix(protocol): correct parameter bounds validation
docs(readme): add development setup instructions
```

### Pull Request Process

1. **Create feature branch** from main
2. **Make focused changes** with clear commit messages
3. **Add tests** for new functionality
4. **Update documentation** as needed
5. **Run all checks** locally
6. **Create pull request** with clear description
7. **Address review feedback**
8. **Merge after approval**

### Code Review Checklist

- [ ] Code follows style guidelines
- [ ] Tests are included and pass
- [ ] Documentation is updated
- [ ] No breaking changes (or documented)
- [ ] Performance impact considered
- [ ] Security implications reviewed

## Advanced Topics

### Custom Liquid Types

To add support for new liquid types:

1. **Define liquid properties** in the protocol
2. **Adjust parameter bounds** for the liquid
3. **Add evaluation metrics** specific to the liquid
4. **Update tests** to cover new functionality

### Optimization Algorithms

The current implementation uses gradient descent. To add new algorithms:

1. **Implement algorithm** in separate module
2. **Create interface** for algorithm selection
3. **Add configuration** for algorithm parameters
4. **Update tests** for new algorithms

### Performance Optimization

- **Profile code** using cProfile
- **Optimize critical paths** in parameter adjustment
- **Use efficient data structures** for large datasets
- **Consider parallel processing** for independent operations

## Support

For development questions:

1. **Check documentation** first
2. **Search existing issues**
3. **Create new issue** with detailed description
4. **Join community discussions**

## License

This project is licensed under the MIT License. See LICENSE file for details.
