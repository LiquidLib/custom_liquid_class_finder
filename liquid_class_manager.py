#!/usr/bin/env python3
"""
Liquid Class Manager CLI - Entry Point

This is a wrapper script that calls the main liquid class manager functionality
from the liquids package. This provides a convenient entry point for users
while keeping the main functionality organized in the package.

Usage:
    python liquid_class_manager.py list
    python liquid_class_manager.py show P1000 "Glycerol 99%"
    python liquid_class_manager.py export output.csv
    python liquid_class_manager.py import input.csv
    python liquid_class_manager.py add
"""

import os
import sys

if __name__ == "__main__":
    # Add the current directory to the Python path before importing
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    try:
        from liquids.liquid_class_manager import main

        main()
    except ImportError:
        print("Error: Could not import liquid_class_manager from liquids package")
        print("Make sure you're running this from the project root directory")
        sys.exit(1)
