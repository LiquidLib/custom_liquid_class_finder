#!/usr/bin/env python3
"""
Test script to demonstrate improved parameter bounds for different pipette and liquid combinations
"""

import sys
import os

# Add the project root to the path so we can import from protocols
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from protocols.optimization_strategies import OptimizationStrategy  # noqa: E402


def test_parameter_bounds():
    """Test parameter bounds for different pipette and liquid combinations"""

    print("=" * 80)
    print("PARAMETER BOUNDS ANALYSIS")
    print("=" * 80)

    # Test different pipette types
    pipette_types = ["P20", "P50", "P300", "P1000"]
    liquid_types = ["WATER", "DMSO", "ETHANOL", "GLYCEROL_99", "PEG_8000_50"]

    print("\n📊 PIPETTE-SPECIFIC BOUNDS:")
    print("-" * 50)

    for pipette in pipette_types:
        print(f"\n🔧 {pipette} Pipette:")
        print("-" * 30)

        # Test with water (baseline)
        bounds = OptimizationStrategy.calculate_pipette_specific_bounds(pipette, "WATER")

        print("Parameter Bounds (min - max):")
        for param, (min_val, max_val) in bounds.items():
            print(f"  {param:25}: {min_val:6.1f} - {max_val:6.1f}")

    print("\n" + "=" * 80)
    print("LIQUID-SPECIFIC DELAY BOUNDS:")
    print("-" * 50)

    for liquid in liquid_types:
        print(f"\n💧 {liquid}:")
        print("-" * 20)

        # Test with P1000 (most common)
        bounds = OptimizationStrategy.calculate_pipette_specific_bounds("P1000", liquid)

        print("Delay Bounds:")
        print(
            f"  aspiration_delay: {bounds['aspiration_delay'][0]:.1f} - "
            f"{bounds['aspiration_delay'][1]:.1f} seconds"
        )
        print(
            f"  dispense_delay:   {bounds['dispense_delay'][0]:.1f} - "
            f"{bounds['dispense_delay'][1]:.1f} seconds"
        )

        # Show reasoning
        if liquid in ["DMSO", "ETHANOL"]:
            print("  → Volatile liquid: Shorter delays to minimize evaporation")
        elif liquid in ["GLYCEROL_99", "PEG_8000_50"]:
            print("  → Viscous liquid: Longer delays allowed for better handling")
        else:
            print("  → Standard liquid: Normal delay range")

    print("\n" + "=" * 80)
    print("COMPARISON WITH OLD BOUNDS:")
    print("-" * 50)

    # Show old vs new bounds for P1000 with water
    old_bounds = {
        "aspiration_rate": (10.0, 500.0),
        "aspiration_delay": (0.0, 5.0),
        "aspiration_withdrawal_rate": (1.0, 20.0),
        "dispense_rate": (10.0, 500.0),
        "dispense_delay": (0.0, 5.0),
        "blowout_rate": (10.0, 300.0),
    }

    new_bounds = OptimizationStrategy.calculate_pipette_specific_bounds("P1000", "WATER")

    print("\nP1000 with WATER - Old vs New Bounds:")
    print("Parameter          | Old Bounds        | New Bounds        | Improvement")
    print("-" * 75)

    for param in old_bounds.keys():
        old_min, old_max = old_bounds[param]
        new_min, new_max = new_bounds[param]

        # Calculate improvement
        old_range = old_max - old_min
        new_range = new_max - new_min
        improvement = ((old_range - new_range) / old_range) * 100

        print(
            f"{param:18} | {old_min:6.1f} - {old_max:6.1f} | {new_min:6.1f} - "
            f"{new_max:6.1f} | {improvement:+5.1f}%"
        )

    print("\n" + "=" * 80)
    print("RECOMMENDATIONS:")
    print("-" * 50)

    print("✅ IMPROVEMENTS:")
    print("• Pipette-specific bounds prevent unrealistic parameter exploration")
    print("• Liquid-specific delay bounds account for volatility/viscosity")
    print("• Tighter bounds lead to faster convergence and better results")
    print("• More realistic parameter ranges for actual liquid handling")

    print("\n⚠️  CONSIDERATIONS:")
    print("• P20 bounds are much tighter (1-20 μL/sec vs 10-500 μL/sec)")
    print("• Volatile liquids have shorter delay limits (0-1s vs 0-5s)")
    print("• Viscous liquids allow longer delays (0-3s) for better handling")
    print("• Blowout rates are more conservative to prevent splashing")

    print("\n🎯 BENEFITS:")
    print("• Faster optimization convergence")
    print("• More realistic parameter combinations")
    print("• Better handling of different liquid types")
    print("• Reduced risk of parameter combinations that don't work")


if __name__ == "__main__":
    test_parameter_bounds()
