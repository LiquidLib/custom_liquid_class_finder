#!/usr/bin/env python3
"""
Demonstration of the Liquid Class System with Default Classes
"""

from liquid_classes import (
    liquid_class_registry,
    PipetteType,
    LiquidType,
    get_liquid_class_params,
    export_liquid_classes_csv,
)


def demo_liquid_class_usage():
    """Demonstrate how to use the liquid class system"""

    print("=== Liquid Class System Demonstration ===\n")

    # Example 1: Get parameters for P300 with Glycerol 99%
    print("Example 1: P300 with Glycerol 99%")
    print("-" * 40)
    params = get_liquid_class_params(PipetteType.P300, LiquidType.GLYCEROL_99)
    if params:
        print(f"Aspiration Rate: {params.aspiration_rate} µL/s")
        print(f"Aspiration Delay: {params.aspiration_delay} s")
        print(f"Dispense Rate: {params.dispense_rate} µL/s")
        print(f"Touch Tip: {'Yes' if params.touch_tip else 'No'}")
        print(f"Parameters dict: {params.to_dict()}")
    print()

    # Example 2: Get parameters for P20 with Sanitizer
    print("Example 2: P20 with Sanitizer 62% Alcohol")
    print("-" * 40)
    params = get_liquid_class_params(PipetteType.P20, LiquidType.SANITIZER_62_ALCOHOL)
    if params:
        print(f"Aspiration Rate: {params.aspiration_rate} µL/s")
        print(f"Aspiration Withdrawal Rate: {params.aspiration_withdrawal_rate} mm/s")
        print(f"Dispense Rate: {params.dispense_rate} µL/s")
        print(f"Touch Tip: {'Yes' if params.touch_tip else 'No'}")
    print()

    # Example 3: List all available liquid classes
    print("Example 3: All Available Liquid Classes")
    print("-" * 40)
    all_classes = liquid_class_registry.list_liquid_classes()

    # Group by pipette type
    pipette_groups = {}
    for key, liquid_class in all_classes.items():
        pipette = liquid_class.pipette.value
        if pipette not in pipette_groups:
            pipette_groups[pipette] = []
        pipette_groups[pipette].append(liquid_class.liquid.value)

    for pipette, liquids in pipette_groups.items():
        print(f"{pipette}: {len(liquids)} liquid classes")
        for liquid in sorted(liquids):
            print(f"  - {liquid}")  # noqa: E221
        print()

    # Example 4: Show CSV export
    print("Example 4: CSV Export (first 3 lines)")
    print("-" * 40)
    csv_data = export_liquid_classes_csv()
    lines = csv_data.split("\n")
    for i, line in enumerate(lines[:4]):  # Header + 3 data lines
        print(line)
    print("...")


def demo_protocol_integration():
    """Show how liquid classes would be used in a protocol"""

    print("\n=== Protocol Integration Example ===")
    print("How to use liquid classes in an Opentrons protocol:")
    print("-" * 50)

    # Example protocol snippet
    protocol_code = """
# Example Opentrons protocol using liquid classes
from liquid_classes import get_liquid_class_params, PipetteType, LiquidType

def run(protocol):
    # Get liquid class parameters
    liquid_params = get_liquid_class_params(
        PipetteType.P300,
        LiquidType.GLYCEROL_99
    )

    if liquid_params:
        # Configure pipette with liquid class parameters
        pipette = protocol.load_instrument('p300_single', 'right')

        # Apply liquid class settings
        pipette.flow_rate.aspirate = liquid_params.aspiration_rate
        pipette.flow_rate.dispense = liquid_params.dispense_rate

        # Use in transfer operations
        pipette.transfer(
            volume=50,
            source=source_plate['A1'],
            dest=dest_plate['A1'],
            touch_tip=liquid_params.touch_tip,
            blow_out=True,
            blowout_location='destination well'
        )
    """

    print(protocol_code)


if __name__ == "__main__":
    demo_liquid_class_usage()
    demo_protocol_integration()
