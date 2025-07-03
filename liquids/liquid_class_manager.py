#!/usr/bin/env python3
"""
Liquid Class Manager CLI

A standalone command-line interface for managing liquid class parameters.
This script can be run directly without installation.

Usage:
    python liquid_class_manager.py list
    python liquid_class_manager.py show P1000 "Glycerol 99%"
    python liquid_class_manager.py export output.csv
    python liquid_class_manager.py import input.csv
    python liquid_class_manager.py add
"""

import argparse
import os
import sys

# Add the current directory to the Python path so we can import from liquids
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from liquids.liquid_classes import (
        LiquidClassParams,
        PipetteType,
        LiquidType,
        liquid_class_registry,
        get_liquid_class_params,
        export_liquid_classes_csv,
        import_liquid_classes_from_csv,
        add_liquid_class_params,
        remove_liquid_class_params,
    )
except ImportError:
    print("Error: Could not import liquid_classes module")
    sys.exit(1)

CSV_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "liquid_classes.csv")


def auto_load_registry():
    if os.path.exists(CSV_PATH):
        try:
            with open(CSV_PATH, "r", encoding="utf-8") as f:
                csv_data = f.read()
            import_liquid_classes_from_csv(csv_data)
        except Exception as e:
            print(f"Warning: Could not auto-load liquid classes from CSV: {e}")


def auto_save_registry():
    try:
        csv_data = export_liquid_classes_csv()
        with open(CSV_PATH, "w", encoding="utf-8") as f:
            f.write(csv_data)
    except Exception as e:
        print(f"Warning: Could not auto-save liquid classes to CSV: {e}")


# Auto-load registry at startup
auto_load_registry()


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
        print(f"\n{key}:")
        print(f"  Pipette: {liquid_class.pipette.value}")
        print(f"  Liquid: {liquid_class.liquid.value}")
        print(f"  Aspiration Rate: {liquid_class.aspiration_rate} µL/s")
        print(f"  Aspiration Delay: {liquid_class.aspiration_delay} s")
        print(f"  Aspiration Withdrawal Rate: {liquid_class.aspiration_withdrawal_rate} mm/s")
        print(f"  Dispense Rate: {liquid_class.dispense_rate} µL/s")
        print(f"  Dispense Delay: {liquid_class.dispense_delay} s")
        print(f"  Blowout Rate: {liquid_class.blowout_rate} µL/s")
        print(f"  Touch Tip: {liquid_class.touch_tip}")


def show_liquid_class(pipette: str, liquid: str):
    """Show specific liquid class parameters"""
    try:
        pipette_type = PipetteType(pipette)
        liquid_type = LiquidType(liquid)
        params = get_liquid_class_params(pipette_type, liquid_type)
    except ValueError:
        # Try to find custom liquid in registry (case-insensitive, space-insensitive match)
        key = f"{pipette}_{liquid}"
        params = liquid_class_registry._liquid_classes.get(key)
        if params is None:
            # Try case-insensitive and space-insensitive match
            search_key = key.lower().replace(" ", "")
            for k, v in liquid_class_registry._liquid_classes.items():
                if k.lower().replace(" ", "") == search_key:
                    params = v
                    break
        if params is None:
            print(f"Error: '{liquid}' is not a valid LiquidType or custom liquid in registry")
            print("\nAvailable options:")
            print(f"  Pipettes: {[p.value for p in PipetteType]}")
            print(f"  Liquids: {[liquid.value for liquid in LiquidType]}")
            print("\nUse './liquid_class_manager.py help' for detailed information.")
            return

    if params is None:
        print(f"No liquid class found for {pipette} and {liquid}")
        return

    print(f"Liquid Class Parameters for {pipette} - {liquid}:")
    print("=" * 50)
    print(f"Aspiration Rate: {params.aspiration_rate} µL/s")
    print(f"Aspiration Delay: {params.aspiration_delay} s")
    print(f"Aspiration Withdrawal Rate: {params.aspiration_withdrawal_rate} mm/s")
    print(f"Dispense Rate: {params.dispense_rate} µL/s")
    print(f"Dispense Delay: {params.dispense_delay} s")
    print(f"Blowout Rate: {params.blowout_rate} µL/s")
    print(f"Touch Tip: {params.touch_tip}")


def add_liquid_class_interactive():
    """Add a new liquid class interactively"""
    print("Add New Liquid Class")
    print("=" * 30)

    # Define custom liquid class once
    class CustomLiquid:
        def __init__(self, name):
            self.value = name
            self.name = name.upper().replace(" ", "_").replace("%", "PCT")

    # Get pipette type
    print("Available pipettes:")
    for i, pipette in enumerate(PipetteType, 1):
        print(f"  {i}. {pipette.value}")

    try:
        pipette_choice = int(input("Select pipette (1-4): ")) - 1
        pipette_type = list(PipetteType)[pipette_choice]
    except (ValueError, IndexError):
        print("Invalid pipette selection")
        return

    # Get liquid type - allow custom name or selection from existing
    print("\nLiquid type:")
    print("  Enter a custom liquid name, or select from existing:")

    # Show built-in liquids
    built_in_liquids = list(LiquidType)
    for i, liquid in enumerate(built_in_liquids, 1):
        print(f"  {i}. {liquid.value}")

    # Show custom liquids from registry
    custom_liquids = []
    for key in liquid_class_registry._liquid_classes.keys():
        # Extract liquid name from key (format: "Pipette_Liquid")
        if "_" in key:
            liquid_name = key.split("_", 1)[1]
            # Check if it's not a built-in liquid
            built_in_names = [liquid.value for liquid in LiquidType]
            if liquid_name not in built_in_names and liquid_name not in custom_liquids:
                custom_liquids.append(liquid_name)

    if custom_liquids:
        print("  Custom liquids:")
        for i, liquid in enumerate(sorted(custom_liquids), len(built_in_liquids) + 1):
            print(f"  {i}. {liquid}")

    liquid_input = input("Enter liquid name or number: ").strip()

    # Try to parse as number first
    try:
        liquid_choice = int(liquid_input) - 1
        if 0 <= liquid_choice < len(built_in_liquids):
            liquid_type = built_in_liquids[liquid_choice]
        elif len(built_in_liquids) <= liquid_choice < len(built_in_liquids) + len(custom_liquids):
            custom_index = liquid_choice - len(built_in_liquids)
            liquid_name = sorted(custom_liquids)[custom_index]
            liquid_type = CustomLiquid(liquid_name)
        else:
            print("Invalid liquid selection")
            return
    except ValueError:
        # Treat as custom liquid name
        liquid_type = CustomLiquid(liquid_input)

    # Get parameters
    print(f"\nEnter parameters for {pipette_type.value} - {liquid_type.value}:")
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
    auto_save_registry()
    print(f"\nLiquid class added successfully: {pipette_type.value} - {liquid_type.value}")


def show_available_options():
    """Show detailed help and available options"""
    print("Liquid Class Manager - Available Options")
    print("=" * 50)

    print("\nSUPPORTED PIPETTES:")
    for pipette in PipetteType:
        print(f"  - {pipette.value}")

    print("\nSUPPORTED LIQUIDS:")
    for liquid in LiquidType:
        print(f"  - {liquid.value}")

    # Show custom liquids from registry
    custom_liquids = set()
    for key in liquid_class_registry._liquid_classes.keys():
        if "_" in key:
            liquid_name = key.split("_", 1)[1]
            built_in_names = [liquid.value for liquid in LiquidType]
            if liquid_name not in built_in_names:
                custom_liquids.add(liquid_name)

    if custom_liquids:
        print("\nCUSTOM LIQUIDS:")
        for liquid in sorted(custom_liquids):
            print(f"  - {liquid}")

    print("\nPARAMETER DESCRIPTIONS:")
    print("  - Aspiration Rate: Speed of liquid aspiration (µL/s)")
    print("  - Aspiration Delay: Wait time after aspiration (s)")
    print("  - Aspiration Withdrawal Rate: Speed of tip withdrawal (mm/s)")
    print("  - Dispense Rate: Speed of liquid dispensing (µL/s)")
    print("  - Dispense Delay: Wait time after dispensing (s)")
    print("  - Blowout Rate: Speed of air blowout (µL/s)")
    print("  - Touch Tip: Whether to touch tip to well wall (boolean)")


def delete_liquid_class(pipette: str, liquid: str):
    """Delete a specific liquid class"""
    try:
        pipette_type = PipetteType(pipette)
        liquid_type = LiquidType(liquid)
    except ValueError as e:
        print(f"Error: {e}")
        print("\nAvailable options:")
        print(f"  Pipettes: {[p.value for p in PipetteType]}")
        print(f"  Liquids: {[liquid.value for liquid in LiquidType]}")
        print("\nUse './liquid_class_manager.py help' for detailed information.")
        return

    # Check if liquid class exists
    params = get_liquid_class_params(pipette_type, liquid_type)
    if params is None:
        print(f"No liquid class found for {pipette} and {liquid}")
        return

    # Confirm deletion
    confirm = input(f"Are you sure you want to delete {pipette} - {liquid}? (y/n): ").lower()
    if confirm not in ["y", "yes"]:
        print("Deletion cancelled.")
        return

    # Remove from registry
    success = remove_liquid_class_params(pipette_type, liquid_type)
    if success:
        auto_save_registry()
        print(f"Liquid class {pipette} - {liquid} deleted successfully.")
    else:
        print(f"Failed to delete liquid class {pipette} - {liquid}.")


def get_dynamic_help_text():
    """Generate dynamic help text including custom liquids"""
    # Get all liquids (built-in + custom)
    all_liquids = [liquid.value for liquid in LiquidType]

    # Add custom liquids from registry
    custom_liquids = set()
    for key in liquid_class_registry._liquid_classes.keys():
        if "_" in key:
            liquid_name = key.split("_", 1)[1]
            if liquid_name not in all_liquids:
                custom_liquids.add(liquid_name)

    all_liquids.extend(sorted(custom_liquids))

    # Format the liquids list
    if len(all_liquids) <= 4:
        liquids_text = ", ".join(all_liquids)
    else:
        # Split into multiple lines for readability
        liquids_text = "  " + ",\n  ".join(all_liquids)

    return f"""
EXAMPLES:
  List all liquid classes:
    ./liquid_class_manager.py list

  Show specific liquid class:
    ./liquid_class_manager.py show P1000 "Glycerol 99%"

  Export to CSV file:
    ./liquid_class_manager.py export output.csv

  Import from CSV file:
    ./liquid_class_manager.py import input.csv

  Add new liquid class interactively:
    ./liquid_class_manager.py add

  Delete specific liquid class:
    ./liquid_class_manager.py delete P1000 "Glycerol 99%"

SUPPORTED PIPETTES:
  P20, P300, P1000

SUPPORTED LIQUIDS:
{liquids_text}

For detailed documentation, see CLI_README.md
"""


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Liquid Class Manager - Manage liquid handling parameters",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=get_dynamic_help_text(),
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # List command
    subparsers.add_parser(
        "list",
        help="List all liquid classes",
        description="Display all available liquid classes with their parameters",
    )

    # Show command
    show_parser = subparsers.add_parser(
        "show",
        help="Show specific liquid class",
        description="Display parameters for a specific pipette-liquid combination",
    )
    show_parser.add_argument("pipette", help="Pipette type (P20, P300, P1000)")
    show_parser.add_argument("liquid", help="Liquid type (e.g., Glycerol 99, Water, DMSO)")

    # Export command
    export_parser = subparsers.add_parser(
        "export",
        help="Export liquid classes to CSV",
        description="Export all liquid classes to a CSV file for backup or editing",
    )
    export_parser.add_argument("filepath", help="Output CSV file path (e.g., output.csv)")

    # Import command
    import_parser = subparsers.add_parser(
        "import",
        help="Import liquid classes from CSV",
        description="Import liquid classes from a CSV file (replaces existing data)",
    )
    import_parser.add_argument(
        "filepath", help="Input CSV file path (must have correct header format)"
    )

    # Add command
    subparsers.add_parser(
        "add",
        help="Add new liquid class interactively",
        description=(
            "Interactively add a new liquid class by selecting pipette, liquid, "
            "and entering parameters"
        ),
    )

    # Delete command
    delete_parser = subparsers.add_parser(
        "delete",
        help="Delete specific liquid class",
        description="Delete a specific liquid class with confirmation prompt",
    )
    delete_parser.add_argument("pipette", help="Pipette type (P20, P300, P1000)")
    delete_parser.add_argument("liquid", help="Liquid type (e.g., Glycerol 99, Water, DMSO)")

    # Help command
    subparsers.add_parser(
        "help",
        help="Show detailed help and available options",
        description=(
            "Display comprehensive help including all available pipettes, liquids, "
            "and parameter descriptions"
        ),
    )

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
            auto_save_registry()
            print(f"Successfully imported liquid classes from '{args.filepath}'")
        except Exception as e:
            print(f"Error importing CSV: {e}")
            sys.exit(1)

    elif args.command == "add":
        add_liquid_class_interactive()

    elif args.command == "delete":
        delete_liquid_class(args.pipette, args.liquid)

    elif args.command == "help":
        show_available_options()


if __name__ == "__main__":
    main()
