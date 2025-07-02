# Liquid Class Calibration with Gradient Descent

[![CI/CD](https://github.com/LiquidLib/custom_liquid_class_finder/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/LiquidLib/custom_liquid_class_finder/actions/workflows/ci-cd.yml)
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Flake8](https://img.shields.io/badge/lint-flake8-blueviolet.svg)](https://flake8.pycqa.org/en/latest/)
[![Mypy](https://img.shields.io/badge/type%20checker-mypy-blue.svg)](http://mypy-lang.org/)

An intelligent Opentrons protocol that automatically optimizes liquid handling parameters for viscous liquids using gradient descent optimization. This protocol minimizes bubble formation and ensures accurate liquid dispensing for challenging liquids like glycerol.

**NEW: Liquid Class Configuration System** - Now includes a comprehensive system for managing liquid handling parameters with CSV import/export and seamless protocol integration.

## Why This Matters

### **Problem Solved**
- **Viscous liquids** like glycerol are notoriously difficult to handle accurately
- **Bubble formation** can ruin experiments and waste expensive reagents
- **Manual optimization** of liquid class parameters is time-consuming and error-prone
- **Inconsistent results** from manual calibration
- **Parameter management** across different liquids and pipettes

### **Benefits**
- **Automated optimization** ensures consistent, reproducible results
- **Systematic approach** eliminates human bias and error
- **Time savings** compared to manual trial-and-error
- **Better performance** through data-driven parameter selection
- **Scalable** to different liquids and conditions
- **Centralized parameter management** for easy sharing and version control


## Videos

Building a protocol on the fly: https://youtu.be/1eq2PzjPmS4

Robot executing the protocol: https://youtube.com/shorts/S0IKX-X8dYI

## Overview

This protocol solves a critical problem in automated liquid handling: **optimizing liquid class parameters for viscous liquids**. Traditional manual calibration is time-consuming and error-prone. This protocol uses machine learning principles (gradient descent) to automatically find the best parameters through systematic testing.

The project now includes a **Liquid Class Configuration System** that provides:
- 📊 **Reference Data Management**: Store and retrieve optimized parameters
- 🔄 **CSV Import/Export**: Easy data exchange in standard format
- 🧪 **Multi-Liquid Support**: Handle different liquids and pipettes
- 🔧 **Protocol Integration**: Seamless integration with calibration protocols

## Key Features

- 🤖 **Automated Optimization**: Uses gradient descent to find optimal parameters
- 🧪 **Viscous Liquid Support**: Specifically designed for challenging liquids like glycerol
- 📊 **Dual Evaluation**: Checks both liquid height accuracy and bubble formation
- 🔧 **Parameter Constraints**: Ensures all parameters stay within safe operational bounds
- 📈 **Real-time Learning**: Adjusts parameters based on previous results
- 🎯 **Optimal Results**: Identifies the best-performing parameter set
- 📋 **Liquid Class Registry**: Centralized parameter management system
- 🔄 **CSV Data Exchange**: Import/export parameters in standard format
- 🎛️ **Configurable Liquids**: Support for multiple liquid types and pipettes
- 🚀 **Simulation Testing**: Built-in simulation tool for rapid parameter testing and protocol generation

## Requirements

- **Robot Type**: Opentrons Flex
- **API Level**: 2.22
- **Labware**:
  - `nest_12_reservoir_15ml` (reservoir)
  - `nest_96_wellplate_200ul_flat` (test plate)
  - `opentrons_flex_96_filtertiprack_1000ul` (1000µL tips)
  - `opentrons_flex_96_filtertiprack_50ul` (50µL tips)
- **Pipettes**:
  - **Single-Channel Mode**: `flex_1channel_1000` (1000µL), `flex_1channel_50` (50µL)
  - **8-Channel Mode**: `flex_8channel_1000` (8-channel 1000µL)

## Quick Start

### **🚀 Protocol Simulation & Testing**

The `run_simulation.py` script is your **go-to tool** for testing protocols with different parameters before running them on physical machines. This is especially valuable for:

- **🧪 Rapid Parameter Testing**: Test different liquid types and sample counts without physical setup
- **🔧 Protocol Generation**: Generate customized protocol files for physical robot deployment
- **⚡ Fast Iteration**: Quickly iterate through parameter combinations to find optimal settings
- **💾 Export Capability**: Save generated protocols for use on physical Opentrons machines

#### **Single-Channel Simulation Examples**

```bash
# Test with default parameters (GLYCEROL_50, 8 samples)
python run_simulation.py

# Test with specific liquid type
python run_simulation.py GLYCEROL_99

# Test with specific liquid and sample count
python run_simulation.py GLYCEROL_90 16

# Generate a protocol file for physical machine use
python run_simulation.py GLYCEROL_99 96 --export
```

### **🔄 8-Channel Mode with 8-Channel Pipettes**

The same `run_simulation.py` script also provides **high-throughput 8-channel processing** using 8-channel pipettes for efficient liquid handling:

- **⚡ 8-Channel Efficiency**: Process 8 wells simultaneously for faster throughput
- **🎯 8-Channel Optimization**: Optimize parameters across multiple wells in parallel
- **🔍 Detection Modes**: Choose between real capacitive sensing or simulated detection
- **📊 8-Channel Analysis**: Comprehensive analysis of channel-to-channel consistency

#### **8-Channel Simulation Examples**

```bash
# Default 8-channel simulation (fake detection, 8 samples)
python run_simulation.py --8channel

# 8-Channel with specific liquid and sample count
python run_simulation.py GLYCEROL_99 24 --8channel

# Use real capacitive detection (for physical robot testing)
python run_simulation.py GLYCEROL_99 24 --8channel --export

# Export 8-channel protocol for physical use
python run_simulation.py GLYCEROL_99 96 --8channel --export
```

#### **Detection Modes**

**Simulated Detection (Default)**:
- ✅ Fast simulation with 95% success rate
- ✅ Good for testing optimization algorithms
- ✅ No real sensor data required
- ✅ Consistent results for development

**Real Detection (with --export)**:
- 🔬 Uses actual capacitive tip sensing
- 🔬 `pipette.aspirate(0)` for liquid detection
- 🔬 Realistic sensor-based evaluation
- 🔬 Best for physical robot deployment

#### **Mode Features**

**Single-Channel Mode**:
- **Individual Well Processing**: Process wells one at a time
- **Gradient Descent**: Optimizes parameters using gradient-based learning
- **Detailed Logging**: Comprehensive well-by-well progress tracking

**8-Channel Mode**:
- **Fixed 8-Channel Size**: 8 wells per operation (optimized for 8-channel pipettes)
- **Gradient Descent**: Optimizes parameters across 8-channel operations
- **Comprehensive Logging**: Detailed 8-channel-by-8-channel progress tracking

### **Basic Protocol Usage**

#### **Single-Channel Mode** (`protocol.py`)
- **Pipettes**: Single-channel 1000µL (dispensing + evaluation)
- **Processing**: Individual wells sequentially
- **Use Case**: Precise optimization with detailed per-well analysis
- **Detection**: Real capacitive sensing or simulated detection
- **Simulation**: Use `run_simulation.py` (default mode)

#### **8-Channel Mode** (`protocol_8channel_single.py`)
- **Pipettes**: 8-channel 1000µL (dispensing + evaluation)
- **Processing**: 8 wells simultaneously in 8-channel operations
- **Use Case**: High-throughput optimization with channel consistency analysis
- **Detection**: Real capacitive sensing or simulated detection
- **Simulation**: Use `run_simulation.py --8channel`

### **Liquid Class System**

The liquid class system provides centralized parameter management:

#### **Quick Start with Liquid Classes**

```python
from liquids.liquid_classes import get_liquid_class_params, PipetteType, LiquidType

# Get your reference data
params = get_liquid_class_params(PipetteType.P1000, LiquidType.GLYCEROL_99)
print(f"Aspiration Rate: {params.aspiration_rate} µL/s")  # 41.175
```

#### **Command Line Management**

**Standalone CLI (Recommended):**
```bash
# List all liquid classes
python liquid_class_manager.py list

# Show your reference data
python liquid_class_manager.py show P1000 "Glycerol 99%"

# Export to CSV
python liquid_class_manager.py export my_liquid_classes.csv

# Import from CSV
python liquid_class_manager.py import my_liquid_classes.csv

# Add new liquid class interactively
python liquid_class_manager.py add

# Delete specific liquid class
python liquid_class_manager.py delete P1000 "Glycerol 99%"
```

**Package Entry Point (if installed):**
```bash
# List all liquid classes
liquid-class-manager list

# Show your reference data
liquid-class-manager show P1000 "Glycerol 99%"

# Export to CSV
liquid-class-manager export my_liquid_classes.csv

# Import from CSV
liquid-class-manager import my_liquid_classes.csv
```

**📖 See [CLI_README.md](CLI_README.md) for detailed CLI documentation.**

#### **Your Reference Data**

The system comes pre-configured with your optimized glycerol parameters:

```
Pipette,Liquid,Aspiration Rate (µL/s),Aspiration Delay (s),Aspiration Withdrawal Rate (mm/s),Dispense Rate (µL/s),Dispense Delay (s),Blowout Rate (µL/s),Touch tip
P1000,Glycerol 99%,41.175,20,4,19.215,20,5.0,No
```

**Key Parameters for Glycerol 99% with P1000:**
- **Aspiration Rate**: 41.175 µL/s (slow for viscous liquid)
- **Aspiration Delay**: 20 s (long delay for complete aspiration)
- **Dispense Rate**: 19.215 µL/s (very slow for controlled dispensing)
- **Touch Tip**: No (not needed for glycerol)

## Configuration Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `sample_count` | Integer | 96 | Number of wells to test (1-96) |
| `pipette_mount` | String | "right" | Mount position for pipette ("left" or "right") |
| `trash_position` | String | "A3" | Deck position for trash container |
| `liquid_type` | String | "GLYCEROL_99" | Type of liquid to calibrate for |
| `pipette_type` | String | "P1000" | Type of pipette to calibrate |

## How It Works

### **Protocol Modes**

The system supports two distinct operational modes:

#### **Single-Channel Mode** (`protocol.py`)
- **Pipettes**: Single-channel 1000µL (dispensing) + single-channel 50µL (evaluation)
- **Processing**: One well at a time for detailed optimization
- **Use Case**: Precise parameter optimization for individual wells
- **Simulation**: Use `run_simulation.py`

#### **8-Channel Mode** (`protocol_8channel.py`)
- **Pipettes**: 8-channel 1000µL (dispensing + evaluation)
- **Processing**: 8 wells simultaneously in 8-channel operations
- **Use Case**: High-throughput optimization with channel consistency analysis
- **Detection**: Real capacitive sensing or simulated detection
- **Simulation**: Use `run_simulation.py`

### 1. **Setup & Configuration**
The protocol loads:
- **Labware**: 12-well reservoir (liquid source), 96-well test plate, tip racks
- **Pipettes**: Single-channel 1000µL (dispensing), single-channel 50µL (evaluation)
- **Liquid**: Configurable liquid type (default: glycerol)

### 2. **Parameters Being Optimized**
The protocol optimizes these critical liquid handling parameters:

| Parameter | Description | Range |
|-----------|-------------|-------|
| `aspiration_rate` | Speed of liquid uptake (µL/s) | 10-500 |
| `aspiration_delay` | Wait time after aspiration (s) | 0-5 |
| `aspiration_withdrawal_rate` | Tip withdrawal speed (mm/s) | 1-20 |
| `dispense_rate` | Speed of liquid dispensing (µL/s) | 10-500 |
| `dispense_delay` | Wait time after dispensing (s) | 0-5 |
| `blowout_rate` | Speed of blowout (µL/s) | 10-300 |
| `touch_tip` | Remove droplets by touching tip | Boolean |

### 3. **Gradient Descent Algorithm**

The optimization follows this iterative process:

```
For each well:
1. Use current parameters to dispense liquid
2. Evaluate result (liquid height + bubble formation)
3. Adjust parameters based on performance
4. Repeat with improved parameters
```

**Parameter Adjustment Logic**:
- ✅ **Better result** (lower bubblicity score) → Continue in same direction
- ❌ **Worse result** → Reverse direction and reduce step size
- 🔒 **Constraints** → Keep all parameters within safe bounds

### 4. **Evaluation Metrics**

#### **Liquid Height Check**
- Verifies liquid is at expected height (2mm from bottom)
- Uses horizontal sweeps with pressure sensors
- Ensures accurate volume dispensing

#### **Bubblicity Score**
- Measures bubble formation above liquid surface
- Checks multiple heights (0.5, 1.0, 1.5, 2.0, 2.5mm above expected)
- Higher bubbles = worse score (weighted by height)
- Lower score = better performance

### 5. **Workflow Process**

For each well in the 96-well plate:

1. **Parameter Selection**: Use liquid class parameters as starting point, then gradient descent-adjusted parameters
2. **Dispense**: Execute liquid handling with current parameters
3. **Evaluate**: Check liquid height and bubble formation
4. **Record**: Store results with parameters used
5. **Optimize**: Adjust parameters for next iteration based on performance

## Output

The protocol provides:
- **Real-time feedback** on each well's performance
- **Optimal parameters** for the liquid class
- **Performance metrics** (height status, bubblicity scores)
- **Parameter evolution** throughout the optimization process

## Example Output

```
Well A1: Height OK: True, Bubblicity: 0.00
Well B1: Height OK: True, Bubblicity: 0.50
Well C1: Height OK: True, Bubblicity: 0.00
...
Optimal parameters found in A1
Optimal bubblicity score: 0.00
Optimal parameters: {'aspiration_rate': 41.175, 'aspiration_delay': 20.0, ...}
```

## Technical Details

### **Gradient Descent Implementation**
The protocol uses a simplified gradient descent approach:
- **Learning rate**: 0.1 (controls step size)
- **Gradient steps**: Parameter-specific adjustment amounts
- **Constraint enforcement**: Keeps parameters within operational bounds
- **Direction reversal**: Adapts when performance degrades

### **Evaluation Strategy**
- **Multi-point sampling**: Checks multiple positions within each well
- **Height-based weighting**: Higher bubbles penalized more heavily
- **Pressure-based detection**: Uses pipette pressure sensors for liquid detection
- **Error handling**: Graceful handling of detection failures

### **Detection System**

The 8-channel mode includes a sophisticated detection system with two modes:

#### **Real Detection Mode**
- **Capacitive Sensing**: Uses `pipette.aspirate(0)` to detect liquid presence
- **Height Verification**: Checks liquid at expected height (2mm from bottom)
- **Bubble Detection**: Scans multiple heights above liquid surface
- **Sensor Integration**: Leverages actual pipette pressure sensors
- **Physical Robot**: Designed for use on actual Opentrons machines

#### **Simulated Detection Mode**
- **Consistent Results**: 95% success rate for reliable testing
- **Fast Execution**: No sensor delays for rapid iteration
- **Development Friendly**: Perfect for algorithm testing and optimization
- **Deterministic**: Same inputs produce same outputs
- **Simulation Environment**: Optimized for Opentrons simulation

#### **Detection Parameters**
- **Expected Liquid Height**: 2.0mm from well bottom
- **Bubble Check Increments**: [0.5, 1.0, 1.5, 2.0, 2.5]mm above expected
- **Horizontal Sweep Points**: 5-point pattern for comprehensive coverage
- **Success Threshold**: Configurable detection sensitivity

### **Liquid Class System Architecture**
- **Registry Pattern**: Centralized storage with type safety
- **CSV Format**: Standard data exchange format
- **Enum-based Types**: Prevents errors with invalid pipette/liquid combinations
- **Protocol Integration**: Seamless integration with Opentrons protocols

## Development

### **Prerequisites**

- Python 3.8 or higher
- pip (Python package installer)
- Git

### **Quick Start for Developers**

1. **Clone the repository**:
   ```bash
   git clone https://github.com/opentrons/liquid-class-finder.git
   cd liquid-class-finder
   ```

2. **Set up development environment**:
   ```bash
   # Using Makefile (recommended)
   make dev-setup

   # Or manually:
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -e ".[dev]"
   pre-commit install
   ```

3. **Verify installation**:
   ```bash
   make check
   ```

4. **Test the liquid class system**:
   ```bash
   python -m pytest tests/test_liquid_classes.py
   python -m liquids.liquid_class_demo_basic
   ```

### **Development Workflow**

#### **Available Commands**

```bash
# Show all available commands
make help

# Install dependencies
make install          # Production dependencies only
make install-dev      # Include development dependencies

# Code quality
make format           # Format code with black
make format-check     # Check formatting without changing
make lint             # Run linting (flake8 + mypy)

# Testing
make test             # Run tests
make test-cov         # Run tests with coverage report

# Cleanup
make clean            # Remove generated files

# Full check
make check            # Run format-check + lint + test
```

#### **Pre-commit Hooks**

The project uses pre-commit hooks to ensure code quality:

- **Trailing whitespace removal**
- **End-of-file fixer**
- **YAML validation**
- **Code formatting with Black**
- **Linting with flake8**
- **Type checking with mypy**

Hooks run automatically on commit. To run manually:
```bash
pre-commit run --all-files
```

#### **Testing**

The test suite uses pytest and includes:

- **Unit tests** for protocol components
- **Mock testing** for Opentrons API interactions
- **Coverage reporting** to ensure comprehensive testing
- **Liquid class system tests** for parameter management

Run tests:
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_protocol.py
pytest test_liquid_classes.py

# Run with verbose output
pytest -v
```

#### **Code Style**

The project follows these style guidelines:

- **Black**: Code formatting (88 character line length)
- **flake8**: Linting with specific rule exceptions
- **mypy**: Static type checking
- **Docstrings**: Google-style docstrings for functions and classes

#### **Project Structure**

```
liquid-class-finder/
├── protocol.py              # Main single-channel protocol file
├── protocol_8channel_single.py  # 8-channel protocol file
├── protocol_env.py          # Environment-based protocol
├── run_simulation.py        # 🚀 Unified simulation & testing tool (single + 8-channel)
├── liquids/                 # Liquid class system
│   ├── liquid_classes.py        # Core liquid class system
│   ├── liquid_class_manager.py  # Command-line management utility
│   ├── liquid_class_demo_basic.py  # Basic demonstration script
│   ├── liquid_class_demo_custom.py # Comprehensive demonstration script
│   └── liquid_classes.csv       # Default liquid class data
├── tests/                  # Test suite
│   ├── __init__.py
│   ├── test_protocol.py
│   ├── test_liquid_classes.py
│   ├── test_protocol_import.py
│   ├── test_optimization.py
│   └── test_logging.py
├── config/                 # Configuration files
│   └── example_config.json
├── scripts/                # Utility scripts
│   └── setup_dev.py
├── docs/                   # Documentation
│   └── LIQUID_CLASS_README.md
├── requirements.txt        # Production dependencies
├── pyproject.toml         # Project configuration
├── Makefile               # Development commands
├── .pre-commit-config.yaml # Pre-commit hooks
├── .gitignore            # Git ignore patterns
└── README.md             # This file
```

#### **Adding New Features**

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the code style guidelines

3. **Add tests** for new functionality

4. **Run checks**:
   ```bash
   make check
   ```

5. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Add feature: description"
   ```

6. **Push and create a pull request**

#### **Debugging**

For debugging Opentrons protocols:

1. **Use the Opentrons App** for simulation
2. **Add debug comments** using `protocol.comment()`
3. **Test with mock data** in the test suite
4. **Use the Opentrons Protocol Designer** for visual debugging

For debugging liquid class system:

1. **Run the demo script**: `python -m liquids.liquid_class_demo_basic`
2. **Use the manager utility**: `python -m liquids.liquid_class_manager list`
3. **Run tests**: `python -m pytest tests/test_liquid_classes.py`

#### **Dependencies**

- **Production**: `opentrons>=6.3.0`
- **Development**: pytest, black, flake8, mypy, pre-commit

To add new dependencies:
1. Add to `pyproject.toml` under `dependencies` or `[project.optional-dependencies.dev]`
2. Update `requirements.txt` if needed
3. Run `pip install -e ".[dev]"` to install

### **Contributing Guidelines**

- Follow the existing code style and structure
- Add tests for new functionality
- Update documentation as needed
- Use descriptive commit messages
- Ensure all checks pass before submitting

## Contributing

This protocol is designed to be extensible. Consider contributing:
- Additional evaluation metrics
- Different optimization algorithms
- Support for other liquid types
- Enhanced parameter sets
- New liquid class features
- Improved CSV import/export formats

## License

This protocol is provided as-is for educational and research purposes. Please ensure compliance with your institution's safety and operational guidelines.
