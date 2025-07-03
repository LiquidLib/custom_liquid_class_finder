"""
Simultaneous Optimization Strategy

This module contains the SimultaneousOptimizationStrategy class that optimizes
all parameters simultaneously using gradient descent.
"""

from typing import List, Dict, Any, Tuple
from .base import OptimizationStrategy


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
