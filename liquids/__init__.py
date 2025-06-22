"""
Liquid Class System Package

This package provides a comprehensive system for managing liquid handling parameters
for automated liquid handling protocols, particularly for viscous liquids like glycerol.

Main components:
- liquid_classes.py: Core system with parameter registry
- liquid_class_manager.py: Command-line utility for management
- liquid_class_demo_basic.py: Basic demonstration script
- liquid_class_demo_custom.py: Comprehensive demonstration script
"""

from .liquid_classes import (
    get_liquid_class_params,
    PipetteType,
    LiquidType,
    LiquidClassParams,
    export_liquid_classes_csv,
    import_liquid_classes_from_csv,
    add_liquid_class_params,
)

__version__ = "1.0.0"
__author__ = "Roman Gurovich"

__all__ = [
    "get_liquid_class_params",
    "PipetteType",
    "LiquidType",
    "LiquidClassParams",
    "export_liquid_classes_csv",
    "import_liquid_classes_from_csv",
    "add_liquid_class_params",
]
