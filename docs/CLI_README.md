# Liquid Class Manager CLI

A comprehensive command-line interface for managing liquid class parameters for automated liquid handling protocols.

## Overview

The Liquid Class Manager CLI provides an easy way to manage liquid handling parameters for different pipette-liquid combinations. It supports viewing, adding, deleting, importing, and exporting liquid class data in CSV format.

## Installation

### Option 1: Standalone Script (Recommended)
The CLI can be run directly without installation:

```bash
python liquid_class_manager.py [command] [options]
```

### Option 2: Installed Package
If you have installed the package, you can use the entry point:

```bash
liquid-class-manager [command] [options]
```

## Available Commands

### `list` - List All Liquid Classes
Display all available liquid classes with their parameters.

```bash
python liquid_class_manager.py list
```

**Output Example:**
```
Available Liquid Classes:
==================================================

P20_Glycerol 10%:
  Pipette: P20
  Liquid: Glycerol 10%
  Aspiration Rate: 6.804 µL/s
  Aspiration Delay: 2.0 s
  Aspiration Withdrawal Rate: 5.0 mm/s
  Dispense Rate: 6.804 µL/s
  Dispense Delay: 2.0 s
  Blowout Rate: 0.5 µL/s
  Touch Tip: False
```

### `show` - Show Specific Liquid Class
Display parameters for a specific pipette-liquid combination.

```bash
python liquid_class_manager.py show P1000 "Glycerol 99%"
```

**Output Example:**
```
Liquid Class Parameters for P1000 - Glycerol 99%:
==================================================
Aspiration Rate: 41.175 µL/s
Aspiration Delay: 20.0 s
Aspiration Withdrawal Rate: 4.0 mm/s
Dispense Rate: 19.215 µL/s
Dispense Delay: 20.0 s
Blowout Rate: 5.0 µL/s
Touch Tip: False
```

### `export` - Export to CSV
Export all liquid classes to a CSV file.

```bash
python liquid_class_manager.py export output.csv
```

**CSV Format:**
```csv
Pipette,Liquid,Aspiration Rate (µL/s),Aspiration Delay (s),Aspiration Withdrawal Rate (mm/s),Dispense Rate (µL/s),Dispense Delay (s),Blowout Rate (µL/s),Touch tip
P1000,Glycerol 99%,41.175,20.0,4.0,19.215,20.0,5.0,No
```

### `import` - Import from CSV
Import liquid classes from a CSV file.

```bash
python liquid_class_manager.py import input.csv
```

**Note:** The CSV must have the exact header format shown above.

### `add` - Add New Liquid Class
Interactively add a new liquid class.

```bash
python liquid_class_manager.py add
```

This will prompt you to:
1. Select a pipette type (P20, P300, P1000)
2. Select a liquid type (Glycerol 10%, Glycerol 99%, etc.)
3. Enter all the parameters (rates, delays, etc.)

### `delete` - Delete Liquid Class
Delete a specific liquid class with confirmation.

```bash
python liquid_class_manager.py delete P1000 "Glycerol 99%"
```

## Supported Pipettes

- **P20**: 20 µL pipette
- **P300**: 300 µL pipette
- **P1000**: 1000 µL pipette

## Supported Liquids

- **Glycerol 10%**: Low viscosity glycerol solution
- **Glycerol 50%**: Medium viscosity glycerol solution
- **Glycerol 90%**: High viscosity glycerol solution
- **Glycerol 99%**: Very high viscosity glycerol solution
- **PEG 8000 50% w/v**: Polyethylene glycol solution
- **Sanitizer 62% Alcohol**: Alcohol-based sanitizer
- **Tween 20 100%**: Surfactant solution
- **Engine oil 100%**: High viscosity oil
- **Water**: Standard water
- **DMSO**: Dimethyl sulfoxide
- **Ethanol**: Ethanol solution

## Parameter Descriptions

### Aspiration Parameters
- **Aspiration Rate**: Speed of liquid uptake (µL/s)
- **Aspiration Delay**: Time to wait after aspiration (s)
- **Aspiration Withdrawal Rate**: Speed of pipette withdrawal (mm/s)

### Dispense Parameters
- **Dispense Rate**: Speed of liquid dispensing (µL/s)
- **Dispense Delay**: Time to wait after dispensing (s)

### Other Parameters
- **Blowout Rate**: Speed of air blowout (µL/s)
- **Touch Tip**: Whether to touch tip after dispensing (Yes/No)

## Examples

### Basic Usage
```bash
# List all available liquid classes
python liquid_class_manager.py list

# Show specific liquid class
python liquid_class_manager.py show P300 "Glycerol 90%"

# Export current data
python liquid_class_manager.py export my_liquid_classes.csv
```

### Data Management
```bash
# Import from CSV file
python liquid_class_manager.py import backup.csv

# Add a new custom liquid class
python liquid_class_manager.py add

# Delete an unwanted liquid class
python liquid_class_manager.py delete P20 "Engine oil 100%"
```

### Batch Operations
```bash
# Export, modify in spreadsheet, then re-import
python liquid_class_manager.py export temp.csv
# Edit temp.csv in your preferred spreadsheet application
python liquid_class_manager.py import temp.csv
```

## Error Handling

The CLI provides helpful error messages for common issues:

- **Invalid pipette/liquid combinations**: Shows available options
- **File not found**: Clear error message with file path
- **CSV format errors**: Detailed parsing error messages
- **Invalid numeric input**: Prompts for correct format

## Integration with Protocols

The liquid class data can be easily integrated into Opentrons protocols:

```python
from liquids.liquid_classes import get_liquid_class_params, PipetteType, LiquidType

# Get parameters for use in protocol
params = get_liquid_class_params(PipetteType.P1000, LiquidType.GLYCEROL_99)
if params:
    # Use parameters in your protocol
    aspiration_rate = params.aspiration_rate
    dispense_rate = params.dispense_rate
```

## Troubleshooting

### Common Issues

1. **"No liquid class found"**: The pipette-liquid combination doesn't exist
2. **CSV import errors**: Check that your CSV has the correct header format
3. **Permission errors**: Ensure you have write permissions for export files

### Getting Help

```bash
# Show general help
python liquid_class_manager.py --help

# Show help for specific command
python liquid_class_manager.py show --help
```

## File Locations

- **Standalone script**: `liquid_class_manager.py` (in project root)
- **Package entry point**: `liquid-class-manager` (after installation)
- **Default data**: `liquids/liquid_classes.csv`

## Contributing

To add new features to the CLI:

1. Modify `liquid_class_manager.py` for the standalone version
2. Update `liquids/liquid_class_manager.py` for the package version
3. Add corresponding tests in `tests/test_liquid_classes.py`
4. Update this documentation

## License

This CLI tool is part of the Custom Liquid Class Finder project and is licensed under the MIT License.

# Custom Liquid Class Finder - CLI Usage Guide

The `run_simulation.py` script provides a robust command-line interface for running Opentrons protocol simulations with custom liquid class parameters.

## Quick Start

```bash
# Basic simulation with default parameters
python run_simulation.py

# Simulate with specific liquid type and sample count
python run_simulation.py GLYCEROL_99 24

# Run 8-channel simulation
python run_simulation.py WATER 96 --8channel

# Export protocol file for inspection
python run_simulation.py DMSO 48 --export
```

## Command Line Options

### Positional Arguments
- `liquid_type` - Liquid type to use for simulation (default: GLYCEROL_50)
- `sample_count` - Number of samples to process (1-96, default: 8)

### Mode Options
- `--8channel` - Run simulation in 8-channel mode (default: single-channel)
- `--export` - Export the generated protocol file instead of deleting it after simulation

### Information Options
- `--list-liquids` - List all available liquid types and exit
- `--show-params LIQUID_TYPE` - Show liquid class parameters for the specified liquid type and exit
- `--verbose, -v` - Enable verbose output with detailed simulation information
- `--quiet, -q` - Suppress non-error output
- `--version` - Show program's version number and exit

### Advanced Options
- `--pipette {P20,P50,P300,P1000}` - Pipette type to use (default: P1000)
- `--real-detection` - Enable real detection mode (default: simulation mode)
- `--custom-params PARAMS` - Custom liquid class parameters in format: `param1=value1,param2=value2,...`

## Available Liquid Types

| Liquid Type | Description |
|-------------|-------------|
| GLYCEROL_10 | Glycerol 10% - Low viscosity aqueous solution |
| GLYCEROL_50 | Glycerol 50% - Medium viscosity aqueous solution |
| GLYCEROL_90 | Glycerol 90% - High viscosity aqueous solution |
| GLYCEROL_99 | Glycerol 99% - Very high viscosity solution |
| PEG_8000_50 | PEG 8000 50% w/v - Polyethylene glycol solution |
| SANITIZER_62_ALCOHOL | Sanitizer 62% Alcohol - Volatile alcohol solution |
| TWEEN_20_100 | Tween 20 100% - Surfactant solution |
| ENGINE_OIL_100 | Engine oil 100% - High viscosity oil |
| WATER | Water - Standard aqueous solution |
| DMSO | DMSO - Dimethyl sulfoxide, volatile organic solvent |
| ETHANOL | Ethanol - Volatile alcohol |

## Custom Liquid Class Parameters

You can specify custom liquid class parameters using the `--custom-params` option. This allows you to override the default parameters for any liquid type.

### Available Parameters

| Parameter | Type | Description | Units |
|-----------|------|-------------|-------|
| `aspiration_rate` | float | Speed of liquid aspiration | µL/s |
| `aspiration_delay` | float | Delay after aspiration | seconds |
| `aspiration_withdrawal_rate` | float | Speed of tip withdrawal after aspiration | mm/s |
| `dispense_rate` | float | Speed of liquid dispense | µL/s |
| `dispense_delay` | float | Delay after dispense | seconds |
| `blowout_rate` | float | Speed of blowout operation | µL/s |
| `touch_tip` | boolean | Whether to touch tip after dispense | true/false |

### Parameter Format

Parameters are specified as comma-separated key-value pairs:
```
param1=value1,param2=value2,param3=value3
```

### Boolean Values

For the `touch_tip` parameter, you can use:
- `true`, `yes`, `1`, `on` for True
- `false`, `no`, `0`, `off` for False

### Examples

```bash
# Override aspiration and dispense rates
python run_simulation.py WATER 8 --custom-params "aspiration_rate=100,dispense_rate=80"

# Set all parameters for a custom liquid class
python run_simulation.py CUSTOM 12 --custom-params "aspiration_rate=50,aspiration_delay=2.0,dispense_rate=40,dispense_delay=1.5,blowout_rate=20,touch_tip=true"

# Use with 8-channel mode
python run_simulation.py ETHANOL 24 --8channel --custom-params "aspiration_rate=75,dispense_rate=60"
```

### Parameter Merging

When you specify custom parameters, they are merged with the default parameters for the liquid type. Any parameters you don't specify will use the default values from the liquid class system.

## Usage Examples

### Basic Operations

```bash
# List all available liquid types
python run_simulation.py --list-liquids

# Show parameters for a specific liquid type
python run_simulation.py --show-params GLYCEROL_50

# Check version
python run_simulation.py --version
```

### Simulation Modes

```bash
# Single-channel simulation (default)
python run_simulation.py WATER 12

# 8-channel simulation
python run_simulation.py ETHANOL 24 --8channel

# With verbose output
python run_simulation.py DMSO 8 --verbose

# Quiet mode (minimal output)
python run_simulation.py GLYCEROL_99 4 --quiet
```

### Protocol Export

```bash
# Export protocol file for inspection
python run_simulation.py WATER 96 --export

# Export with specific parameters
python run_simulation.py ETHANOL 48 --8channel --export
```

### Advanced Usage

```bash
# Use specific pipette type
python run_simulation.py WATER 12 --pipette P300

# Enable real detection mode
python run_simulation.py DMSO 8 --real-detection

  # Combine multiple options
  python run_simulation.py GLYCEROL_50 24 --8channel --verbose --export

  # Run with custom liquid class parameters
  python run_simulation.py WATER 8 --custom-params "aspiration_rate=100,dispense_rate=80,touch_tip=true"

  # Custom parameters with 8-channel mode
  python run_simulation.py DMSO 24 --8channel --custom-params "aspiration_rate=50,aspiration_delay=2.0"
```

## Output Modes

### Normal Mode
Shows essential simulation information and results.

### Verbose Mode (`--verbose`)
Provides detailed information including:
- Configuration summary
- Parameter adjustments
- Gradient calculations
- Step-by-step execution details
- Final optimization statistics

### Quiet Mode (`--quiet`)
Suppresses all non-error output, useful for:
- Batch processing
- Integration with other tools
- Automated testing

## Error Handling

The CLI provides clear error messages for:
- Invalid liquid types
- Out-of-range sample counts
- Missing dependencies
- Protocol generation failures

## Integration

The script can be easily integrated into:
- Automated workflows
- CI/CD pipelines
- Laboratory automation systems
- Data analysis pipelines

## Dependencies

- Python 3.10+
- Opentrons API
- Required protocol files (`protocols/single_channel.py`, `protocols/eight_channel.py`)

## Troubleshooting

### Common Issues

1. **"protocol.py not found"**
   - Ensure you're running from the correct directory
   - Check that protocol files exist

2. **"Could not import liquid_classes module"**
   - Verify the `liquids/` directory structure
   - Check Python path configuration

3. **"Invalid liquid type"**
   - Use `--list-liquids` to see available types
   - Check spelling and case sensitivity

### Getting Help

```bash
# Show help
python run_simulation.py --help

# Show version
python run_simulation.py --version

# List available liquids
python run_simulation.py --list-liquids
```

For more information, visit: https://github.com/LiquidLib/custom_liquid_class_finder
