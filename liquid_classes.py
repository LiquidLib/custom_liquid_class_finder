"""
Liquid Class Configuration System

This module defines liquid class parameters for different pipettes and liquids,
based on reference data for optimal liquid handling performance.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class PipetteType(Enum):
    """Supported pipette types"""

    P1000 = "P1000"
    P300 = "P300"
    P50 = "P50"


class LiquidType(Enum):
    """Supported liquid types"""

    GLYCEROL_99 = "Glycerol 99%"
    WATER = "Water"
    DMSO = "DMSO"
    ETHANOL = "Ethanol"


@dataclass
class LiquidClassParams:
    """Liquid class parameters for a specific pipette-liquid combination"""

    pipette: PipetteType
    liquid: LiquidType
    aspiration_rate: float  # µL/s
    aspiration_delay: float  # s
    aspiration_withdrawal_rate: float  # mm/s
    dispense_rate: float  # µL/s
    dispense_delay: float  # s
    blowout_rate: float  # µL/s
    touch_tip: bool

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for protocol use"""
        return {
            "aspiration_rate": self.aspiration_rate,
            "aspiration_delay": self.aspiration_delay,
            "aspiration_withdrawal_rate": self.aspiration_withdrawal_rate,
            "dispense_rate": self.dispense_rate,
            "dispense_delay": self.dispense_delay,
            "blowout_rate": self.blowout_rate,
            "touch_tip": self.touch_tip,
        }

    def __str__(self) -> str:
        return (
            f"{self.pipette.value}, {self.liquid.value}, "
            f"{self.aspiration_rate}, {self.aspiration_delay}, {self.aspiration_withdrawal_rate}, "
            f"{self.dispense_rate}, {self.dispense_delay}, {self.blowout_rate}, "
            f"{'Yes' if self.touch_tip else 'No'}"
        )


class LiquidClassRegistry:
    """Registry for liquid class parameters"""

    def __init__(self):
        self._liquid_classes: Dict[str, LiquidClassParams] = {}
        self._initialize_default_classes()

    def _initialize_default_classes(self):
        """Initialize with default liquid class parameters"""

        # Reference liquid class from user data
        glycerol_p1000 = LiquidClassParams(
            pipette=PipetteType.P1000,
            liquid=LiquidType.GLYCEROL_99,
            aspiration_rate=41.175,
            aspiration_delay=20.0,
            aspiration_withdrawal_rate=4.0,
            dispense_rate=19.215,
            dispense_delay=20.0,
            blowout_rate=5.0,
            touch_tip=False,
        )

        self.add_liquid_class(glycerol_p1000)

        # Add some common default liquid classes
        water_p1000 = LiquidClassParams(
            pipette=PipetteType.P1000,
            liquid=LiquidType.WATER,
            aspiration_rate=150.0,
            aspiration_delay=1.0,
            aspiration_withdrawal_rate=5.0,
            dispense_rate=150.0,
            dispense_delay=1.0,
            blowout_rate=100.0,
            touch_tip=True,
        )

        self.add_liquid_class(water_p1000)

    def add_liquid_class(self, liquid_class: LiquidClassParams):
        """Add a liquid class to the registry"""
        key = f"{liquid_class.pipette.value}_{liquid_class.liquid.value}"
        self._liquid_classes[key] = liquid_class

    def get_liquid_class(
        self, pipette: PipetteType, liquid: LiquidType
    ) -> Optional[LiquidClassParams]:
        """Get liquid class parameters for a pipette-liquid combination"""
        key = f"{pipette.value}_{liquid.value}"
        return self._liquid_classes.get(key)

    def list_liquid_classes(self) -> Dict[str, LiquidClassParams]:
        """List all available liquid classes"""
        return self._liquid_classes.copy()

    def export_csv(self) -> str:
        """Export all liquid classes to CSV format"""
        header = (
            "Pipette, Liquid, Aspiration Rate (µL/s), Aspiration Delay (s), "
            "Aspiration Withdrawal Rate (mm/s), Dispense Rate (µL/s), "
            "Dispense Delay (s), Blowout Rate (µL/s), Touch tip"
        )
        rows = [header]

        for liquid_class in self._liquid_classes.values():
            rows.append(str(liquid_class))

        return "\n".join(rows)

    def import_from_csv(self, csv_data: str):
        """Import liquid classes from CSV data"""
        lines = csv_data.strip().split("\n")
        if len(lines) < 2:
            raise ValueError("CSV must have at least a header and one data row")

        # Skip header
        for line in lines[1:]:
            if line.strip():
                self._parse_csv_line(line)

    def _parse_csv_line(self, line: str):
        """Parse a single CSV line into a LiquidClassParams object"""
        parts = line.split(",")
        if len(parts) != 9:
            raise ValueError(f"Invalid CSV line format: {line}")

        try:
            pipette = PipetteType(parts[0])
            liquid = LiquidType(parts[1])
            aspiration_rate = float(parts[2])
            aspiration_delay = float(parts[3])
            aspiration_withdrawal_rate = float(parts[4])
            dispense_rate = float(parts[5])
            dispense_delay = float(parts[6])
            blowout_rate = float(parts[7])
            touch_tip = parts[8].lower() == "yes"

            liquid_class = LiquidClassParams(
                pipette=pipette,
                liquid=liquid,
                aspiration_rate=aspiration_rate,
                aspiration_delay=aspiration_delay,
                aspiration_withdrawal_rate=aspiration_withdrawal_rate,
                dispense_rate=dispense_rate,
                dispense_delay=dispense_delay,
                blowout_rate=blowout_rate,
                touch_tip=touch_tip,
            )

            self.add_liquid_class(liquid_class)

        except (ValueError, KeyError) as e:
            raise ValueError(f"Error parsing CSV line '{line}': {e}")


# Global registry instance
liquid_class_registry = LiquidClassRegistry()


def get_liquid_class_params(
    pipette: PipetteType, liquid: LiquidType
) -> Optional[LiquidClassParams]:
    """Convenience function to get liquid class parameters"""
    return liquid_class_registry.get_liquid_class(pipette, liquid)


def add_liquid_class_params(liquid_class: LiquidClassParams):
    """Convenience function to add liquid class parameters"""
    liquid_class_registry.add_liquid_class(liquid_class)


def export_liquid_classes_csv() -> str:
    """Convenience function to export all liquid classes to CSV"""
    return liquid_class_registry.export_csv()


def import_liquid_classes_from_csv(csv_data: str):
    """Convenience function to import liquid classes from CSV"""
    liquid_class_registry.import_from_csv(csv_data)
