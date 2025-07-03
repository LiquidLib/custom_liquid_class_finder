"""
Optimization Strategy Plugins for Liquid Class Calibration

This package provides a pluggable architecture for different optimization strategies
used in liquid class calibration protocols. Each strategy implements the same interface
but uses different approaches to parameter optimization.
"""

from .base import OptimizationStrategy
from .simultaneous import SimultaneousOptimizationStrategy
from .hybrid import HybridOptimizationStrategy
from .coordinate_descent import CoordinateDescentOptimizationStrategy
from .factory import OptimizationStrategyFactory

__all__ = [
    "OptimizationStrategy",
    "SimultaneousOptimizationStrategy",
    "HybridOptimizationStrategy",
    "CoordinateDescentOptimizationStrategy",
    "OptimizationStrategyFactory",
]
