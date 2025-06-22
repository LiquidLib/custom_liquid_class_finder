#!/usr/bin/env python3
"""
Test script for the liquid class system

This script tests the liquid class configuration system to ensure it works
correctly with the reference data provided by the user.
"""

import unittest
from liquid_classes import (
    LiquidClassParams,
    PipetteType,
    LiquidType,
    liquid_class_registry,
    get_liquid_class_params,
    export_liquid_classes_csv,
    import_liquid_classes_from_csv,
)


class TestLiquidClasses(unittest.TestCase):
    """Test cases for the liquid class system"""

    def setUp(self):
        """Set up test fixtures"""
        # Clear the registry for each test
        liquid_class_registry._liquid_classes.clear()
        liquid_class_registry._initialize_default_classes()

    def test_glycerol_p1000_reference_data(self):
        """Test that the glycerol P1000 reference data is correctly loaded"""
        params = get_liquid_class_params(PipetteType.P1000, LiquidType.GLYCEROL_99)

        self.assertIsNotNone(params)
        self.assertEqual(params.pipette, PipetteType.P1000)
        self.assertEqual(params.liquid, LiquidType.GLYCEROL_99)
        self.assertEqual(params.aspiration_rate, 41.175)
        self.assertEqual(params.aspiration_delay, 20.0)
        self.assertEqual(params.aspiration_withdrawal_rate, 4.0)
        self.assertEqual(params.dispense_rate, 19.215)
        self.assertEqual(params.dispense_delay, 20.0)
        self.assertEqual(params.blowout_rate, 5.0)
        self.assertEqual(params.touch_tip, False)

    def test_csv_export(self):
        """Test CSV export functionality"""
        csv_data = export_liquid_classes_csv()

        # Check that CSV contains the expected header
        self.assertIn("Pipette,Liquid,Aspiration Rate (µL/s)", csv_data)

        # Check that glycerol data is in the CSV (with decimal points)
        self.assertIn("P1000,Glycerol 99%,41.175,20.0,4.0,19.215,20.0,5.0,No", csv_data)

    def test_csv_import(self):
        """Test CSV import functionality"""
        # Clear registry
        liquid_class_registry._liquid_classes.clear()

        # Test CSV data
        test_csv = (
            "Pipette, Liquid, Aspiration Rate (µL/s), Aspiration Delay (s), "
            "Aspiration Withdrawal Rate (mm/s), Dispense Rate (µL/s), "
            "Dispense Delay (s), Blowout Rate (µL/s), Touch tip\n"
            "P1000, Glycerol 99%, 41.175, 20, 4, 19.215, 20, 5.0, No"
        )

        # Import the CSV
        import_liquid_classes_from_csv(test_csv)

        # Verify the data was imported correctly
        params = get_liquid_class_params(PipetteType.P1000, LiquidType.GLYCEROL_99)
        self.assertIsNotNone(params)
        self.assertEqual(params.aspiration_rate, 41.175)
        self.assertEqual(params.dispense_rate, 19.215)

    def test_to_dict_conversion(self):
        """Test conversion to dictionary format"""
        params = get_liquid_class_params(PipetteType.P1000, LiquidType.GLYCEROL_99)
        param_dict = params.to_dict()

        expected_keys = {
            "aspiration_rate",
            "aspiration_delay",
            "aspiration_withdrawal_rate",
            "dispense_rate",
            "dispense_delay",
            "blowout_rate",
            "touch_tip",
        }

        self.assertEqual(set(param_dict.keys()), expected_keys)
        self.assertEqual(param_dict["aspiration_rate"], 41.175)
        self.assertEqual(param_dict["touch_tip"], False)

    def test_string_representation(self):
        """Test string representation of liquid class parameters"""
        params = get_liquid_class_params(PipetteType.P1000, LiquidType.GLYCEROL_99)
        param_str = str(params)

        # Check that the string contains the expected values
        self.assertIn("P1000", param_str)
        self.assertIn("Glycerol 99%", param_str)
        self.assertIn("41.175", param_str)
        self.assertIn("19.215", param_str)
        self.assertIn("No", param_str)  # touch_tip = False

    def test_nonexistent_liquid_class(self):
        """Test behavior when requesting non-existent liquid class"""
        params = get_liquid_class_params(PipetteType.P50, LiquidType.DMSO)
        self.assertIsNone(params)

    def test_add_new_liquid_class(self):
        """Test adding a new liquid class"""
        # Create a new liquid class
        new_params = LiquidClassParams(
            pipette=PipetteType.P300,
            liquid=LiquidType.DMSO,
            aspiration_rate=75.0,
            aspiration_delay=2.0,
            aspiration_withdrawal_rate=3.0,
            dispense_rate=75.0,
            dispense_delay=2.0,
            blowout_rate=50.0,
            touch_tip=True,
        )

        # Add to registry
        liquid_class_registry.add_liquid_class(new_params)

        # Verify it was added
        retrieved_params = get_liquid_class_params(PipetteType.P300, LiquidType.DMSO)
        self.assertIsNotNone(retrieved_params)
        self.assertEqual(retrieved_params.aspiration_rate, 75.0)
        self.assertEqual(retrieved_params.touch_tip, True)

    def test_invalid_csv_format(self):
        """Test handling of invalid CSV format"""
        invalid_csv = "Invalid,CSV,Format"

        with self.assertRaises(ValueError):
            import_liquid_classes_from_csv(invalid_csv)

    def test_empty_csv(self):
        """Test handling of empty CSV"""
        empty_csv = ""

        with self.assertRaises(ValueError):
            import_liquid_classes_from_csv(empty_csv)

    def test_csv_with_invalid_values(self):
        """Test handling of CSV with invalid numeric values"""
        invalid_csv = (
            "Pipette, Liquid, Aspiration Rate (µL/s), Aspiration Delay (s), "
            "Aspiration Withdrawal Rate (mm/s), Dispense Rate (µL/s), "
            "Dispense Delay (s), Blowout Rate (µL/s), Touch tip\n"
            "P1000, Glycerol 99%, invalid, 20, 4, 19.215, 20, 5.0, No"
        )

        with self.assertRaises(ValueError):
            import_liquid_classes_from_csv(invalid_csv)


def run_demo():
    """Run a quick demo of the system"""
    print("=== Liquid Class System Demo ===\n")

    # Show the reference data
    params = get_liquid_class_params(PipetteType.P1000, LiquidType.GLYCEROL_99)
    if params:
        print("Reference Liquid Class Parameters:")
        print(f"  Pipette: {params.pipette.value}")
        print(f"  Liquid: {params.liquid.value}")
        print(f"  Aspiration Rate: {params.aspiration_rate} µL/s")
        print(f"  Dispense Rate: {params.dispense_rate} µL/s")
        print(f"  Touch Tip: {params.touch_tip}")
        print()

    # Show CSV export
    print("CSV Export:")
    csv_data = export_liquid_classes_csv()
    print(csv_data)
    print()

    print("Demo completed successfully!")


if __name__ == "__main__":
    # Run the demo
    run_demo()

    # Run the tests
    print("\n=== Running Tests ===")
    unittest.main(argv=[""], exit=False, verbosity=2)
