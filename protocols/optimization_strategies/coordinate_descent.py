"""
Coordinate Descent Optimization Strategy

This module contains the CoordinateDescentOptimizationStrategy class that optimizes
one parameter at a time in cycling order.
"""

from typing import List, Dict, Any, Tuple
from .base import OptimizationStrategy


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
