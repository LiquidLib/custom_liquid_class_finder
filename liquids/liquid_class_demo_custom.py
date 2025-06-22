#!/usr/bin/env python3
"""
Liquid Class Demo Script

This script demonstrates how to use the liquid class configuration system
with the reference data provided by the user.
"""

from .liquid_classes import (
    LiquidClassParams,
    PipetteType,
    LiquidType,
    liquid_class_registry,
    get_liquid_class_params,
    export_liquid_classes_csv,
    import_liquid_classes_from_csv,
)


def demo_basic_usage():
    """Demonstrate basic usage of the liquid class system"""
    print("=== Liquid Class Demo ===\n")

    # 1. Show the reference liquid class that was loaded
    print("1. Reference Liquid Class (from your data):")
    glycerol_params = get_liquid_class_params(PipetteType.P1000, LiquidType.GLYCEROL_99)
    if glycerol_params:
        print(f"   Pipette: {glycerol_params.pipette.value}")
        print(f"   Liquid: {glycerol_params.liquid.value}")
        print(f"   Aspiration Rate: {glycerol_params.aspiration_rate} µL/s")
        print(f"   Aspiration Delay: {glycerol_params.aspiration_delay} s")
        print(f"   Aspiration Withdrawal Rate: {glycerol_params.aspiration_withdrawal_rate} mm/s")
        print(f"   Dispense Rate: {glycerol_params.dispense_rate} µL/s")
        print(f"   Dispense Delay: {glycerol_params.dispense_delay} s")
        print(f"   Blowout Rate: {glycerol_params.blowout_rate} µL/s")
        print(f"   Touch Tip: {glycerol_params.touch_tip}")
        print()

    # 2. Show all available liquid classes
    print("2. All Available Liquid Classes:")
    all_classes = liquid_class_registry.list_liquid_classes()
    for key, liquid_class in all_classes.items():
        print(f"   {key}: {liquid_class}")
    print()

    # 3. Export to CSV format
    print("3. Export to CSV Format:")
    csv_data = export_liquid_classes_csv()
    print(csv_data)
    print()


def demo_csv_import():
    """Demonstrate importing liquid classes from CSV"""
    print("=== CSV Import Demo ===\n")

    # Your reference data in CSV format
    reference_csv = (
        "Pipette,Liquid,Aspiration Rate (µL/s),Aspiration Delay (s),"
        "Aspiration Withdrawal Rate (mm/s),Dispense Rate (µL/s),Dispense Delay (s),"
        "Blowout Rate (µL/s),Touch tip\n"
        "P1000,Glycerol 99%,41.175,20,4,19.215,20,5.0,No"
    )

    print("1. Importing from CSV:")
    print(reference_csv)
    print()

    # Import the CSV data
    import_liquid_classes_from_csv(reference_csv)

    # Verify it was imported correctly
    print("2. Verification - Retrieved liquid class:")
    glycerol_params = get_liquid_class_params(PipetteType.P1000, LiquidType.GLYCEROL_99)
    if glycerol_params:
        print(f"   Aspiration Rate: {glycerol_params.aspiration_rate} µL/s")
        print(f"   Dispense Rate: {glycerol_params.dispense_rate} µL/s")
        print(f"   Touch Tip: {glycerol_params.touch_tip}")
    print()


def demo_protocol_integration():
    """Demonstrate how to integrate with the protocol"""
    print("=== Protocol Integration Demo ===\n")

    # Get the liquid class parameters
    glycerol_params = get_liquid_class_params(PipetteType.P1000, LiquidType.GLYCEROL_99)

    if glycerol_params:
        print("1. Liquid class parameters for protocol use:")
        protocol_params = glycerol_params.to_dict()
        for key, value in protocol_params.items():
            print(f"   {key}: {value}")
        print()

        print("2. Example protocol integration:")
        print("   # In your protocol:")
        print(
            "   liquid_params = get_liquid_class_params(PipetteType.P1000, LiquidType.GLYCEROL_99)"
        )
        print("   if liquid_params:")
        print("       params = liquid_params.to_dict()")
        print("       pipette.flow_rate.aspirate = params['aspiration_rate']")
        print("       pipette.flow_rate.dispense = params['dispense_rate']")
        print("       pipette.flow_rate.blow_out = params['blowout_rate']")
        print()


def demo_adding_new_liquid_class():
    """Demonstrate adding a new liquid class"""
    print("=== Adding New Liquid Class Demo ===\n")

    # Create a new liquid class for DMSO with P300 pipette
    dmso_p300 = LiquidClassParams(
        pipette=PipetteType.P300,
        liquid=LiquidType.DMSO,
        aspiration_rate=75.0,
        aspiration_delay=2.0,
        aspiration_withdrawal_rate=3.0,
        dispense_rate=75.0,
        dispense_delay=2.0,
        blowout_rate=50.0,
        touch_tip=True,
    )

    print("1. Adding new liquid class:")
    print(f"   {dmso_p300}")
    print()

    # Add to registry
    liquid_class_registry.add_liquid_class(dmso_p300)

    # Verify it was added
    print("2. Verification - Retrieved new liquid class:")
    retrieved_params = get_liquid_class_params(PipetteType.P300, LiquidType.DMSO)
    if retrieved_params:
        print(f"   Aspiration Rate: {retrieved_params.aspiration_rate} µL/s")
        print(f"   Dispense Rate: {retrieved_params.dispense_rate} µL/s")
        print(f"   Touch Tip: {retrieved_params.touch_tip}")
    print()

    # Show updated CSV export
    print("3. Updated CSV export:")
    updated_csv = export_liquid_classes_csv()
    print(updated_csv)


def main():
    """Run all demos"""
    try:
        demo_basic_usage()
        demo_csv_import()
        demo_protocol_integration()
        demo_adding_new_liquid_class()

        print("=== Demo Completed Successfully ===")

    except Exception as e:
        print(f"Error during demo: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
