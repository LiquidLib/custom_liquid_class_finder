# Liquid Class Calibration with Gradient Descent

An intelligent Opentrons protocol that automatically optimizes liquid handling parameters for viscous liquids using gradient descent optimization. This protocol minimizes bubble formation and ensures accurate liquid dispensing for challenging liquids like glycerol.

## Overview

This protocol solves a critical problem in automated liquid handling: **optimizing liquid class parameters for viscous liquids**. Traditional manual calibration is time-consuming and error-prone. This protocol uses machine learning principles (gradient descent) to automatically find the best parameters through systematic testing.

## Key Features

- 🤖 **Automated Optimization**: Uses gradient descent to find optimal parameters
- 🧪 **Viscous Liquid Support**: Specifically designed for challenging liquids like glycerol
- 📊 **Dual Evaluation**: Checks both liquid height accuracy and bubble formation
- 🔧 **Parameter Constraints**: Ensures all parameters stay within safe operational bounds
- 📈 **Real-time Learning**: Adjusts parameters based on previous results
- 🎯 **Optimal Results**: Identifies the best-performing parameter set

## How It Works

### 1. **Setup & Configuration**
The protocol loads:
- **Labware**: 12-well reservoir (glycerol source), 96-well test plate, tip racks
- **Pipettes**: 8-channel 1000µL (dispensing), 8-channel 50µL (evaluation)
- **Liquid**: 100% glycerol as the test liquid

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
For each well (column):
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

For each column in the 96-well plate:

1. **Parameter Selection**: Use reference parameters for first well, then gradient descent-adjusted parameters
2. **Dispense**: Execute liquid handling with current parameters
3. **Evaluate**: Check liquid height and bubble formation
4. **Record**: Store results with parameters used
5. **Optimize**: Adjust parameters for next iteration based on performance

## Requirements

- **Robot Type**: Opentrons Flex
- **API Level**: 2.22
- **Labware**:
  - `nest_12_reservoir_15ml` (reservoir)
  - `nest_96_wellplate_200ul_flat` (test plate)
  - `opentrons_flex_96_filtertiprack_1000ul` (1000µL tips)
  - `opentrons_flex_96_filtertiprack_50ul` (50µL tips)
- **Pipettes**:
  - `flex_8channel_1000` (8-channel 1000µL)
  - `flex_8channel_50` (8-channel 50µL)

## Configuration Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `sample_count` | Integer | 96 | Number of wells to test (1-96) |
| `pipette_mount` | String | "right" | Mount position for 8-channel pipette ("left" or "right") |

## Usage

1. **Load the Protocol**: Upload `protocol.py` to your Opentrons App
2. **Configure Parameters**: Set sample count and pipette mount as needed
3. **Prepare Labware**: Ensure all required labware is loaded and positioned
4. **Add Glycerol**: Load 15mL of 100% glycerol in reservoir position A1
5. **Run Protocol**: Execute the protocol and monitor progress
6. **Review Results**: Check the protocol comments for optimal parameters

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
Optimal parameters: {'aspiration_rate': 150.0, 'aspiration_delay': 1.0, ...}
```

## Why This Matters

### **Problem Solved**
- **Viscous liquids** like glycerol are notoriously difficult to handle accurately
- **Bubble formation** can ruin experiments and waste expensive reagents
- **Manual optimization** of liquid class parameters is time-consuming and error-prone
- **Inconsistent results** from manual calibration

### **Benefits**
- **Automated optimization** ensures consistent, reproducible results
- **Systematic approach** eliminates human bias and error
- **Time savings** compared to manual trial-and-error
- **Better performance** through data-driven parameter selection
- **Scalable** to different liquids and conditions

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

Run tests:
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_protocol.py

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
├── protocol.py              # Main protocol file
├── requirements.txt         # Production dependencies
├── pyproject.toml          # Project configuration
├── Makefile                # Development commands
├── .pre-commit-config.yaml # Pre-commit hooks
├── .gitignore             # Git ignore patterns
├── tests/                 # Test suite
│   ├── __init__.py
│   └── test_protocol.py
└── README.md              # This file
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

#### **Dependencies**

- **Production**: `opentrons>=6.3.0`, `opentrons-protocol-api>=2.22.0`
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

## License

This protocol is provided as-is for educational and research purposes. Please ensure compliance with your institution's safety and operational guidelines.
