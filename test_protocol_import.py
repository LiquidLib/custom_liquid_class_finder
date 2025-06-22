#!/usr/bin/env python3
"""
Test script to verify protocol imports work correctly
"""

import sys
import os

# Simulate the protocol's import approach
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from liquid_classes import get_liquid_class_params, PipetteType, LiquidType

    print("✅ Successfully imported liquid_classes module")

    # Test basic functionality
    params = get_liquid_class_params(PipetteType.P1000, LiquidType.GLYCEROL_99)
    if params:
        print("✅ Successfully retrieved glycerol parameters:")
        print(f"   Aspiration Rate: {params.aspiration_rate} µL/s")
        print(f"   Dispense Rate: {params.dispense_rate} µL/s")
    else:
        print("❌ Failed to retrieve glycerol parameters")

except ImportError as e:
    print(f"❌ Import failed: {e}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\nPath information:")
print(f"Current directory: {os.getcwd()}")
print(f"Python path: {sys.path[:3]}...")  # Show first 3 entries
