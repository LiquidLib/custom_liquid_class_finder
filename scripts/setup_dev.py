#!/usr/bin/env python3
"""
Development environment setup script for Liquid Class Finder
"""
import os
import sys
import subprocess
import venv
from pathlib import Path


def run_command(cmd, check=True, shell=True):
    """Run a shell command and handle errors"""
    print(f"Running: {cmd}")
    try:
        result = subprocess.run(cmd, shell=shell, check=check, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        if check:
            sys.exit(1)
        return e


def setup_development_environment():
    """Set up the complete development environment"""
    print("🚀 Setting up Liquid Class Finder development environment...")

    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)

    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")

    # Create virtual environment
    venv_path = Path(".venv")
    if not venv_path.exists():
        print("📦 Creating virtual environment...")
        venv.create(".venv", with_pip=True)
        print("✅ Virtual environment created")
    else:
        print("✅ Virtual environment already exists")

    # Determine activation script
    if os.name == "nt":  # Windows
        pip_path = ".venv/Scripts/pip"
        python_path = ".venv/Scripts/python"
    else:  # Unix/Linux/macOS
        pip_path = ".venv/bin/pip"
        python_path = ".venv/bin/python"

    # Upgrade pip
    print("⬆️  Upgrading pip...")
    run_command(f"{pip_path} install --upgrade pip")

    # Install dependencies
    print("📦 Installing dependencies...")
    run_command(f"{pip_path} install -e '.[dev]'")

    # Install pre-commit hooks
    print("🔧 Installing pre-commit hooks...")
    run_command(f"{python_path} -m pre_commit install")

    print("\n🎉 Development environment setup complete!")
    print("\nNext steps:")
    print("1. Activate the virtual environment:")
    if os.name == "nt":
        print("   .venv\\Scripts\\activate")
    else:
        print("   source .venv/bin/activate")
    print("2. Run tests: make test")
    print("3. Check code quality: make check")
    print("4. Start developing!")


if __name__ == "__main__":
    setup_development_environment()
