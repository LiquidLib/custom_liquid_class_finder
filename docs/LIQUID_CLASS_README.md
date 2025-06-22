# Liquid Class Configuration System

A comprehensive system for managing liquid handling parameters for different pipette-liquid combinations, with support for CSV import/export and integration with Opentrons protocols.

## Overview

This system provides a structured way to store, retrieve, and manage liquid class parameters for automated liquid handling. It's designed to work with the existing gradient descent calibration protocol and supports the reference data format you provided.

## Your Reference Data

The system is pre-configured with your reference liquid class data:

```
Pipette,Liquid,Aspiration Rate (µL/s),Aspiration Delay (s),Aspiration Withdrawal Rate (mm/s),Dispense Rate (µL/s),Dispense Delay (s),Blowout Rate (µL/s),Touch tip
P1000,Glycerol 99%,41.175,20,4,19.215,20,5.0,No
```

**Key Parameters for Glycerol 99% with P1000:**
- **Aspiration Rate**: 41.175 µL/s (slow for viscous liquid)
- **Aspiration Delay**: 20 s (long delay for complete aspiration)
- **Aspiration Withdrawal Rate**: 4 mm/s (slow withdrawal)
- **Dispense Rate**: 19.215 µL/s (very slow for controlled dispensing)
- **Dispense Delay**: 20 s (long delay for complete dispensing)
- **Blowout Rate**: 5.0 µL/s (slow blowout)
- **Touch Tip**: No (not needed for glycerol)

## Features

### 🔧 **Core Functionality**
- **Liquid Class Registry**: Centralized storage of parameters
- **Type Safety**: Enum-based pipette and liquid types
- **CSV Import/Export**: Easy data exchange
- **Protocol Integration**: Seamless integration with Opentrons protocols

### 📊 **Supported Pipettes**
- P1000 (1000 µL)
- P300 (300 µL)
- P50 (50 µL)

### 🧪 **Supported Liquids**
- Glycerol 99%
- Water
- DMSO
- Ethanol

### 🔄 **Data Formats**
- **CSV Format**: Standard spreadsheet format
- **Dictionary Format**: For protocol integration
- **String Format**: For display and logging

## Quick Start

### 1. Basic Usage

```python
from liquids.liquid_classes import get_liquid_class_params, PipetteType, LiquidType

# Get parameters for your reference data
params = get_liquid_class_params(PipetteType.P1000, LiquidType.GLYCEROL_99)

if params:
    print(f"Aspiration Rate: {params.aspiration_rate} µL/s")
    print(f"Dispense Rate: {params.dispense_rate} µL/s")
    print(f"Touch Tip: {params.touch_tip}")
```

### 2. Protocol Integration

```python
# In your Opentrons protocol
liquid_params = get_liquid_class_params(PIPETTE_TYPE, LIQUID_TYPE)

if liquid_params:
    params = liquid_params.to_dict()

    # Set pipette flow rates
    pipette.flow_rate.aspirate = params['aspiration_rate']
    pipette.flow_rate.dispense = params['dispense_rate']
    pipette.flow_rate.blow_out = params['blowout_rate']

    # Use in liquid handling
    pipette.aspirate(volume, source)
    protocol.delay(seconds=params['aspiration_delay'])
    pipette.dispense(volume, destination)
    protocol.delay(seconds=params['dispense_delay'])

    if params['touch_tip']:
        pipette.touch_tip(destination)
```

### 3. CSV Import/Export

```python
from liquids.liquid_classes import export_liquid_classes_csv, import_liquid_classes_from_csv

# Export all liquid classes to CSV
csv_data = export_liquid_classes_csv()
print(csv_data)

# Import from CSV
csv_data = """Pipette,Liquid,Aspiration Rate (µL/s),Aspiration Delay (s),Aspiration Withdrawal Rate (mm/s),Dispense Rate (µL/s),Dispense Delay (s),Blowout Rate (µL/s),Touch tip
P1000,Glycerol 99%,41.175,20,4,19.215,20,5.0,No"""

import_liquid_classes_from_csv(csv_data)
```

### 4. Adding New Liquid Classes

```python
from liquids.liquid_classes import LiquidClassParams, add_liquid_class_params

# Create new liquid class
new_params = LiquidClassParams(
    pipette=PipetteType.P300,
    liquid=LiquidType.DMSO,
    aspiration_rate=75.0,
    aspiration_delay=2.0,
    aspiration_withdrawal_rate=3.0,
    dispense_rate=75.0,
    dispense_delay=2.0,
    blowout_rate=50.0,
    touch_tip=True
)

# Add to registry
add_liquid_class_params(new_params)
```

## File Structure

```
├── liquid_classes.py          # Core liquid class system
├── liquid_class_demo_basic.py # Basic demonstration script
├── liquid_class_demo_custom.py # Comprehensive demonstration script
├── test_liquid_classes.py     # Test suite
├── protocol.py               # Updated protocol with integration
└── LIQUID_CLASS_README.md    # This file
```

## API Reference

### Core Classes

#### `LiquidClassParams`
Data class representing liquid class parameters.

```python
@dataclass
class LiquidClassParams:
    pipette: PipetteType
    liquid: LiquidType
    aspiration_rate: float  # µL/s
    aspiration_delay: float  # s
    aspiration_withdrawal_rate: float  # mm/s
    dispense_rate: float  # µL/s
    dispense_delay: float  # s
    blowout_rate: float  # µL/s
    touch_tip: bool
```

#### `LiquidClassRegistry`
Central registry for managing liquid class parameters.

```python
class LiquidClassRegistry:
    def add_liquid_class(self, liquid_class: LiquidClassParams)
    def get_liquid_class(self, pipette: PipetteType, liquid: LiquidType) -> Optional[LiquidClassParams]
    def list_liquid_classes(self) -> Dict[str, LiquidClassParams]
    def export_csv(self) -> str
    def import_from_csv(self, csv_data: str)
```

### Convenience Functions

```python
# Get liquid class parameters
get_liquid_class_params(pipette: PipetteType, liquid: LiquidType) -> Optional[LiquidClassParams]

# Add liquid class parameters
add_liquid_class_params(liquid_class: LiquidClassParams)

# Export to CSV
export_liquid_classes_csv() -> str

# Import from CSV
import_liquid_classes_from_csv(csv_data: str)
```

## Testing

Run the test suite to verify everything works correctly:

```bash
python test_liquid_classes.py
```

This will run both the demo and comprehensive tests.

## Integration with Gradient Descent Protocol

The updated `protocol.py` now integrates with the liquid class system:

1. **Parameter Selection**: Uses liquid class parameters as starting point
2. **Liquid Type Support**: Configurable liquid types via protocol parameters
3. **Fallback Handling**: Graceful fallback to default parameters if liquid class not found
4. **Dynamic Liquid Definition**: Automatic liquid definition based on selected type

### Protocol Parameters

The protocol now includes these additional parameters:

- **Liquid type**: Choose from Glycerol 99%, Water, DMSO, Ethanol
- **Pipette type**: Choose from P1000, P300, P50

## Best Practices

### 1. **Parameter Validation**
Always validate parameters before use:

```python
params = get_liquid_class_params(pipette_type, liquid_type)
if params is None:
    # Use default parameters or raise error
    pass
```

### 2. **CSV Data Management**
- Keep CSV files in version control
- Validate CSV format before import
- Export regularly to backup configurations

### 3. **Protocol Integration**
- Use the `to_dict()` method for protocol integration
- Handle missing liquid classes gracefully
- Log which liquid class is being used

### 4. **Adding New Liquids**
- Test parameters thoroughly before adding
- Document the source of parameters
- Consider viscosity and surface tension

## Troubleshooting

### Common Issues

1. **"No liquid class parameters found"**
   - Check that the pipette and liquid combination exists
   - Verify enum values match exactly
   - Import CSV data if needed

2. **CSV Import Errors**
   - Ensure CSV has correct header format
   - Check that all numeric values are valid
   - Verify enum values match supported types

3. **Protocol Integration Issues**
   - Use `to_dict()` method for parameter conversion
   - Handle None return values
   - Check parameter bounds

### Debug Mode

Enable debug output by running the demo script:

```bash
python liquid_class_demo_basic.py
```

This will show all available liquid classes and demonstrate functionality.

## Future Enhancements

### Planned Features
- **Parameter Validation**: Automatic bounds checking
- **Liquid Properties**: Viscosity, surface tension, density
- **Temperature Dependencies**: Temperature-based parameter adjustment
- **Batch Operations**: Bulk import/export operations
- **Web Interface**: GUI for parameter management

### Extension Points
- **Custom Liquid Types**: Easy addition of new liquids
- **Parameter Interpolation**: Automatic parameter calculation
- **Performance Metrics**: Integration with calibration results
- **Database Backend**: Persistent storage option

## Contributing

To add new features or fix issues:

1. **Add Tests**: Include comprehensive test coverage
2. **Update Documentation**: Keep this README current
3. **Follow Conventions**: Use existing code style
4. **Validate Changes**: Run test suite before submitting

## License

This system is part of the liquid class calibration project and follows the same licensing terms.
