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

    P20 = "P20"
    P50 = "P50"
    P300 = "P300"
    P1000 = "P1000"


class LiquidType(Enum):
    """Supported liquid types"""

    GLYCEROL_10 = "Glycerol 10%"
    GLYCEROL_50 = "Glycerol 50%"
    GLYCEROL_90 = "Glycerol 90%"
    GLYCEROL_99 = "Glycerol 99%"
    PEG_8000_50 = "PEG 8000 50% w/v"
    SANITIZER_62_ALCOHOL = "Sanitizer 62% Alcohol"
    TWEEN_20_100 = "Tween 20 100%"
    ENGINE_OIL_100 = "Engine oil 100%"
    WATER = "Water"
    DMSO = "DMSO"
    ETHANOL = "Ethanol"


@dataclass
class LiquidClassParams:
    """Liquid class parameters for a specific pipette-liquid combination"""

    pipette: PipetteType
    liquid: Any  # Accept both LiquidType and custom types
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

        # P20 liquid classes
        p20_glycerol_10 = LiquidClassParams(
            pipette=PipetteType.P20,
            liquid=LiquidType.GLYCEROL_10,
            aspiration_rate=6.804,
            aspiration_delay=2.0,
            aspiration_withdrawal_rate=5.0,
            dispense_rate=6.804,
            dispense_delay=2.0,
            blowout_rate=0.5,
            touch_tip=False,
        )

        p20_glycerol_90 = LiquidClassParams(
            pipette=PipetteType.P20,
            liquid=LiquidType.GLYCEROL_90,
            aspiration_rate=5.292,
            aspiration_delay=7.0,
            aspiration_withdrawal_rate=2.0,
            dispense_rate=5.292,
            dispense_delay=7.0,
            blowout_rate=0.5,
            touch_tip=False,
        )

        p20_glycerol_99 = LiquidClassParams(
            pipette=PipetteType.P20,
            liquid=LiquidType.GLYCEROL_99,
            aspiration_rate=3.78,
            aspiration_delay=10.0,
            aspiration_withdrawal_rate=2.0,
            dispense_rate=3.78,
            dispense_delay=10.0,
            blowout_rate=0.5,
            touch_tip=False,
        )

        p20_peg_8000_50 = LiquidClassParams(
            pipette=PipetteType.P20,
            liquid=LiquidType.PEG_8000_50,
            aspiration_rate=6.048,
            aspiration_delay=7.0,
            aspiration_withdrawal_rate=5.0,
            dispense_rate=6.048,
            dispense_delay=7.0,
            blowout_rate=0.5,
            touch_tip=False,
        )

        p20_sanitizer_62_alcohol = LiquidClassParams(
            pipette=PipetteType.P20,
            liquid=LiquidType.SANITIZER_62_ALCOHOL,
            aspiration_rate=1.0,
            aspiration_delay=2.0,
            aspiration_withdrawal_rate=20.0,
            dispense_rate=3.78,
            dispense_delay=2.0,
            blowout_rate=0.5,
            touch_tip=True,
        )

        p20_tween_20_100 = LiquidClassParams(
            pipette=PipetteType.P20,
            liquid=LiquidType.TWEEN_20_100,
            aspiration_rate=5.292,
            aspiration_delay=7.0,
            aspiration_withdrawal_rate=2.0,
            dispense_rate=3.024,
            dispense_delay=7.0,
            blowout_rate=0.5,
            touch_tip=True,
        )

        p20_engine_oil_100 = LiquidClassParams(
            pipette=PipetteType.P20,
            liquid=LiquidType.ENGINE_OIL_100,
            aspiration_rate=6.048,
            aspiration_delay=7.0,
            aspiration_withdrawal_rate=1.0,
            dispense_rate=6.048,
            dispense_delay=7.0,
            blowout_rate=0.5,
            touch_tip=True,
        )

        # P300 liquid classes
        p300_glycerol_10 = LiquidClassParams(
            pipette=PipetteType.P300,
            liquid=LiquidType.GLYCEROL_10,
            aspiration_rate=83.25,
            aspiration_delay=2.0,
            aspiration_withdrawal_rate=5.0,
            dispense_rate=83.25,
            dispense_delay=2.0,
            blowout_rate=10.0,
            touch_tip=False,
        )

        p300_glycerol_90 = LiquidClassParams(
            pipette=PipetteType.P300,
            liquid=LiquidType.GLYCEROL_90,
            aspiration_rate=64.75,
            aspiration_delay=8.0,
            aspiration_withdrawal_rate=1.0,
            dispense_rate=64.75,
            dispense_delay=8.0,
            blowout_rate=4.0,
            touch_tip=False,
        )

        p300_glycerol_99 = LiquidClassParams(
            pipette=PipetteType.P300,
            liquid=LiquidType.GLYCEROL_99,
            aspiration_rate=55.5,
            aspiration_delay=10.0,
            aspiration_withdrawal_rate=1.0,
            dispense_rate=55.5,
            dispense_delay=10.0,
            blowout_rate=4.0,
            touch_tip=False,
        )

        p300_peg_8000_50 = LiquidClassParams(
            pipette=PipetteType.P300,
            liquid=LiquidType.PEG_8000_50,
            aspiration_rate=74.0,
            aspiration_delay=6.0,
            aspiration_withdrawal_rate=4.0,
            dispense_rate=74.0,
            dispense_delay=74.0,
            blowout_rate=4.0,
            touch_tip=False,
        )

        p300_sanitizer_62_alcohol = LiquidClassParams(
            pipette=PipetteType.P300,
            liquid=LiquidType.SANITIZER_62_ALCOHOL,
            aspiration_rate=92.5,
            aspiration_delay=2.0,
            aspiration_withdrawal_rate=20.0,
            dispense_rate=92.5,
            dispense_delay=2.0,
            blowout_rate=4.0,
            touch_tip=True,
        )

        p300_tween_20_100 = LiquidClassParams(
            pipette=PipetteType.P300,
            liquid=LiquidType.TWEEN_20_100,
            aspiration_rate=13.9,
            aspiration_delay=10.0,
            aspiration_withdrawal_rate=1.0,
            dispense_rate=13.9,
            dispense_delay=11.0,
            blowout_rate=7.0,
            touch_tip=True,
        )

        p300_engine_oil_100 = LiquidClassParams(
            pipette=PipetteType.P300,
            liquid=LiquidType.ENGINE_OIL_100,
            aspiration_rate=74.0,
            aspiration_delay=3.0,
            aspiration_withdrawal_rate=2.0,
            dispense_rate=46.25,
            dispense_delay=7.0,
            blowout_rate=10.0,
            touch_tip=True,
        )

        # P1000 liquid classes
        p1000_glycerol_10 = LiquidClassParams(
            pipette=PipetteType.P1000,
            liquid=LiquidType.GLYCEROL_10,
            aspiration_rate=247.05,
            aspiration_delay=2.0,
            aspiration_withdrawal_rate=30.0,
            dispense_rate=247.05,
            dispense_delay=2.0,
            blowout_rate=75.0,
            touch_tip=False,
        )

        p1000_glycerol_50 = LiquidClassParams(
            pipette=PipetteType.P1000,
            liquid=LiquidType.GLYCEROL_50,
            aspiration_rate=247.05,
            aspiration_delay=3.0,
            aspiration_withdrawal_rate=30.0,
            dispense_rate=247.05,
            dispense_delay=3.0,
            blowout_rate=75.0,
            touch_tip=False,
        )

        p1000_glycerol_90 = LiquidClassParams(
            pipette=PipetteType.P1000,
            liquid=LiquidType.GLYCEROL_90,
            aspiration_rate=164.7,
            aspiration_delay=10.0,
            aspiration_withdrawal_rate=3.0,
            dispense_rate=109.8,
            dispense_delay=10.0,
            blowout_rate=15.0,
            touch_tip=False,
        )

        p1000_glycerol_99 = LiquidClassParams(
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

        # Add all liquid classes to registry
        liquid_classes = [
            # P20 classes
            p20_glycerol_10,
            p20_glycerol_90,
            p20_glycerol_99,
            p20_peg_8000_50,
            p20_sanitizer_62_alcohol,
            p20_tween_20_100,
            p20_engine_oil_100,
            # P300 classes
            p300_glycerol_10,
            p300_glycerol_90,
            p300_glycerol_99,
            p300_peg_8000_50,
            p300_sanitizer_62_alcohol,
            p300_tween_20_100,
            p300_engine_oil_100,
            # P1000 classes
            p1000_glycerol_10,
            p1000_glycerol_50,
            p1000_glycerol_90,
            p1000_glycerol_99,
        ]

        for liquid_class in liquid_classes:
            self.add_liquid_class(liquid_class)

    def add_liquid_class(self, liquid_class: LiquidClassParams):
        """Add a liquid class to the registry"""
        key = f"{liquid_class.pipette.value}_{liquid_class.liquid.value}"
        self._liquid_classes[key] = liquid_class

    def remove_liquid_class(self, pipette: PipetteType, liquid: LiquidType) -> bool:
        """Remove a liquid class from the registry"""
        key = f"{pipette.value}_{liquid.value}"
        if key in self._liquid_classes:
            del self._liquid_classes[key]
            return True
        return False

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
        # Use header with no spaces after commas for compatibility
        header = (
            "Pipette,Liquid,Aspiration Rate (µL/s),Aspiration Delay (s),"
            "Aspiration Withdrawal Rate (mm/s),Dispense Rate (µL/s),"
            "Dispense Delay (s),Blowout Rate (µL/s),Touch tip"
        )
        rows = [header]

        for liquid_class in self._liquid_classes.values():
            # Export with no extra spaces after commas
            row = str(liquid_class)
            row = ",".join([field.strip() for field in row.split(",")])
            rows.append(row)

        return "\n".join(rows)

    def import_from_csv(self, csv_data: str):
        """Import liquid classes from CSV data"""
        lines = csv_data.strip().split("\n")
        if len(lines) < 2:
            raise ValueError("CSV must have at least a header and one data row")

        # Accept both header formats (with or without spaces after commas)
        header_no_space = (
            "Pipette,Liquid,Aspiration Rate (µL/s),Aspiration Delay (s),"
            "Aspiration Withdrawal Rate (mm/s),Dispense Rate (µL/s),"
            "Dispense Delay (s),Blowout Rate (µL/s),Touch tip"
        )
        header = lines[0].replace(" ", "")
        if header != header_no_space.replace(" ", ""):
            raise ValueError("CSV header does not match expected format")

        # Skip header
        for line in lines[1:]:
            if line.strip():
                self._parse_csv_line(line)

    def _parse_csv_line(self, line: str):
        """Parse a single CSV line into a LiquidClassParams object"""
        # Strip whitespace from all fields
        parts = [p.strip() for p in line.split(",")]
        if len(parts) != 9:
            raise ValueError(f"Invalid CSV line format: {line}")

        try:
            pipette = PipetteType(parts[0])
            try:
                liquid: Any = LiquidType(parts[1])
            except ValueError:
                # Allow custom liquids
                class CustomLiquid:
                    def __init__(self, name):
                        self.value = name
                        self.name = name.upper().replace(" ", "_").replace("%", "PCT")

                liquid = CustomLiquid(parts[1])
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


def remove_liquid_class_params(pipette: PipetteType, liquid: LiquidType) -> bool:
    """Convenience function to remove liquid class parameters"""
    return liquid_class_registry.remove_liquid_class(pipette, liquid)


def export_liquid_classes_csv() -> str:
    """Convenience function to export all liquid classes to CSV"""
    return liquid_class_registry.export_csv()


def import_liquid_classes_from_csv(csv_data: str):
    """Convenience function to import liquid classes from CSV"""
    liquid_class_registry.import_from_csv(csv_data)
