#!/usr/bin/env python3
"""
Liquid Class Manager

A utility script for managing liquid class parameters, including CSV import/export
and interactive parameter management.
"""

import argparse
import sys

from liquid_classes import (
    LiquidClassParams,
    PipetteType,
    LiquidType,
    liquid_class_registry,
    get_liquid_class_params,
    export_liquid_classes_csv,
    import_liquid_classes_from_csv,
    add_liquid_class_params,
)


def load_csv_file(filepath: str) -> str:
    """Load CSV data from file"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file '{filepath}': {e}")
        sys.exit(1)


def save_csv_file(filepath: str, csv_data: str):
    """Save CSV data to file"""
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(csv_data)
        print(f"CSV data saved to '{filepath}'")
    except Exception as e:
        print(f"Error saving file '{filepath}': {e}")
        sys.exit(1)


def list_all_liquid_classes():
    """List all available liquid classes"""
    print("Available Liquid Classes:")
    print("=" * 50)

    all_classes = liquid_class_registry.list_liquid_classes()
    if not all_classes:
        print("No liquid classes found.")
        return

    for key, liquid_class in all_classes.items():
        print(f"\n{key}:")  # noqa: E231
        print(f"  Pipette: {liquid_class.pipette.value}")
        print(f"  Liquid: {liquid_class.liquid.value}")
        print(f"  Aspiration Rate: {liquid_class.aspiration_rate} µL/s")
        print(f"  Aspiration Delay: {liquid_class.aspiration_delay} s")
        print(f"  Aspiration Withdrawal Rate: " f"{liquid_class.aspiration_withdrawal_rate} mm/s")
        print(f"  Dispense Rate: {liquid_class.dispense_rate} µL/s")
        print(f"  Dispense Delay: {liquid_class.dispense_delay} s")
        print(f"  Blowout Rate: {liquid_class.blowout_rate} µL/s")
        print(f"  Touch Tip: {liquid_class.touch_tip}")


def show_liquid_class(pipette: str, liquid: str):
    """Show specific liquid class parameters"""
    try:
        pipette_type = PipetteType(pipette)
        liquid_type = LiquidType(liquid)
    except ValueError as e:
        print(f"Error: {e}")
        print(f"Available pipettes: {[p.value for p in PipetteType]}")
        print(f"Available liquids: {[liquid.value for liquid in LiquidType]}")
        return

    params = get_liquid_class_params(pipette_type, liquid_type)
    if params is None:
        print(f"No liquid class found for {pipette} and {liquid}")
        return

    print(f"Liquid Class Parameters for {pipette} - {liquid}:")  # noqa: E231
    print("=" * 50)
    print(f"Aspiration Rate: {params.aspiration_rate} µL/s")
    print(f"Aspiration Delay: {params.aspiration_delay} s")
    print(f"Aspiration Withdrawal Rate: " f"{params.aspiration_withdrawal_rate} mm/s")
    print(f"Dispense Rate: {params.dispense_rate} µL/s")
    print(f"Dispense Delay: {params.dispense_delay} s")
    print(f"Blowout Rate: {params.blowout_rate} µL/s")
    print(f"Touch Tip: {params.touch_tip}")


def add_liquid_class_interactive():
    """Add a new liquid class interactively"""
    print("Add New Liquid Class")
    print("=" * 30)

    # Get pipette type
    print("Available pipettes:")
    for i, pipette in enumerate(PipetteType, 1):
        print(f"  {i}. {pipette.value}")

    try:
        pipette_choice = int(input("Select pipette (1-3): ")) - 1
        pipette_type = list(PipetteType)[pipette_choice]
    except (ValueError, IndexError):
        print("Invalid pipette selection")
        return

    # Get liquid type
    print("\nAvailable liquids:")
    for i, liquid in enumerate(LiquidType, 1):
        print(f"  {i}. {liquid.value}")

    try:
        liquid_choice = int(input("Select liquid (1-4): ")) - 1
        liquid_type = list(LiquidType)[liquid_choice]
    except (ValueError, IndexError):
        print("Invalid liquid selection")
        return

    # Get parameters
    print("\nEnter parameters:")
    try:
        aspiration_rate = float(input("Aspiration Rate (µL/s): "))
        aspiration_delay = float(input("Aspiration Delay (s): "))
        aspiration_withdrawal_rate = float(input("Aspiration Withdrawal Rate (mm/s): "))
        dispense_rate = float(input("Dispense Rate (µL/s): "))
        dispense_delay = float(input("Dispense Delay (s): "))
        blowout_rate = float(input("Blowout Rate (µL/s): "))
        touch_tip_input = input("Touch Tip (y/n): ").lower()
        touch_tip = touch_tip_input in ["y", "yes", "true"]
    except ValueError:
        print("Invalid numeric input")
        return

    # Create and add liquid class
    new_params = LiquidClassParams(
        pipette=pipette_type,
        liquid=liquid_type,
        aspiration_rate=aspiration_rate,
        aspiration_delay=aspiration_delay,
        aspiration_withdrawal_rate=aspiration_withdrawal_rate,
        dispense_rate=dispense_rate,
        dispense_delay=dispense_delay,
        blowout_rate=blowout_rate,
        touch_tip=touch_tip,
    )

    add_liquid_class_params(new_params)
    print(f"\nLiquid class added successfully: " f"{pipette_type.value} - {liquid_type.value}")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Liquid Class Manager - Manage liquid handling parameters",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s list                                    # List all liquid classes
  %(prog)s show P1000 "Glycerol 99%"              # Show specific liquid class
  %(prog)s export output.csv                      # Export to CSV file
  %(prog)s import input.csv                       # Import from CSV file
  %(prog)s add                                     # Add new liquid class interactively
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # List command
    subparsers.add_parser("list", help="List all liquid classes")

    # Show command
    show_parser = subparsers.add_parser("show", help="Show specific liquid class")
    show_parser.add_argument("pipette", help="Pipette type (e.g., P1000)")
    show_parser.add_argument("liquid", help='Liquid type (e.g., "Glycerol 99%")')

    # Export command
    export_parser = subparsers.add_parser("export", help="Export liquid classes to CSV")
    export_parser.add_argument("filepath", help="Output CSV file path")

    # Import command
    import_parser = subparsers.add_parser("import", help="Import liquid classes from CSV")
    import_parser.add_argument("filepath", help="Input CSV file path")

    # Add command
    subparsers.add_parser("add", help="Add new liquid class interactively")

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Execute command
    if args.command == "list":
        list_all_liquid_classes()

    elif args.command == "show":
        show_liquid_class(args.pipette, args.liquid)

    elif args.command == "export":
        csv_data = export_liquid_classes_csv()
        save_csv_file(args.filepath, csv_data)

    elif args.command == "import":
        csv_data = load_csv_file(args.filepath)
        try:
            import_liquid_classes_from_csv(csv_data)
            print(f"Successfully imported liquid classes from " f"'{args.filepath}'")
        except Exception as e:
            print(f"Error importing CSV: {e}")
            sys.exit(1)

    elif args.command == "add":
        add_liquid_class_interactive()


if __name__ == "__main__":
    main()
