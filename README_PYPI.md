# Custom Liquid Class Finder

[![PyPI version](https://badge.fury.io/py/custom-liquid-class-finder.svg)](https://badge.fury.io/py/custom-liquid-class-finder)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI/CD](https://github.com/LiquidLib/custom_liquid_class_finder/workflows/CI/CD%20Pipeline/badge.svg)](https://github.com/LiquidLib/custom_liquid_class_finder/actions)

An intelligent Opentrons protocol that automatically optimizes liquid handling parameters for viscous liquids using gradient descent optimization. This package minimizes bubble formation and ensures accurate liquid dispensing for challenging liquids like glycerol.

## 🚀 Quick Start

### Installation

```bash
pip install custom-liquid-class-finder
```

### Basic Usage

```python
from liquids.liquid_classes import get_liquid_class_params, PipetteType, LiquidType

# Get optimized parameters for P1000 with Glycerol 99%
params = get_liquid_class_params(PipetteType.P1000, LiquidType.GLYCEROL_99)

if params:
    print(f"Aspiration Rate: {params.aspiration_rate} µL/s")
    print(f"Dispense Rate: {params.dispense_rate} µL/s")
    print(f"Touch Tip: {params.touch_tip}")
```

### Command Line Tool

```bash
# List all available liquid classes
liquid-class-manager list

# Show specific liquid class parameters
liquid-class-manager show P1000 "Glycerol 99%"

# Export to CSV
liquid-class-manager export my_parameters.csv

# Import from CSV
liquid-class-manager import my_parameters.csv
```

## 🧪 Features

- **Automated Optimization**: Uses gradient descent to find optimal parameters
- **Viscous Liquid Support**: Specifically designed for challenging liquids like glycerol
- **Multi-Pipette Support**: P20, P50, P300, P1000 pipettes
- **Multiple Liquid Types**: Glycerol, DMSO, Ethanol, Water, and more
- **CSV Import/Export**: Easy data exchange in standard format
- **Opentrons Integration**: Seamless integration with Opentrons protocols
- **Command Line Tools**: Easy management of liquid class parameters

## 📦 Supported Pipettes & Liquids

| Pipettes | Liquids |
|----------|---------|
| P1000 (1000 µL) | Glycerol 10%, 50%, 90%, 99% |
| P300 (300 µL) | PEG 8000 50% w/v |
| P50 (50 µL) | Sanitizer 62% Alcohol |
| P20 (20 µL) | Tween 20 100%, Engine oil 100% |
| | Water, DMSO, Ethanol |

## 🔧 Advanced Usage

### Custom Liquid Class Parameters

```python
from liquids.liquid_classes import LiquidClassParams, PipetteType, LiquidType

# Create custom parameters
custom_params = LiquidClassParams(
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

# Add to registry
from liquids.liquid_classes import add_liquid_class_params
add_liquid_class_params(custom_params)
```

### Opentrons Protocol Integration

```python
from opentrons import protocol_api
from liquids.liquid_classes import get_liquid_class_params, PipetteType, LiquidType

def run(protocol: protocol_api.ProtocolContext):
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
```

## 📊 Reference Data

The package comes pre-configured with optimized parameters:

```
Pipette,Liquid,Aspiration Rate (µL/s),Aspiration Delay (s),Aspiration Withdrawal Rate (mm/s),Dispense Rate (µL/s),Dispense Delay (s),Blowout Rate (µL/s),Touch tip
P1000,Glycerol 99%,41.175,20,4,19.215,20,5.0,No
```

**Key Parameters for Glycerol 99% with P1000:**
- **Aspiration Rate**: 41.175 µL/s (slow for viscous liquid)
- **Aspiration Delay**: 20 s (long delay for complete aspiration)
- **Dispense Rate**: 19.215 µL/s (very slow for controlled dispensing)
- **Touch Tip**: No (not needed for glycerol)

## 🛠️ Development

### Installation for Development

```bash
git clone https://github.com/LiquidLib/custom_liquid_class_finder.git
cd custom_liquid_class_finder
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=liquids --cov-report=html

# Run specific test file
pytest tests/test_liquid_classes.py
```

### Code Quality

```bash
# Format code
black .

# Lint code
flake8 --max-line-length=100 --extend-ignore=E203,W503 .

# Type checking
mypy --ignore-missing-imports .
```

## 📚 Documentation

For detailed documentation, visit the [GitHub repository](https://github.com/LiquidLib/custom_liquid_class_finder).

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Opentrons for the excellent automation platform
- The scientific community for feedback and testing
- Contributors who help improve liquid handling automation

## 📞 Support

If you encounter any issues or have questions:

1. Check the [documentation](https://github.com/LiquidLib/custom_liquid_class_finder#readme)
2. Search [existing issues](https://github.com/LiquidLib/custom_liquid_class_finder/issues)
3. Create a [new issue](https://github.com/LiquidLib/custom_liquid_class_finder/issues/new)

---

**Made with ❤️ for the scientific community**
