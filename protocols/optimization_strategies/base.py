"""
Base Optimization Strategy Class

This module contains the abstract base class for all optimization strategies
used in liquid class calibration protocols.
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
