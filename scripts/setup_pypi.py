#!/usr/bin/env python3
"""
Setup script for PyPI publishing preparation.
This script helps validate the package before publishing.
"""

import sys
import subprocess
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Command: {cmd}")
        print(f"Error: {e.stderr}")
        return False


def check_file_exists(filepath, description):
    """Check if a file exists."""
    if Path(filepath).exists():
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description} missing: {filepath}")
        return False


def main():
    """Main setup function."""
    print("🚀 PyPI Publishing Setup")
    print("=" * 50)

    # Check required files
    required_files = [
        ("pyproject.toml", "Package configuration"),
        ("README.md", "Package documentation"),
        ("LICENSE", "License file"),
        ("CHANGELOG.md", "Changelog"),
        ("MANIFEST.in", "Package manifest"),
        ("liquids/__init__.py", "Package init file"),
    ]

    all_files_exist = True
    for filepath, description in required_files:
        if not check_file_exists(filepath, description):
            all_files_exist = False

    if not all_files_exist:
        print("\n❌ Some required files are missing. Please create them before publishing.")
        sys.exit(1)

    # Run quality checks
    checks_passed = True

    # Check code formatting
    if not run_command("black --check .", "Code formatting check"):
        checks_passed = False

    # Check linting
    if not run_command("flake8 --max-line-length=100 --extend-ignore=E203,W503 .", "Linting check"):
        checks_passed = False

    # Check type hints
    if not run_command("mypy --ignore-missing-imports .", "Type checking"):
        checks_passed = False

    # Run tests
    if not run_command("pytest --cov=liquids --cov-report=term-missing", "Test suite"):
        checks_passed = False

    # Build package
    if not run_command("python -m build", "Package build"):
        checks_passed = False

    # Check package
    if not run_command("twine check dist/*", "Package validation"):
        checks_passed = False

    if checks_passed:
        print("\n🎉 All checks passed! Package is ready for publishing.")
        print("\n📦 To publish to TestPyPI:")
        print("   twine upload --repository testpypi dist/*")
        print("\n📦 To publish to PyPI:")
        print("   twine upload dist/*")
    else:
        print("\n❌ Some checks failed. Please fix the issues before publishing.")
        sys.exit(1)


if __name__ == "__main__":
    main()
