# Optimization Strategy Architecture

## Overview

The liquid class calibration system now supports a pluggable optimization architecture that allows different optimization strategies to be used interchangeably. This provides flexibility in choosing the most appropriate optimization approach for different liquid types and experimental conditions.

## Architecture Components

### 1. Abstract Base Class: `OptimizationStrategy`

The `OptimizationStrategy` abstract base class defines the interface that all optimization strategies must implement:

```python
class OptimizationStrategy(ABC):
    def generate_parameters(self, well_idx: int, well_data: List[Dict[str, Any]],
                          learning_rate: float) -> Dict[str, float]:
        """Generate parameters for the next well"""
        pass

    def get_strategy_name(self) -> str:
        """Get the name of this optimization strategy"""
        pass

    def get_strategy_description(self) -> str:
        """Get description of this optimization strategy"""
        pass
```

### 2. Strategy Factory: `OptimizationStrategyFactory`

The factory pattern provides a clean way to create optimization strategies:

```python
strategy = OptimizationStrategyFactory.create_strategy(
    "hybrid", reference_params, param_bounds
)
```

## Available Strategies

### 1. Simultaneous Gradient Descent (`simultaneous`)

**Description**: Optimizes all 6 parameters simultaneously using gradient descent

**Characteristics**:
- **Parameters**: All 6 liquid handling parameters
- **Approach**: Traditional gradient descent on all parameters at once
- **Best for**: Well-behaved liquids (water, simple buffers)
- **Pros**: Captures parameter interactions, efficient for smooth landscapes
- **Cons**: May get stuck in local minima, requires more data per iteration

**Implementation Details**:
- Uses finite difference gradients between consecutive wells
- Applies learning rate and step size to each parameter
- Constrains parameters to valid bounds

### 2. Hybrid Hierarchical Optimization (`hybrid`)

**Description**: Hierarchical optimization in phases followed by fine-tuning

**Phases**:
1. **Flow Rates** (wells 0-23): Optimize `aspiration_rate`, `dispense_rate`, `blowout_rate`
2. **Delays** (wells 24-47): Optimize `aspiration_delay`, `dispense_delay`
3. **Withdrawal** (wells 48-59): Optimize `aspiration_withdrawal_rate`
4. **Fine-tuning** (wells 60-95): Optimize all 6 parameters with smaller step sizes

**Characteristics**:
- **Best for**: Complex liquids (viscous, volatile, multi-component)
- **Pros**: Systematic approach, good for complex landscapes
- **Cons**: May miss global optima, longer total runtime

**Implementation Details**:
- Each phase uses phase-specific step sizes
- Best parameters from each phase carry forward to the next
- Fine-tuning phase uses smaller step sizes for precision

### 3. Coordinate Descent (`coordinate`)

**Description**: Optimizes one parameter at a time in cycling order

**Characteristics**:
- **Parameters**: Cycles through parameters: aspiration_rate → dispense_rate → blowout_rate → aspiration_delay → dispense_delay → aspiration_withdrawal_rate
- **Best for**: Initial exploration or when computational budget is limited
- **Pros**: Simple, robust, good for high-dimensional spaces
- **Cons**: May converge slowly, doesn't capture interactions

**Implementation Details**:
- Changes parameter every 3 wells
- Only optimizes the current parameter while keeping others fixed
- Uses coordinate-wise gradient descent

## Usage in Protocols

### Protocol Parameter Selection

Add the optimization strategy parameter to your protocol:

```python
def add_parameters(parameters):
    # ... other parameters ...
    parameters.add_str(
        display_name="Optimization strategy",
        variable_name="optimization_strategy",
        choices=[
            {"display_name": "Simultaneous Gradient Descent", "value": "simultaneous"},
            {"display_name": "Hybrid Hierarchical", "value": "hybrid"},
            {"display_name": "Coordinate Descent", "value": "coordinate"},
        ],
        default="simultaneous",
        description="Optimization strategy to use for parameter tuning",
    )
```

### Strategy Initialization

Initialize the strategy in your protocol:

```python
# Initialize optimization strategy
try:
    optimization_strategy = OptimizationStrategyFactory.create_strategy(
        OPTIMIZATION_STRATEGY, reference_params, param_bounds
    )
    protocol.comment(f"✅ Using optimization strategy: {optimization_strategy.get_strategy_name()}")
    protocol.comment(f"📝 Strategy description: {optimization_strategy.get_strategy_description()}")
except ValueError as e:
    protocol.comment(f"❌ Error creating optimization strategy: {e}")
    return
```

### Parameter Generation

Use the strategy to generate parameters for each well:

```python
# Generate parameters using the optimization strategy
current_params = optimization_strategy.generate_parameters(well_idx, well_data, learning_rate)

# Log parameter generation
if well_idx == 0:
    protocol.comment("Using reference liquid class parameters for first well")
else:
    protocol.comment(f"Generated parameters using {optimization_strategy.get_strategy_name()}")
    # Check for phase information (hybrid strategy specific)
    current_phase = getattr(optimization_strategy, 'current_phase', None)
    if current_phase:
        protocol.comment(f"Current phase: {current_phase}")
```

### Result Recording

Record results in the strategy for history tracking:

```python
# Record result in optimization strategy
optimization_strategy.record_result(well_idx, current_params, bubblicity_score, height_status, learning_rate)
```

## Strategy Selection Guidelines

### Choose **Simultaneous** when:
- Working with well-behaved liquids (water, simple buffers)
- You have sufficient wells (96 wells recommended)
- Parameter interactions are expected to be smooth
- You want the fastest convergence

### Choose **Hybrid** when:
- Working with complex liquids (viscous, volatile, multi-component)
- You want a systematic approach to optimization
- Parameter interactions are complex or unknown
- You have time for a thorough optimization

### Choose **Coordinate** when:
- You have limited computational budget
- You want to understand individual parameter effects
- The optimization landscape is expected to be rugged
- You're doing initial exploration of a new liquid type

## Mathematical Comparison

### Simultaneous Optimization
- **Gradient**: ∇f(θ) = [∂f/∂θ₁, ∂f/∂θ₂, ..., ∂f/∂θ₆]
- **Update**: θᵗ⁺¹ = θᵗ + α∇f(θᵗ)
- **Complexity**: O(6) per iteration

### Hybrid Optimization
- **Phase 1**: ∇f(θ) = [∂f/∂θ₁, ∂f/∂θ₃, ∂f/∂θ₆] (flow rates)
- **Phase 2**: ∇f(θ) = [∂f/∂θ₂, ∂f/∂θ₄] (delays)
- **Phase 3**: ∇f(θ) = [∂f/∂θ₅] (withdrawal)
- **Phase 4**: ∇f(θ) = [∂f/∂θ₁, ∂f/∂θ₂, ..., ∂f/∂θ₆] (fine-tuning)
- **Complexity**: O(3) → O(2) → O(1) → O(6)

### Coordinate Descent
- **Gradient**: ∇ᵢf(θ) = ∂f/∂θᵢ (single coordinate)
- **Update**: θᵢᵗ⁺¹ = θᵢᵗ + α∇ᵢf(θᵗ)
- **Complexity**: O(1) per iteration

## Extending the Architecture

### Adding New Strategies

To add a new optimization strategy:

1. Create a new class inheriting from `OptimizationStrategy`
2. Implement the required abstract methods
3. Add the strategy to the factory

```python
class MyCustomStrategy(OptimizationStrategy):
    def generate_parameters(self, well_idx, well_data, learning_rate):
        # Your custom parameter generation logic
        pass

    def get_strategy_name(self):
        return "My Custom Strategy"

    def get_strategy_description(self):
        return "Description of my custom approach"

# Add to factory
class OptimizationStrategyFactory:
    @staticmethod
    def create_strategy(strategy_name, reference_params, param_bounds):
        if strategy_name.lower() == "my_custom":
            return MyCustomStrategy(reference_params, param_bounds)
        # ... existing strategies ...
```

### Customizing Existing Strategies

You can customize existing strategies by:

1. Subclassing and overriding methods
2. Modifying step sizes and learning rates
3. Adding custom constraints or evaluation functions

## Testing

Run the test script to see all strategies in action:

```bash
python test_optimization_strategies.py
```

This will demonstrate:
- Parameter generation for each strategy
- Strategy-specific behavior
- Performance characteristics
- Usage recommendations

## Performance Considerations

### Computational Complexity
- **Simultaneous**: O(6) per well, most efficient for smooth landscapes
- **Hybrid**: O(3-6) per well, balanced approach
- **Coordinate**: O(1) per well, most robust for rugged landscapes

### Memory Usage
- All strategies maintain optimization history
- Hybrid strategy has additional phase tracking
- Memory usage is generally low (< 1MB for 96 wells)

### Convergence Properties
- **Simultaneous**: Fastest convergence for smooth functions
- **Hybrid**: Systematic convergence, good for complex landscapes
- **Coordinate**: Slowest convergence but most robust

## Future Enhancements

Potential improvements to the architecture:

1. **Adaptive Strategies**: Automatically switch strategies based on performance
2. **Multi-Objective Optimization**: Optimize for multiple criteria (bubblicity, speed, accuracy)
3. **Bayesian Optimization**: Use probabilistic models for parameter selection
4. **Parallel Optimization**: Run multiple strategies simultaneously
5. **Strategy Ensembles**: Combine multiple strategies for better performance
