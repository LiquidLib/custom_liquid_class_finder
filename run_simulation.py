#!/usr/bin/env python3
"""
Wrapper script to run Opentrons simulation with command-line arguments
"""

import sys
import subprocess
import tempfile
import os
from pathlib import Path
import argparse


def get_liquid_class_params_from_module(liquid_type, pipette_type="P1000"):
    """Dynamically evaluate the liquid_classes module to get parameters"""

    try:
        # Import the liquid classes module
        sys.path.insert(0, str(Path.cwd()))
        from liquids.liquid_classes import get_liquid_class_params, PipetteType, LiquidType

        # Convert string types to enums
        pipette_enum = PipetteType[pipette_type]
        liquid_enum = LiquidType[liquid_type]

        # Get the liquid class parameters
        params = get_liquid_class_params(pipette_enum, liquid_enum)

        if params:
            return {
                "aspiration_rate": params.aspiration_rate,
                "aspiration_delay": params.aspiration_delay,
                "aspiration_withdrawal_rate": params.aspiration_withdrawal_rate,
                "dispense_rate": params.dispense_rate,
                "dispense_delay": params.dispense_delay,
                "blowout_rate": params.blowout_rate,
                "touch_tip": params.touch_tip,
            }
        else:
            # Fallback to default parameters if not found
            return get_default_liquid_params(pipette_type, liquid_type)

    except ImportError as e:
        print(f"Warning: Could not import liquid_classes module: {e}")
        return get_default_liquid_params(pipette_type, liquid_type)
    except Exception as e:
        print(f"Warning: Error getting liquid class parameters: {e}")
        return get_default_liquid_params(pipette_type, liquid_type)


def parse_custom_params(custom_params_str):
    """Parse custom liquid class parameters from command line string"""
    if not custom_params_str:
        return None

    params = {}
    try:
        # Parse key=value pairs
        for pair in custom_params_str.split(","):
            if "=" in pair:
                key, value = pair.strip().split("=", 1)
                key = key.strip()
                value = value.strip()

                # Convert value to appropriate type
                if key in [
                    "aspiration_rate",
                    "aspiration_delay",
                    "aspiration_withdrawal_rate",
                    "dispense_rate",
                    "dispense_delay",
                    "blowout_rate",
                ]:
                    params[key] = float(value)
                elif key == "touch_tip":
                    # Handle boolean values
                    if value.lower() in ["true", "yes", "1", "on"]:
                        params[key] = True
                    elif value.lower() in ["false", "no", "0", "off"]:
                        params[key] = False
                    else:
                        raise ValueError(f"Invalid boolean value for {key}: {value}")
                else:
                    raise ValueError(f"Unknown parameter: {key}")

    except Exception as e:
        raise ValueError(f"Error parsing custom parameters: {e}")

    return params


def get_default_liquid_params(pipette_type, liquid_type):
    """Fallback default parameters if liquid class lookup fails"""

    # Base parameters by pipette type
    base_params = {
        "P20": {
            "aspiration_rate": 5.0,
            "aspiration_delay": 1.0,
            "aspiration_withdrawal_rate": 5.0,
            "dispense_rate": 5.0,
            "dispense_delay": 1.0,
            "blowout_rate": 1.0,
            "touch_tip": False,
        },
        "P50": {
            "aspiration_rate": 10.0,
            "aspiration_delay": 1.0,
            "aspiration_withdrawal_rate": 5.0,
            "dispense_rate": 10.0,
            "dispense_delay": 1.0,
            "blowout_rate": 5.0,
            "touch_tip": False,
        },
        "P300": {
            "aspiration_rate": 50.0,
            "aspiration_delay": 1.0,
            "aspiration_withdrawal_rate": 5.0,
            "dispense_rate": 50.0,
            "dispense_delay": 1.0,
            "blowout_rate": 10.0,
            "touch_tip": False,
        },
        "P1000": {
            "aspiration_rate": 150.0,
            "aspiration_delay": 1.0,
            "aspiration_withdrawal_rate": 5.0,
            "dispense_rate": 150.0,
            "dispense_delay": 1.0,
            "blowout_rate": 100.0,
            "touch_tip": True,
        },
    }

    params = base_params.get(pipette_type, base_params["P1000"]).copy()

    # Adjust for volatile liquids
    if liquid_type in ["DMSO", "ETHANOL", "SANITIZER_62_ALCOHOL"]:
        params["aspiration_rate"] *= 0.7
        params["dispense_rate"] *= 0.7
        params["blowout_rate"] *= 0.5
        params["touch_tip"] = True

    return params


def create_modified_protocol(
    liquid_type="GLYCEROL_50",
    sample_count=96,
    export_temp=False,
    use_real_detection=False,
    custom_params=None,
):
    """Create a modified protocol file with the specified parameters"""

    # Read the original protocol
    protocol_path = Path("protocol.py")
    if not protocol_path.exists():
        print("Error: protocol.py not found")
        return None

    with open(protocol_path, "r") as f:
        content = f.read()

    # Create a file with modified parameters
    if export_temp:
        # Create in current directory with descriptive name
        output_filename = f"protocol_{liquid_type}_{sample_count}samples.py"
        temp_file = open(output_filename, "w")
    else:
        # Create temporary file in system temp directory
        temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False)

    # Replace the default values in the protocol
    modified_content = content.replace('default="GLYCEROL_99"', f'default="{liquid_type}"').replace(
        "default=96", f"default={sample_count}"
    )

    # Set the detection flag based on use_real_detection parameter
    if use_real_detection:
        modified_content = modified_content.replace(
            "USE_REAL_DETECTION = False  # Set to False for simulation mode",
            "USE_REAL_DETECTION = True  # Set to True for real detection",
        )
    else:
        modified_content = modified_content.replace(
            "USE_REAL_DETECTION = True  # Set to False for simulation mode",
            "USE_REAL_DETECTION = False  # Set to False for simulation mode",
        )

    # Handle custom parameters if provided
    if custom_params:
        modified_content = _inject_custom_liquid_params(
            modified_content, liquid_type, custom_params
        )
    elif export_temp:
        modified_content = _inject_hardcoded_liquid_params(modified_content, liquid_type)

    # Replace enum comparisons with string comparisons
    for liquid in [
        "GLYCEROL_10",
        "GLYCEROL_50",
        "GLYCEROL_90",
        "GLYCEROL_99",
        "PEG_8000_50",
        "SANITIZER_62_ALCOHOL",
        "TWEEN_20_100",
        "ENGINE_OIL_100",
        "WATER",
        "DMSO",
        "ETHANOL",
    ]:
        modified_content = modified_content.replace(
            f"LIQUID_TYPE == LiquidType.{liquid}", f"LIQUID_TYPE == '{liquid}'"
        )

    temp_file.write(modified_content)
    temp_file.close()

    return temp_file.name


def _inject_custom_liquid_params(content, liquid_type, custom_params):
    """Inject custom liquid parameters into protocol content"""
    # Merge with defaults for any missing parameters
    default_params = get_liquid_class_params_from_module(liquid_type)
    if default_params:
        for key, value in default_params.items():
            if key not in custom_params:
                custom_params[key] = value

    # Create hardcoded function with custom parameters
    hardcoded_function = f'''
# flake8: noqa: E272,E202

def get_hardcoded_liquid_class_params():
    """Hardcoded liquid class parameters for {liquid_type} (custom)"""
    return {{
        "aspiration_rate": {custom_params["aspiration_rate"]},
        "aspiration_delay": {custom_params["aspiration_delay"]},
        "aspiration_withdrawal_rate": {custom_params["aspiration_withdrawal_rate"]},
        "dispense_rate": {custom_params["dispense_rate"]},
        "dispense_delay": {custom_params["dispense_delay"]},
        "blowout_rate": {custom_params["blowout_rate"]},
        "touch_tip": {custom_params["touch_tip"]}
    }}

def get_default_liquid_class_params(pipette, liquid):
    """Simplified default liquid class parameters for exported protocol"""
    # Return the hardcoded parameters since we don't need the complex logic
    return get_hardcoded_liquid_class_params()
'''

    return _inject_liquid_params_into_content(content, hardcoded_function, liquid_type)


def _inject_hardcoded_liquid_params(content, liquid_type):
    """Inject hardcoded liquid parameters into protocol content"""
    # Get the liquid class parameters by evaluating the module
    liquid_params = get_liquid_class_params_from_module(liquid_type)

    if not liquid_params:
        return content

    # Create hardcoded function
    hardcoded_function = f'''
# flake8: noqa: E272,E202

def get_hardcoded_liquid_class_params():
    """Hardcoded liquid class parameters for {liquid_type}"""
    return {{
        "aspiration_rate": {liquid_params["aspiration_rate"]},
        "aspiration_delay": {liquid_params["aspiration_delay"]},
        "aspiration_withdrawal_rate": {liquid_params["aspiration_withdrawal_rate"]},
        "dispense_rate": {liquid_params["dispense_rate"]},
        "dispense_delay": {liquid_params["dispense_delay"]},
        "blowout_rate": {liquid_params["blowout_rate"]},
        "touch_tip": {liquid_params["touch_tip"]}
    }}

def get_default_liquid_class_params(pipette, liquid):
    """Simplified default liquid class parameters for exported protocol"""
    # Return the hardcoded parameters since we don't need the complex logic
    return get_hardcoded_liquid_class_params()
'''

    return _inject_liquid_params_into_content(content, hardcoded_function, liquid_type)


def _inject_liquid_params_into_content(content, hardcoded_function, liquid_type):
    """Common function to inject liquid parameters into protocol content"""
    # Remove the liquid class imports
    import_string = (
        "from liquids.liquid_classes import (\n"
        "    get_liquid_class_params,\n"
        "    PipetteType,\n"
        "    LiquidType,\n"
        "    LiquidClassParams,\n"
        ")"
    )
    content = content.replace(
        import_string,
        "# Liquid class imports removed - using hardcoded values",
    )

    # Add the hardcoded function after the imports section
    import_end = content.find("metadata = {")
    if import_end != -1:
        content = content[:import_end] + hardcoded_function + "\n\n" + content[import_end:]

    # Replace the liquid type conversion in the run function
    content = content.replace(
        "LIQUID_TYPE = LiquidType[protocol.params.liquid_type]  # type: ignore",
        f"LIQUID_TYPE = '{liquid_type}'  # Hardcoded liquid type",
    )

    # Replace the pipette type conversion
    content = content.replace(
        "PIPETTE_TYPE = PipetteType[protocol.params.pipette_type]  # type: ignore",
        "PIPETTE_TYPE = 'P1000'  # Hardcoded pipette type",
    )

    # Replace the get_liquid_class_params call with the hardcoded function
    content = content.replace(
        "get_liquid_class_params(PIPETTE_TYPE, LIQUID_TYPE)",
        "get_hardcoded_liquid_class_params()",
    )

    # Replace references to .value attributes since we're using strings now
    content = content.replace("PIPETTE_TYPE.value", "PIPETTE_TYPE")
    content = content.replace("LIQUID_TYPE.value", "LIQUID_TYPE")

    # Replace the .to_dict() call since we're returning a dict directly
    content = content.replace("liquid_class_params.to_dict()", "liquid_class_params")

    # Replace the original get_default_liquid_class_params function
    # Find the start and end of the original function
    original_func_start = content.find(
        "def get_default_liquid_class_params("
        "pipette: PipetteType, liquid: LiquidType) -> LiquidClassParams:"
    )
    if original_func_start != -1:
        # Find the end of the function (next function definition)
        next_func_start = content.find("def ", original_func_start + 1)
        if next_func_start != -1:
            # Replace the entire original function
            content = content[:original_func_start] + content[next_func_start:]
        else:
            # If no next function, just remove from start to end of file
            content = content[:original_func_start]

    return content


def filter_output(output, verbose=False):
    """Filter out unwanted messages from the output"""
    if not output:
        return ""

    lines = output.split("\n")
    filtered_lines = []

    # Messages to skip in non-verbose mode
    skip_messages = [
        "robot_settings.json not found",
        "Loading defaults",
        "Belt calibration not found",
        "Using default robot settings",
        "Robot settings loaded",
    ]

    # Messages to highlight in verbose mode
    highlight_messages = [
        "Protocol simulation completed",
        "Protocol completed successfully",
        "Error:",
        "Warning:",
        "INFO:",
        "DEBUG:",
    ]

    for line in lines:
        # Skip unwanted messages unless verbose
        if not verbose and any(skip_msg in line for skip_msg in skip_messages):
            continue

        # Highlight important messages in verbose mode
        if verbose and any(highlight_msg in line for highlight_msg in highlight_messages):
            filtered_lines.append(f"  {line}")
        else:
            filtered_lines.append(line)

    return "\n".join(filtered_lines)


def run_simulation(
    liquid_type="GLYCEROL_50",
    sample_count=96,
    export_temp=False,
    verbose=False,
    quiet=False,
    custom_params=None,
):
    """Run the simulation with specified parameters"""

    if not quiet:
        print("Running simulation with:")
        print(f"  Liquid Type: {liquid_type}")
        print(f"  Sample Count: {sample_count}")
        print(f"  Detection Mode: {'Real' if export_temp else 'Simulated'}")
        if verbose:
            print(f"  Verbose Mode: Enabled")
        print()

    # Use real detection when exporting
    use_real_detection = export_temp

    # Create modified protocol
    temp_protocol = create_modified_protocol(
        liquid_type, sample_count, export_temp, use_real_detection, custom_params
    )
    if not temp_protocol:
        return False

    try:
        # Run the simulation
        result = subprocess.run(
            ["opentrons_simulate", temp_protocol], capture_output=True, text=True
        )

        # Filter and print output
        if result.stdout:
            filtered_stdout = filter_output(result.stdout, verbose)
            if filtered_stdout.strip():
                if not quiet:
                    print("Simulation Output:")
                    print(filtered_stdout)

        if result.stderr:
            filtered_stderr = filter_output(result.stderr, verbose)
            if filtered_stderr.strip():
                if not quiet:
                    print("Simulation Errors:")
                    print(filtered_stderr)

        if verbose and not quiet:
            print(f"Simulation completed with return code: {result.returncode}")

        return result.returncode == 0

    finally:
        # Clean up temporary file unless export is requested
        if not export_temp:
            try:
                os.unlink(temp_protocol)
            except OSError:
                pass
        else:
            if not quiet:
                print(f"\nTemporary protocol file exported to: {temp_protocol}")


def create_modified_8channel_protocol(
    liquid_type="GLYCEROL_50",
    sample_count=96,
    export_temp=False,
    use_real_detection=False,
    custom_params=None,
):
    """Create a modified 8channel protocol file with the specified parameters"""
    protocol_path = Path("protocol_8channel_single.py")
    if not protocol_path.exists():
        print("Error: protocol_8channel_single.py not found")
        return None
    with open(protocol_path, "r") as f:
        content = f.read()
    if export_temp:
        output_filename = f"protocol_8channel_single_{liquid_type}_{sample_count}samples.py"
        temp_file = open(output_filename, "w")
    else:
        temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False)
    modified_content = content.replace('default="GLYCEROL_99"', f'default="{liquid_type}"').replace(
        "default=96", f"default={sample_count}"
    )

    # Set the detection flag based on use_real_detection parameter
    if use_real_detection:
        modified_content = modified_content.replace(
            "USE_REAL_DETECTION = False  # Set to False for simulation mode",
            "USE_REAL_DETECTION = True  # Set to True for real detection",
        )
    else:
        modified_content = modified_content.replace(
            "USE_REAL_DETECTION = True  # Set to False for simulation mode",
            "USE_REAL_DETECTION = False  # Set to False for simulation mode",
        )

    # Handle custom parameters if provided
    if custom_params:
        modified_content = _inject_custom_liquid_params(
            modified_content, liquid_type, custom_params
        )
    elif export_temp:
        modified_content = _inject_hardcoded_liquid_params(modified_content, liquid_type)

    # Replace enum comparisons with string comparisons
    for liquid in [
        "GLYCEROL_10",
        "GLYCEROL_50",
        "GLYCEROL_90",
        "GLYCEROL_99",
        "PEG_8000_50",
        "SANITIZER_62_ALCOHOL",
        "TWEEN_20_100",
        "ENGINE_OIL_100",
        "WATER",
        "DMSO",
        "ETHANOL",
    ]:
        modified_content = modified_content.replace(
            f"LIQUID_TYPE == LiquidType.{liquid}", f"LIQUID_TYPE == '{liquid}'"
        )

    temp_file.write(modified_content)
    temp_file.close()
    return temp_file.name


def run_simulation_8channel(
    liquid_type="GLYCEROL_50",
    sample_count=96,
    export_temp=False,
    verbose=False,
    quiet=False,
    custom_params=None,
):
    """Run the 8channel simulation with specified parameters"""
    if not quiet:
        print("Running 8-channel simulation with:")
        print(f"  Liquid Type: {liquid_type}")
        print(f"  Sample Count: {sample_count}")
        print(f"  Detection Mode: {'Real' if export_temp else 'Simulated'}")
        if verbose:
            print(f"  Verbose Mode: Enabled")
        print()

    # Use real detection when exporting
    use_real_detection = export_temp

    temp_protocol = create_modified_8channel_protocol(
        liquid_type, sample_count, export_temp, use_real_detection, custom_params
    )
    if not temp_protocol:
        return False
    try:
        result = subprocess.run(
            ["opentrons_simulate", temp_protocol], capture_output=True, text=True
        )
        if result.stdout:
            filtered_stdout = filter_output(result.stdout, verbose)
            if filtered_stdout.strip():
                if not quiet:
                    print("Simulation Output:")
                    print(filtered_stdout)
        if result.stderr:
            filtered_stderr = filter_output(result.stderr, verbose)
            if filtered_stderr.strip():
                if not quiet:
                    print("Simulation Errors:")
                    print(filtered_stderr)

        if verbose and not quiet:
            print(f"8-channel simulation completed with return code: {result.returncode}")

        return result.returncode == 0
    finally:
        if not export_temp:
            try:
                os.unlink(temp_protocol)
            except OSError:
                pass
        else:
            if not quiet:
                print(f"\nTemporary 8channel protocol file exported to: {temp_protocol}")


def main():
    """Main function to handle command-line arguments"""
    parser = argparse.ArgumentParser(
        description="Run Opentrons protocol simulation with custom liquid class parameters",
        epilog="""
EXAMPLES:
  # Basic simulation with default parameters
  python run_simulation.py

  # Simulate with specific liquid type and sample count
  python run_simulation.py GLYCEROL_99 24

  # Run 8-channel simulation
  python run_simulation.py WATER 96 --8channel

  # Export protocol file for inspection
  python run_simulation.py DMSO 48 --export

  # List available liquid types
  python run_simulation.py --list-liquids

  # Show liquid class parameters for a specific type
  python run_simulation.py --show-params GLYCEROL_50

  # Verbose output with detailed information
  python run_simulation.py ETHANOL 12 --verbose

  # Run with custom liquid class parameters
  python run_simulation.py WATER 8 --custom-params "aspiration_rate=100,dispense_rate=80,touch_tip=true"

  # Custom parameters with 8-channel mode
  python run_simulation.py DMSO 24 --8channel --custom-params "aspiration_rate=50,aspiration_delay=2.0"

AVAILABLE LIQUID TYPES:
  GLYCEROL_10, GLYCEROL_50, GLYCEROL_90, GLYCEROL_99
  PEG_8000_50, SANITIZER_62_ALCOHOL, TWEEN_20_100
  ENGINE_OIL_100, WATER, DMSO, ETHANOL

For more information, visit: https://github.com/LiquidLib/custom_liquid_class_finder
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Positional arguments
    parser.add_argument(
        "liquid_type",
        nargs="?",
        default="GLYCEROL_50",
        help="Liquid type to use for simulation (default: GLYCEROL_50)",
    )
    parser.add_argument(
        "sample_count",
        nargs="?",
        type=int,
        default=8,
        help="Number of samples to process (1-96, default: 8)",
    )

    # Mode options
    parser.add_argument(
        "--8channel",
        action="store_true",
        help="Run simulation in 8-channel mode (default: single-channel)",
    )
    parser.add_argument(
        "--export",
        action="store_true",
        help="Export the generated protocol file instead of deleting it after simulation",
    )

    # Information options
    parser.add_argument(
        "--list-liquids", action="store_true", help="List all available liquid types and exit"
    )
    parser.add_argument(
        "--show-params",
        metavar="LIQUID_TYPE",
        help="Show liquid class parameters for the specified liquid type and exit",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output with detailed simulation information",
    )
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress non-error output")

    # Advanced options
    parser.add_argument(
        "--pipette",
        choices=["P20", "P50", "P300", "P1000"],
        default="P1000",
        help="Pipette type to use (default: P1000)",
    )
    parser.add_argument(
        "--real-detection",
        action="store_true",
        help="Enable real detection mode (default: simulation mode)",
    )

    # Custom liquid class parameters
    parser.add_argument(
        "--custom-params",
        metavar="PARAMS",
        help="Custom liquid class parameters in format: param1=value1,param2=value2,... "
        "Available params: aspiration_rate, aspiration_delay, aspiration_withdrawal_rate, "
        "dispense_rate, dispense_delay, blowout_rate, touch_tip",
    )

    # Information options
    parser.add_argument("--version", action="version", version="custom-liquid-class-finder 0.1.0")

    args = parser.parse_args()

    # Handle information requests first
    if args.list_liquids:
        print_liquid_types()
        return 0

    if args.show_params:
        show_liquid_params(args.show_params.upper())
        return 0

    # Validate arguments
    liquid_type = args.liquid_type.upper()
    sample_count = args.sample_count
    export_temp = args.export
    mode_8channel = args.__dict__["8channel"]
    verbose = args.verbose
    quiet = args.quiet

    valid_liquids = [
        "GLYCEROL_10",
        "GLYCEROL_50",
        "GLYCEROL_90",
        "GLYCEROL_99",
        "PEG_8000_50",
        "SANITIZER_62_ALCOHOL",
        "TWEEN_20_100",
        "ENGINE_OIL_100",
        "WATER",
        "DMSO",
        "ETHANOL",
    ]

    if liquid_type not in valid_liquids:
        print(f"Error: Invalid liquid type '{liquid_type}'")
        print(f"Available types: {', '.join(valid_liquids)}")
        print("Use --list-liquids to see detailed descriptions")
        return 1

    if sample_count < 1 or sample_count > 96:
        print("Error: Sample count must be between 1 and 96")
        return 1

    # Parse custom parameters if provided
    custom_params = None
    if args.custom_params:
        try:
            custom_params = parse_custom_params(args.custom_params)
            if verbose and not quiet:
                print(f"Custom parameters parsed: {custom_params}")
        except ValueError as e:
            print(f"Error: {e}")
            return 1

    # Set detection mode based on arguments
    use_real_detection = args.real_detection or export_temp

    if verbose and not quiet:
        print(f"Configuration:")
        print(f"  Liquid Type: {liquid_type}")
        print(f"  Sample Count: {sample_count}")
        print(f"  Pipette Type: {args.pipette}")
        print(f"  Mode: {'8-channel' if mode_8channel else 'Single-channel'}")
        print(f"  Detection: {'Real' if use_real_detection else 'Simulated'}")
        print(f"  Export: {'Yes' if export_temp else 'No'}")
        if custom_params:
            print(f"  Custom Parameters: {custom_params}")
        print()

    if mode_8channel:
        success = run_simulation_8channel(
            liquid_type, sample_count, export_temp, verbose, quiet, custom_params
        )
    else:
        success = run_simulation(
            liquid_type, sample_count, export_temp, verbose, quiet, custom_params
        )

    return 0 if success else 1


def print_liquid_types():
    """Print all available liquid types with descriptions"""
    liquid_descriptions = {
        "GLYCEROL_10": "Glycerol 10% - Low viscosity aqueous solution",
        "GLYCEROL_50": "Glycerol 50% - Medium viscosity aqueous solution",
        "GLYCEROL_90": "Glycerol 90% - High viscosity aqueous solution",
        "GLYCEROL_99": "Glycerol 99% - Very high viscosity solution",
        "PEG_8000_50": "PEG 8000 50% w/v - Polyethylene glycol solution",
        "SANITIZER_62_ALCOHOL": "Sanitizer 62% Alcohol - Volatile alcohol solution",
        "TWEEN_20_100": "Tween 20 100% - Surfactant solution",
        "ENGINE_OIL_100": "Engine oil 100% - High viscosity oil",
        "WATER": "Water - Standard aqueous solution",
        "DMSO": "DMSO - Dimethyl sulfoxide, volatile organic solvent",
        "ETHANOL": "Ethanol - Volatile alcohol",
    }

    print("Available Liquid Types:")
    print("=" * 50)
    for liquid, description in liquid_descriptions.items():
        print(f"{liquid:<20} - {description}")
    print("\nUse --show-params LIQUID_TYPE to see detailed parameters")


def show_liquid_params(liquid_type):
    """Show liquid class parameters for a specific liquid type"""
    try:
        # Import the liquid classes module
        sys.path.insert(0, str(Path.cwd()))
        from liquids.liquid_classes import get_liquid_class_params, PipetteType, LiquidType

        if liquid_type not in [lt.name for lt in LiquidType]:
            print(f"Error: Unknown liquid type '{liquid_type}'")
            print("Use --list-liquids to see available types")
            return

        liquid_enum = LiquidType[liquid_type]

        print(f"Liquid Class Parameters for {liquid_type}:")
        print("=" * 50)

        for pipette_name in ["P20", "P50", "P300", "P1000"]:
            pipette_enum = PipetteType[pipette_name]
            params = get_liquid_class_params(pipette_enum, liquid_enum)

            if params:
                print(f"\n{pipette_name} Pipette:")
                print(f"  Aspiration Rate: {params.aspiration_rate} µL/s")
                print(f"  Aspiration Delay: {params.aspiration_delay} s")
                print(f"  Aspiration Withdrawal Rate: {params.aspiration_withdrawal_rate} mm/s")
                print(f"  Dispense Rate: {params.dispense_rate} µL/s")
                print(f"  Dispense Delay: {params.dispense_delay} s")
                print(f"  Blowout Rate: {params.blowout_rate} µL/s")
                print(f"  Touch Tip: {'Yes' if params.touch_tip else 'No'}")
            else:
                print(f"\n{pipette_name} Pipette: No parameters available")

    except ImportError as e:
        print(f"Error: Could not import liquid_classes module: {e}")
        print("Make sure you're running from the correct directory")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    sys.exit(main())
