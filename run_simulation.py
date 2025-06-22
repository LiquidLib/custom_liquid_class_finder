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
    liquid_type="GLYCEROL_50", sample_count=96, export_temp=False, use_real_detection=False
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

    # If exporting, replace the liquid class imports and usage with hardcoded values
    if export_temp:
        # Get the liquid class parameters by evaluating the module
        liquid_params = get_liquid_class_params_from_module(liquid_type)

        if liquid_params:
            # Create a hardcoded liquid class function
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

            # Remove the liquid class imports
            import_string = (
                "from liquids.liquid_classes import (\n"
                "    get_liquid_class_params,\n"
                "    PipetteType,\n"
                "    LiquidType,\n"
                "    LiquidClassParams,\n"
                ")"
            )
            modified_content = modified_content.replace(
                import_string,
                "# Liquid class imports removed - using hardcoded values",
            )

            # Add the hardcoded function after the imports section
            import_end = modified_content.find("metadata = {")
            if import_end != -1:
                modified_content = (
                    modified_content[:import_end]
                    + hardcoded_function
                    + "\n\n"
                    + modified_content[import_end:]
                )

            # Replace the liquid type conversion in the run function
            modified_content = modified_content.replace(
                "LIQUID_TYPE = LiquidType[protocol.params.liquid_type]  # type: ignore",
                f"LIQUID_TYPE = '{liquid_type}'  # Hardcoded liquid type",
            )

            # Replace the pipette type conversion
            modified_content = modified_content.replace(
                "PIPETTE_TYPE = PipetteType[protocol.params.pipette_type]  # type: ignore",
                "PIPETTE_TYPE = 'P1000'  # Hardcoded pipette type",
            )

            # Replace the get_liquid_class_params call with the hardcoded function
            modified_content = modified_content.replace(
                "get_liquid_class_params(PIPETTE_TYPE, LIQUID_TYPE)",
                "get_hardcoded_liquid_class_params()",
            )

            # Replace references to .value attributes since we're using strings now
            modified_content = modified_content.replace("PIPETTE_TYPE.value", "PIPETTE_TYPE")
            modified_content = modified_content.replace("LIQUID_TYPE.value", "LIQUID_TYPE")

            # Replace the .to_dict() call since we're returning a dict directly
            modified_content = modified_content.replace(
                "liquid_class_params.to_dict()", "liquid_class_params"
            )

            # Replace the original get_default_liquid_class_params function
            # Find the start and end of the original function
            original_func_start = modified_content.find(
                "def get_default_liquid_class_params("
                "pipette: PipetteType, liquid: LiquidType) -> LiquidClassParams:"
            )
            if original_func_start != -1:
                # Find the end of the function (next function definition)
                next_func_start = modified_content.find("def ", original_func_start + 1)
                if next_func_start != -1:
                    # Replace the entire original function
                    modified_content = (
                        modified_content[:original_func_start] + modified_content[next_func_start:]
                    )
                else:
                    # If no next function, just remove from start to end of file
                    modified_content = modified_content[:original_func_start]

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


def filter_output(output):
    """Filter out unwanted messages from the output"""
    if not output:
        return ""

    lines = output.split("\n")
    filtered_lines = []

    for line in lines:
        # Skip robot settings and belt calibration messages
        if any(
            skip_msg in line
            for skip_msg in [
                "robot_settings.json not found",
                "Loading defaults",
                "Belt calibration not found",
            ]
        ):
            continue
        filtered_lines.append(line)

    return "\n".join(filtered_lines)


def run_simulation(liquid_type="GLYCEROL_50", sample_count=96, export_temp=False):
    """Run the simulation with specified parameters"""

    print("Running simulation with:")
    print(f"  Liquid Type: {liquid_type}")
    print(f"  Sample Count: {sample_count}")
    print(f"  Detection Mode: {'Real' if export_temp else 'Simulated'}")
    print()

    # Use real detection when exporting
    use_real_detection = export_temp

    # Create modified protocol
    temp_protocol = create_modified_protocol(
        liquid_type, sample_count, export_temp, use_real_detection
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
            filtered_stdout = filter_output(result.stdout)
            if filtered_stdout.strip():
                print("Simulation Output:")
                print(filtered_stdout)

        if result.stderr:
            filtered_stderr = filter_output(result.stderr)
            if filtered_stderr.strip():
                print("Simulation Errors:")
                print(filtered_stderr)

        return result.returncode == 0

    finally:
        # Clean up temporary file unless export is requested
        if not export_temp:
            try:
                os.unlink(temp_protocol)
            except OSError:
                pass
        else:
            print(f"\nTemporary protocol file exported to: {temp_protocol}")


def create_modified_8channel_protocol(
    liquid_type="GLYCEROL_50", sample_count=96, export_temp=False, use_real_detection=False
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

    temp_file.write(modified_content)
    temp_file.close()
    return temp_file.name


def run_simulation_8channel(liquid_type="GLYCEROL_50", sample_count=96, export_temp=False):
    """Run the 8channel simulation with specified parameters"""
    print("Running 8-channel simulation with:")
    print(f"  Liquid Type: {liquid_type}")
    print(f"  Sample Count: {sample_count}")
    print(f"  Detection Mode: {'Real' if export_temp else 'Simulated'}")
    print()

    # Use real detection when exporting
    use_real_detection = export_temp

    temp_protocol = create_modified_8channel_protocol(
        liquid_type, sample_count, export_temp, use_real_detection
    )
    if not temp_protocol:
        return False
    try:
        result = subprocess.run(
            ["opentrons_simulate", temp_protocol], capture_output=True, text=True
        )
        if result.stdout:
            filtered_stdout = filter_output(result.stdout)
            if filtered_stdout.strip():
                print("Simulation Output:")
                print(filtered_stdout)
        if result.stderr:
            filtered_stderr = filter_output(result.stderr)
            if filtered_stderr.strip():
                print("Simulation Errors:")
                print(filtered_stderr)
        return result.returncode == 0
    finally:
        if not export_temp:
            try:
                os.unlink(temp_protocol)
            except OSError:
                pass
        else:
            print(f"\nTemporary 8channel protocol file exported to: {temp_protocol}")


def main():
    """Main function to handle command-line arguments"""
    parser = argparse.ArgumentParser(
        description="Run Opentrons protocol simulation in single or 8-channel mode."
    )
    parser.add_argument(
        "liquid_type",
        nargs="?",
        default="GLYCEROL_50",
        help="Liquid type (default: GLYCEROL_50)",
    )
    parser.add_argument(
        "sample_count",
        nargs="?",
        type=int,
        default=8,
        help="Sample count (default: 8)",
    )
    parser.add_argument(
        "--export",
        action="store_true",
        help="Export the generated protocol file instead of deleting it",
    )
    parser.add_argument(
        "--8channel",
        action="store_true",
        help="Run simulation in 8-channel mode (default: single-channel)",
    )
    args = parser.parse_args()

    liquid_type = args.liquid_type.upper()
    sample_count = args.sample_count
    export_temp = args.export
    mode_8channel = args.__dict__["8channel"]

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
        print(f"Error: Invalid liquid type. Choose from: {', '.join(valid_liquids)}")
        return 1
    if sample_count < 1 or sample_count > 96:
        print("Error: Sample count must be between 1 and 96")
        return 1

    if mode_8channel:
        success = run_simulation_8channel(liquid_type, sample_count, export_temp)
    else:
        success = run_simulation(liquid_type, sample_count, export_temp)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
