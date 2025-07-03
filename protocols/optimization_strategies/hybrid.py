"""
Hybrid Optimization Strategy

This module contains the HybridOptimizationStrategy class that uses hierarchical
phases followed by fine-tuning for parameter optimization.
"""

from typing import List, Dict, Any, Tuple
from .base import OptimizationStrategy


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
