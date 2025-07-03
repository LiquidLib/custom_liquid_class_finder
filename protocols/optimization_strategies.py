"""
Optimization Strategy Plugins for Liquid Class Calibration

This module provides a pluggable architecture for different optimization strategies
used in liquid class calibration protocols. Each strategy implements the same interface
but uses different approaches to parameter optimization.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple


class OptimizationStrategy(ABC):
    """Abstract base class for optimization strategies"""

    def __init__(
        self, reference_params: Dict[str, float], param_bounds: Dict[str, Tuple[float, float]]
    ):
        """
        Initialize optimization strategy

        Args:
            reference_params: Reference parameters to start optimization from
            param_bounds: Parameter bounds (min, max) for each parameter
        """
        self.reference_params = reference_params
        self.param_bounds = param_bounds
        self.optimization_history: List[Dict[str, Any]] = []
        self.best_score = float("inf")
        self.best_params = reference_params.copy()

    @staticmethod
    def calculate_pipette_specific_bounds(
        pipette_type: str, liquid_type: str = "WATER"
    ) -> Dict[str, Tuple[float, float]]:
        """
        Calculate reasonable parameter bounds based on pipette type and liquid type

        Args:
            pipette_type: Type of pipette (P20, P50, P300, P1000)
            liquid_type: Type of liquid being handled

        Returns:
            Dictionary of parameter bounds (min, max) for each parameter
        """
        # Base bounds for different pipette types
        pipette_bounds = {
            "P20": {
                "aspiration_rate": (1.0, 20.0),  # 1-20 μL/sec
                "dispense_rate": (1.0, 20.0),  # 1-20 μL/sec
                "blowout_rate": (0.5, 10.0),  # 0.5-10 μL/sec
                "aspiration_withdrawal_rate": (0.5, 5.0),  # 0.5-5 μL/sec
            },
            "P50": {
                "aspiration_rate": (2.0, 50.0),  # 2-50 μL/sec
                "dispense_rate": (2.0, 50.0),  # 2-50 μL/sec
                "blowout_rate": (1.0, 20.0),  # 1-20 μL/sec
                "aspiration_withdrawal_rate": (1.0, 10.0),  # 1-10 μL/sec
            },
            "P300": {
                "aspiration_rate": (5.0, 150.0),  # 5-150 μL/sec
                "dispense_rate": (5.0, 150.0),  # 5-150 μL/sec
                "blowout_rate": (2.0, 50.0),  # 2-50 μL/sec
                "aspiration_withdrawal_rate": (1.0, 15.0),  # 1-15 μL/sec
            },
            "P1000": {
                "aspiration_rate": (10.0, 300.0),  # 10-300 μL/sec
                "dispense_rate": (10.0, 300.0),  # 10-300 μL/sec
                "blowout_rate": (5.0, 150.0),  # 5-150 μL/sec
                "aspiration_withdrawal_rate": (2.0, 25.0),  # 2-25 μL/sec
            },
        }

        # Get base bounds for pipette type
        if pipette_type not in pipette_bounds:
            # Default to P1000 if unknown
            pipette_type = "P1000"

        bounds = pipette_bounds[pipette_type].copy()

        # Add delay bounds (same for all pipettes, but liquid-dependent)
        if liquid_type in ["DMSO", "ETHANOL"]:
            # Volatile liquids need shorter delays
            bounds.update(
                {
                    "aspiration_delay": (0.0, 1.0),  # 0-1 seconds
                    "dispense_delay": (0.0, 1.0),  # 0-1 seconds
                }
            )
        elif liquid_type in ["GLYCEROL_99", "PEG_8000_50", "ENGINE_OIL_100"]:
            # Viscous liquids can benefit from longer delays
            bounds.update(
                {
                    "aspiration_delay": (0.0, 3.0),  # 0-3 seconds
                    "dispense_delay": (0.0, 3.0),  # 0-3 seconds
                }
            )
        else:
            # Standard delays for most liquids
            bounds.update(
                {
                    "aspiration_delay": (0.0, 2.0),  # 0-2 seconds
                    "dispense_delay": (0.0, 2.0),  # 0-2 seconds
                }
            )

        return bounds

    @staticmethod
    def get_default_bounds() -> Dict[str, Tuple[float, float]]:
        """
        Get default parameter bounds (fallback for backward compatibility)

        Returns:
            Dictionary of default parameter bounds
        """
        return {
            "aspiration_rate": (10.0, 300.0),
            "aspiration_delay": (0.0, 2.0),
            "aspiration_withdrawal_rate": (1.0, 20.0),
            "dispense_rate": (10.0, 300.0),
            "dispense_delay": (0.0, 2.0),
            "blowout_rate": (5.0, 150.0),
        }

    @abstractmethod
    def generate_parameters(
        self, well_idx: int, well_data: List[Dict[str, Any]], learning_rate: float
    ) -> Dict[str, float]:
        """
        Generate parameters for the next well

        Args:
            well_idx: Current well index (0-based)
            well_data: List of previous well results
            learning_rate: Current learning rate

        Returns:
            Dictionary of parameters for the next well
        """
        pass

    @abstractmethod
    def get_strategy_name(self) -> str:
        """Get the name of this optimization strategy"""
        pass

    @abstractmethod
    def get_strategy_description(self) -> str:
        """Get description of this optimization strategy"""
        pass

    def apply_constraints(self, params: Dict[str, float]) -> Dict[str, float]:
        """Apply parameter constraints to keep values within bounds"""
        constrained_params = params.copy()
        for param, (min_val, max_val) in self.param_bounds.items():
            if param in constrained_params:
                constrained_params[param] = max(min_val, min(max_val, constrained_params[param]))
        return constrained_params

    def record_result(
        self,
        well_idx: int,
        parameters: Dict[str, float],
        score: float,
        height_status: bool,
        learning_rate: float,
    ):
        """Record optimization result for history tracking"""
        self.optimization_history.append(
            {
                "iteration": well_idx,
                "parameters": parameters.copy(),
                "score": score,
                "height_status": height_status,
                "learning_rate": learning_rate,
                "best_score": self.best_score,
            }
        )

        if height_status and score < self.best_score:
            self.best_score = score
            self.best_params = parameters.copy()


class SimultaneousOptimizationStrategy(OptimizationStrategy):
    """Simultaneous optimization of all parameters using gradient descent"""

    def __init__(
        self, reference_params: Dict[str, float], param_bounds: Dict[str, Tuple[float, float]]
    ):
        super().__init__(reference_params, param_bounds)

        # Gradient descent parameters
        self.gradient_step = {
            "aspiration_rate": 10.0,
            "aspiration_delay": 0.05,
            "aspiration_withdrawal_rate": 0.5,
            "dispense_rate": 10.0,
            "dispense_delay": 0.05,
            "blowout_rate": 5.0,
        }

    def get_strategy_name(self) -> str:
        return "Simultaneous Gradient Descent"

    def get_strategy_description(self) -> str:
        return "Optimizes all 6 parameters simultaneously using gradient descent"

    def calculate_gradient_direction(
        self,
        previous_score: float,
        current_score: float,
        previous_params: Dict[str, float],
        current_params: Dict[str, float],
    ) -> Dict[str, float]:
        """Calculate gradient direction for each parameter"""
        if previous_score == float("inf"):
            return {param: 0.0 for param in self.gradient_step.keys()}

        gradients = {}
        for param in self.gradient_step.keys():
            if param in previous_params and param in current_params:
                param_change = current_params[param] - previous_params[param]
                if abs(param_change) > 1e-6:  # Avoid division by zero
                    score_change = current_score - previous_score
                    gradients[param] = -score_change / param_change
                else:
                    gradients[param] = 0.0
            else:
                gradients[param] = 0.0

        return gradients

    def update_parameters_with_gradient(
        self, current_params: Dict[str, float], gradients: Dict[str, float], learning_rate: float
    ) -> Dict[str, float]:
        """Update parameters using calculated gradients"""
        updated_params = current_params.copy()

        for param, gradient in gradients.items():
            if param in updated_params:
                step = learning_rate * self.gradient_step[param] * gradient
                updated_params[param] += step

        return updated_params

    def generate_parameters(
        self, well_idx: int, well_data: List[Dict[str, Any]], learning_rate: float
    ) -> Dict[str, float]:
        """Generate parameters using simultaneous gradient descent"""

        if well_idx == 0:
            # First well - use reference parameters
            return self.reference_params.copy()

        elif well_idx == 1:
            # Second well - simple exploration
            current_params = self.reference_params.copy()
            for param in self.gradient_step.keys():
                if param in current_params:
                    adjustment = well_idx * self.gradient_step[param] * 0.1
                    current_params[param] += adjustment
            return self.apply_constraints(current_params)

        else:
            # Subsequent wells - gradient descent
            if len(well_data) >= 2:
                last_result = well_data[-1]
                second_last_result = well_data[-2]

                # Calculate gradients
                gradients = self.calculate_gradient_direction(
                    second_last_result["bubblicity_score"],
                    last_result["bubblicity_score"],
                    second_last_result["parameters"],
                    last_result["parameters"],
                )

                # Update parameters
                current_params = self.update_parameters_with_gradient(
                    last_result["parameters"], gradients, learning_rate
                )

                return self.apply_constraints(current_params)
            else:
                # Fallback to exploration
                return self.reference_params.copy()


class HybridOptimizationStrategy(OptimizationStrategy):
    """Hybrid optimization using hierarchical phases followed by fine-tuning"""

    def __init__(
        self,
        reference_params: Dict[str, float],
        param_bounds: Dict[str, Tuple[float, float]],
        sample_count: int = 96,
    ):
        super().__init__(reference_params, param_bounds)

        # Calculate proportional wells per phase based on sample count
        self.sample_count = sample_count
        self.phase_configs = self._calculate_phase_allocation(sample_count)

        # Phase tracking
        self.current_phase = "flow_rates"
        self.phase_start_well = 0
        self.phase_best_params = self.reference_params.copy()

    def _calculate_phase_allocation(self, sample_count: int) -> Dict[str, Dict[str, Any]]:
        """Calculate proportional wells per phase based on sample count"""

        # Original proportions for 96 wells:
        # flow_rates: 24/96 = 25%
        # delays: 24/96 = 25%
        # withdrawal: 12/96 = 12.5%
        # fine_tune: 36/96 = 37.5%

        # Calculate proportional allocation
        flow_rates_wells = max(1, int(sample_count * 0.25))  # 25%
        delays_wells = max(1, int(sample_count * 0.25))  # 25%
        withdrawal_wells = max(1, int(sample_count * 0.125))  # 12.5%
        fine_tune_wells = (
            sample_count - flow_rates_wells - delays_wells - withdrawal_wells
        )  # Remaining

        # Ensure we don't exceed sample count
        total_allocated = flow_rates_wells + delays_wells + withdrawal_wells + fine_tune_wells
        if total_allocated > sample_count:
            # Adjust fine_tune to fit
            fine_tune_wells = max(
                1, sample_count - flow_rates_wells - delays_wells - withdrawal_wells
            )

        return {
            "flow_rates": {
                "params": ["aspiration_rate", "dispense_rate", "blowout_rate"],
                "step_sizes": {"aspiration_rate": 10.0, "dispense_rate": 10.0, "blowout_rate": 5.0},
                "wells_per_phase": flow_rates_wells,
                "description": f"Flow rate optimization (3 parameters, {flow_rates_wells} wells)",
            },
            "delays": {
                "params": ["aspiration_delay", "dispense_delay"],
                "step_sizes": {"aspiration_delay": 0.05, "dispense_delay": 0.05},
                "wells_per_phase": delays_wells,
                "description": f"Delay optimization (2 parameters, {delays_wells} wells)",
            },
            "withdrawal": {
                "params": ["aspiration_withdrawal_rate"],
                "step_sizes": {"aspiration_withdrawal_rate": 0.5},
                "wells_per_phase": withdrawal_wells,
                "description": (
                    f"Withdrawal rate optimization (1 parameter, {withdrawal_wells} wells)"
                ),
            },
            "fine_tune": {
                "params": [
                    "aspiration_rate",
                    "aspiration_delay",
                    "aspiration_withdrawal_rate",
                    "dispense_rate",
                    "dispense_delay",
                    "blowout_rate",
                ],
                "step_sizes": {
                    "aspiration_rate": 5.0,
                    "aspiration_delay": 0.02,
                    "aspiration_withdrawal_rate": 0.2,
                    "dispense_rate": 5.0,
                    "dispense_delay": 0.02,
                    "blowout_rate": 2.0,
                },
                "wells_per_phase": fine_tune_wells,
                "description": (
                    f"Fine-tuning all parameters (6 parameters, {fine_tune_wells} wells)"
                ),
            },
        }

        # Phase tracking
        self.current_phase = "flow_rates"
        self.phase_start_well = 0
        self.phase_best_params = self.reference_params.copy()

    def get_strategy_name(self) -> str:
        return "Hybrid Hierarchical Optimization"

    def get_strategy_description(self) -> str:
        return "Hierarchical optimization: Flow rates → Delays → Withdrawal → Fine-tuning"

    def get_current_phase(self, well_idx: int) -> str:
        """Determine current optimization phase based on well index"""
        wells_used = 0
        for phase_name, config in self.phase_configs.items():
            wells_used += config["wells_per_phase"]
            if well_idx < wells_used:
                return phase_name
        return "fine_tune"  # Default to fine-tuning phase

    def get_phase_parameters(self, phase: str) -> List[str]:
        """Get parameters optimized in the current phase"""
        return self.phase_configs[phase]["params"]

    def get_phase_step_sizes(self, phase: str) -> Dict[str, float]:
        """Get step sizes for the current phase"""
        return self.phase_configs[phase]["step_sizes"]

    def calculate_phase_gradient(
        self,
        phase: str,
        previous_score: float,
        current_score: float,
        previous_params: Dict[str, float],
        current_params: Dict[str, float],
    ) -> Dict[str, float]:
        """Calculate gradient for parameters in the current phase"""
        if previous_score == float("inf"):
            return {param: 0.0 for param in self.get_phase_parameters(phase)}

        gradients = {}

        for param in self.get_phase_parameters(phase):
            if param in previous_params and param in current_params:
                param_change = current_params[param] - previous_params[param]
                if abs(param_change) > 1e-6:
                    score_change = current_score - previous_score
                    gradients[param] = -score_change / param_change
                else:
                    gradients[param] = 0.0
            else:
                gradients[param] = 0.0

        return gradients

    def update_phase_parameters(
        self,
        phase: str,
        current_params: Dict[str, float],
        gradients: Dict[str, float],
        learning_rate: float,
    ) -> Dict[str, float]:
        """Update parameters for the current phase"""
        updated_params = current_params.copy()
        step_sizes = self.get_phase_step_sizes(phase)

        for param, gradient in gradients.items():
            if param in updated_params and param in step_sizes:
                step = learning_rate * step_sizes[param] * gradient
                updated_params[param] += step

        return updated_params

    def generate_parameters(
        self, well_idx: int, well_data: List[Dict[str, Any]], learning_rate: float
    ) -> Dict[str, float]:
        """Generate parameters using hybrid hierarchical approach"""

        # Determine current phase
        current_phase = self.get_current_phase(well_idx)

        # Check if we're starting a new phase
        if current_phase != self.current_phase:
            self.current_phase = current_phase
            self.phase_start_well = well_idx
            # Use best parameters from previous phase as starting point
            if well_data:
                self.phase_best_params = well_data[-1]["parameters"].copy()

        if well_idx == 0:
            # First well - use reference parameters
            return self.reference_params.copy()

        elif well_idx == self.phase_start_well:
            # First well of a new phase - use best from previous phase
            return self.phase_best_params.copy()

        elif well_idx == self.phase_start_well + 1:
            # Second well of phase - simple exploration
            current_params = self.phase_best_params.copy()
            phase_params = self.get_phase_parameters(current_phase)
            step_sizes = self.get_phase_step_sizes(current_phase)

            for param in phase_params:
                if param in current_params and param in step_sizes:
                    adjustment = step_sizes[param] * 0.1
                    current_params[param] += adjustment

            return self.apply_constraints(current_params)

        else:
            # Subsequent wells in phase - phase-specific gradient descent
            phase_well_data = [d for d in well_data if d.get("phase") == current_phase]

            if len(phase_well_data) >= 2:
                last_result = phase_well_data[-1]
                second_last_result = phase_well_data[-2]

                # Calculate gradients for current phase parameters
                gradients = self.calculate_phase_gradient(
                    current_phase,
                    second_last_result["bubblicity_score"],
                    last_result["bubblicity_score"],
                    second_last_result["parameters"],
                    last_result["parameters"],
                )

                # Update parameters for current phase only
                current_params = self.update_phase_parameters(
                    current_phase, last_result["parameters"], gradients, learning_rate
                )

                return self.apply_constraints(current_params)
            else:
                # Fallback to exploration
                return self.phase_best_params.copy()

    def record_result(
        self,
        well_idx: int,
        parameters: Dict[str, float],
        score: float,
        height_status: bool,
        learning_rate: float,
    ):
        """Record optimization result with phase information"""
        current_phase = self.get_current_phase(well_idx)

        self.optimization_history.append(
            {
                "iteration": well_idx,
                "phase": current_phase,
                "parameters": parameters.copy(),
                "score": score,
                "height_status": height_status,
                "learning_rate": learning_rate,
                "best_score": self.best_score,
            }
        )

        if height_status and score < self.best_score:
            self.best_score = score
            self.best_params = parameters.copy()


class CoordinateDescentOptimizationStrategy(OptimizationStrategy):
    """Coordinate descent optimization - optimize one parameter at a time"""

    def __init__(
        self, reference_params: Dict[str, float], param_bounds: Dict[str, Tuple[float, float]]
    ):
        super().__init__(reference_params, param_bounds)

        # Parameter order for coordinate descent
        self.param_order = [
            "aspiration_rate",
            "dispense_rate",
            "blowout_rate",
            "aspiration_delay",
            "dispense_delay",
            "aspiration_withdrawal_rate",
        ]

        # Step sizes for each parameter
        self.step_sizes = {
            "aspiration_rate": 10.0,
            "aspiration_delay": 0.05,
            "aspiration_withdrawal_rate": 0.5,
            "dispense_rate": 10.0,
            "dispense_delay": 0.05,
            "blowout_rate": 5.0,
        }

        self.current_param_index = 0
        self.param_cycle_count = 0

    def get_strategy_name(self) -> str:
        return "Coordinate Descent"

    def get_strategy_description(self) -> str:
        return "Optimizes one parameter at a time in cycling order"

    def generate_parameters(
        self, well_idx: int, well_data: List[Dict[str, Any]], learning_rate: float
    ) -> Dict[str, float]:
        """Generate parameters using coordinate descent"""

        if well_idx == 0:
            # First well - use reference parameters
            return self.reference_params.copy()

        # Get current parameter to optimize
        current_param = self.param_order[self.current_param_index]

        if well_idx == 1:
            # Second well - start coordinate descent
            current_params = self.reference_params.copy()
            if current_param in current_params:
                adjustment = self.step_sizes[current_param] * 0.1
                current_params[current_param] += adjustment
            return self.apply_constraints(current_params)

        else:
            # Coordinate descent optimization
            if len(well_data) >= 2:
                last_result = well_data[-1]
                second_last_result = well_data[-2]

                # Only optimize the current parameter
                current_params = last_result["parameters"].copy()

                if current_param in current_params:
                    param_change = (
                        current_params[current_param]
                        - second_last_result["parameters"][current_param]
                    )
                    if abs(param_change) > 1e-6:
                        score_change = (
                            last_result["bubblicity_score"] - second_last_result["bubblicity_score"]
                        )
                        gradient = -score_change / param_change
                        step = learning_rate * self.step_sizes[current_param] * gradient
                        current_params[current_param] += step

                return self.apply_constraints(current_params)
            else:
                return self.reference_params.copy()

    def record_result(
        self,
        well_idx: int,
        parameters: Dict[str, float],
        score: float,
        height_status: bool,
        learning_rate: float,
    ):
        """Record result and advance to next parameter if needed"""
        super().record_result(well_idx, parameters, score, height_status, learning_rate)

        # Advance to next parameter every few wells (parameter cycling)
        if well_idx > 0 and well_idx % 3 == 0:  # Change parameter every 3 wells
            self.current_param_index = (self.current_param_index + 1) % len(self.param_order)
            if self.current_param_index == 0:
                self.param_cycle_count += 1


# Strategy factory
class OptimizationStrategyFactory:
    """Factory for creating optimization strategies"""

    @staticmethod
    def create_strategy(
        strategy_name: str,
        reference_params: Dict[str, float],
        param_bounds: Dict[str, Tuple[float, float]],
        sample_count: int = 96,
    ) -> OptimizationStrategy:
        """
        Create optimization strategy by name

        Args:
            strategy_name: Name of strategy ("simultaneous", "hybrid", "coordinate")
            reference_params: Reference parameters
            param_bounds: Parameter bounds

        Returns:
            OptimizationStrategy instance
        """
        if strategy_name.lower() == "simultaneous":
            return SimultaneousOptimizationStrategy(reference_params, param_bounds)
        elif strategy_name.lower() == "hybrid":
            return HybridOptimizationStrategy(reference_params, param_bounds, sample_count)
        elif strategy_name.lower() == "coordinate":
            return CoordinateDescentOptimizationStrategy(reference_params, param_bounds)
        else:
            raise ValueError(f"Unknown optimization strategy: {strategy_name}")

    @staticmethod
    def get_available_strategies() -> List[str]:
        """Get list of available strategy names"""
        return ["simultaneous", "hybrid", "coordinate"]
