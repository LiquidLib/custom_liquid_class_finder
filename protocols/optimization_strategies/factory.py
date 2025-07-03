"""
Optimization Strategy Factory

This module contains the OptimizationStrategyFactory class that creates
optimization strategy instances by name.
"""

from typing import List, Dict, Tuple
from .base import OptimizationStrategy
from .simultaneous import SimultaneousOptimizationStrategy
from .hybrid import HybridOptimizationStrategy
from .coordinate_descent import CoordinateDescentOptimizationStrategy


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
            sample_count: Number of samples for hybrid strategy

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
