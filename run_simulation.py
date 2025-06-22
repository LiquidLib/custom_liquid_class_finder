#!/usr/bin/env python3
"""
Wrapper script to run Opentrons simulation with command-line arguments
"""

import sys
import subprocess
import tempfile
import os
from pathlib import Path


def create_modified_protocol(liquid_type="GLYCEROL_50", sample_count=96, export_temp=False):
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

    print(f"Running simulation with:")
    print(f"  Liquid Type: {liquid_type}")
    print(f"  Sample Count: {sample_count}")
    print()

    # Create modified protocol
    temp_protocol = create_modified_protocol(liquid_type, sample_count, export_temp)
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
            except:
                pass
        else:
            print(f"\nTemporary protocol file exported to: {temp_protocol}")


def main():
    """Main function to handle command-line arguments"""

    # Default values
    liquid_type = "GLYCEROL_50"
    sample_count = 8
    export_temp = False

    # Parse command-line arguments
    args = sys.argv[1:]

    # Check for export flag
    if "--export" in args:
        export_temp = True
        args.remove("--export")

    if len(args) > 0:
        liquid_type = args[0].upper()

    if len(args) > 1:
        try:
            sample_count = int(args[1])
        except ValueError:
            print("Error: Sample count must be a number")
            return 1

    # Validate liquid type
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

    # Validate sample count
    if sample_count < 1 or sample_count > 96:
        print("Error: Sample count must be between 1 and 96")
        return 1

    # Run simulation
    success = run_simulation(liquid_type, sample_count, export_temp)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
