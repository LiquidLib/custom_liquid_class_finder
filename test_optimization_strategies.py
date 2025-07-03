#!/usr/bin/env python3
"""
Test script to demonstrate the different optimization strategies
"""

import sys
import os

# Add the protocols directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "protocols"))  # noqa: E402

from optimization_strategies import OptimizationStrategyFactory  # noqa: E402


def test_optimization_strategies():
    """Test all optimization strategies with sample data"""

    # Sample reference parameters
    reference_params = {
        "aspiration_rate": 150.0,
        "aspiration_delay": 1.0,
        "aspiration_withdrawal_rate": 5.0,
        "dispense_rate": 150.0,
        "dispense_delay": 1.0,
        "blowout_rate": 100.0,
    }

    # Parameter bounds
    param_bounds = {
        "aspiration_rate": (10.0, 500.0),
        "aspiration_delay": (0.0, 5.0),
        "aspiration_withdrawal_rate": (1.0, 20.0),
        "dispense_rate": (10.0, 500.0),
        "dispense_delay": (0.0, 5.0),
        "blowout_rate": (10.0, 300.0),
    }

    # Test different sample counts for hybrid strategy
    sample_counts = [8, 24, 48, 96]

    # Sample well data (simulating previous results)
    sample_well_data = [
        {
            "well_id": "A1",
            "well_index": 0,
            "parameters": reference_params.copy(),
            "height_status": True,
            "bubblicity_score": 2.5,
        },
        {
            "well_id": "A2",
            "well_index": 1,
            "parameters": {
                "aspiration_rate": 140.0,
                "aspiration_delay": 1.1,
                "aspiration_withdrawal_rate": 5.2,
                "dispense_rate": 145.0,
                "dispense_delay": 1.05,
                "blowout_rate": 95.0,
            },
            "height_status": True,
            "bubblicity_score": 2.1,
        },
    ]

    # Test hybrid strategy with different sample counts
    print("=" * 80)
    print("HYBRID STRATEGY - PROPORTIONAL ALLOCATION")
    print("=" * 80)

    for sample_count in sample_counts:
        print(f"\n📊 Sample Count: {sample_count}")
        print("-" * 30)

        try:
            # Create hybrid strategy with specific sample count
            strategy = OptimizationStrategyFactory.create_strategy(
                "hybrid", reference_params, param_bounds, sample_count
            )

            print(f"Strategy: {strategy.get_strategy_name()}")
            print(f"Description: {strategy.get_strategy_description()}")

            # Show phase allocation
            phase_configs = getattr(strategy, "phase_configs", None)
            if phase_configs:
                print("\nPhase Allocation:")
                total_wells = 0
                for phase_name, config in phase_configs.items():
                    wells = config["wells_per_phase"]
                    total_wells += wells
                    percentage = (wells / sample_count) * 100
                    print(
                        f"  {phase_name:12}: {wells:2d} wells ({percentage:5.1f}%) - "
                        f"{config['description']}"
                    )
                print(f"  {'Total':12}: {total_wells:2d} wells")

        except Exception as e:
            print(f"❌ Error testing hybrid strategy with {sample_count} samples: {e}")

    # Test all strategies with default sample count
    strategies = OptimizationStrategyFactory.get_available_strategies()

    print("\n" + "=" * 80)
    print("ALL STRATEGIES COMPARISON (96 samples)")
    print("=" * 80)

    for strategy_name in strategies:
        print(f"\n🔧 Testing Strategy: {strategy_name.upper()}")
        print("-" * 50)

        try:
            # Create strategy
            strategy = OptimizationStrategyFactory.create_strategy(
                strategy_name, reference_params, param_bounds, 96
            )

            print(f"Strategy Name: {strategy.get_strategy_name()}")
            print(f"Description: {strategy.get_strategy_description()}")

            # Test parameter generation for different wells
            learning_rate = 0.1

            print("\nParameter Generation Test:")
            print("Well | Parameters Generated")
            print("-----|-------------------")

            for well_idx in range(5):
                params = strategy.generate_parameters(well_idx, sample_well_data, learning_rate)

                # Show key parameters
                key_params = {
                    "asp_rate": params["aspiration_rate"],
                    "asp_delay": params["aspiration_delay"],
                    "disp_rate": params["dispense_rate"],
                    "disp_delay": params["dispense_delay"],
                    "blowout": params["blowout_rate"],
                }

                print(f"{well_idx:4d} | {key_params}")

                # Simulate a result and record it
                simulated_score = 2.0 + (well_idx * 0.1)  # Decreasing score
                strategy.record_result(well_idx, params, simulated_score, True, learning_rate)

            # Show strategy statistics
            print("\nStrategy Statistics:")
            print(f"  Best score achieved: {strategy.best_score:.3f}")
            print(f"  Iterations recorded: {len(strategy.optimization_history)}")

            # Show phase information for hybrid strategy
            if hasattr(strategy, "current_phase"):
                print(f"  Current phase: {strategy.current_phase}")

        except Exception as e:
            print(f"❌ Error testing strategy {strategy_name}: {e}")

    print("\n" + "=" * 80)
    print("COMPARISON SUMMARY")
    print("=" * 80)

    print("\nStrategy Characteristics:")
    print("1. SIMULTANEOUS: Optimizes all 6 parameters at once using gradient descent")
    print("   - Pros: Captures parameter interactions, efficient for smooth landscapes")
    print("   - Cons: May get stuck in local minima, requires more data per iteration")

    print("\n2. HYBRID: Hierarchical optimization in phases")
    print("   - Phase 1: Flow rates (3 params, 24 wells)")
    print("   - Phase 2: Delays (2 params, 24 wells)")
    print("   - Phase 3: Withdrawal rate (1 param, 12 wells)")
    print("   - Phase 4: Fine-tuning (6 params, 36 wells)")
    print("   - Pros: Systematic approach, good for complex landscapes")
    print("   - Cons: May miss global optima, longer total runtime")

    print("\n3. COORDINATE: Optimizes one parameter at a time")
    print("   - Pros: Simple, robust, good for high-dimensional spaces")
    print("   - Cons: May converge slowly, doesn't capture interactions")

    print("\n" + "=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    print("• Use SIMULTANEOUS for well-behaved liquid types (water, simple buffers)")
    print("• Use HYBRID for complex liquids (viscous, volatile, multi-component)")
    print("• Use COORDINATE for initial exploration or when computational budget is limited")


if __name__ == "__main__":
    test_optimization_strategies()
