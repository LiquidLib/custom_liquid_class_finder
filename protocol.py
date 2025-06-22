import sys
import os

try:
    protocol_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    # __file__ is not defined (e.g., in Opentrons simulation)
    protocol_dir = os.getcwd()

if protocol_dir not in sys.path:
    sys.path.insert(0, protocol_dir)

from opentrons import protocol_api, types
from typing import List, Dict, Any, Optional

# Try to import liquid classes, with fallback if not available
try:
    from liquid_classes import get_liquid_class_params, PipetteType, LiquidType

    LIQUID_CLASSES_AVAILABLE = True
except ImportError:
    # Fallback: define basic enums and functions if module not available
    from enum import Enum

    class FallbackPipetteType(Enum):
        P1000 = "P1000"
        P300 = "P300"
        P50 = "P50"

    class FallbackLiquidType(Enum):
        GLYCEROL_99 = "Glycerol 99%"
        WATER = "Water"
        DMSO = "DMSO"
        ETHANOL = "Ethanol"

    def get_liquid_class_params_fallback(pipette: Any, liquid: Any) -> Optional[Dict[str, float]]:
        """Fallback function that returns default parameters"""
        if pipette == FallbackPipetteType.P1000 and liquid == FallbackLiquidType.GLYCEROL_99:
            return {
                "aspiration_rate": 41.175,
                "aspiration_delay": 20.0,
                "aspiration_withdrawal_rate": 4.0,
                "dispense_rate": 19.215,
                "dispense_delay": 20.0,
                "blowout_rate": 5.0,
                "touch_tip": False,
            }
        return None

    # Use fallback types when main module is not available
    PipetteType = FallbackPipetteType  # type: ignore
    LiquidType = FallbackLiquidType  # type: ignore
    get_liquid_class_params = get_liquid_class_params_fallback  # type: ignore
    LIQUID_CLASSES_AVAILABLE = False

metadata = {
    "protocolName": "Liquid Class Calibration with Gradient Descent",
    "author": "Roman Gurovich",
    "description": (
        "Calibration protocol using gradient descent to optimize liquid handling parameters across all 96 wells"  # noqa: E501
    ),
    "source": "Roman Gurovich",
}

requirements = {"robotType": "Flex", "apiLevel": "2.22"}


def add_parameters(parameters):
    parameters.add_int(
        display_name="Sample count",
        variable_name="sample_count",
        default=96,
        minimum=1,
        maximum=96,
        description="Number of wells to test (1-96)",
    )
    parameters.add_str(
        display_name="Pipette mount",
        variable_name="pipette_mount",
        choices=[
            {"display_name": "Left", "value": "left"},
            {"display_name": "Right", "value": "right"},
        ],
        default="right",
        description="Mount position for pipette",
    )
    parameters.add_str(
        display_name="Trash position",
        variable_name="trash_position",
        choices=[
            {"display_name": "A1", "value": "A1"},
            {"display_name": "A2", "value": "A2"},
            {"display_name": "A3", "value": "A3"},
            {"display_name": "B1", "value": "B1"},
            {"display_name": "B2", "value": "B2"},
            {"display_name": "B3", "value": "B3"},
            {"display_name": "C1", "value": "C1"},
            {"display_name": "C2", "value": "C2"},
            {"display_name": "C3", "value": "C3"},
            {"display_name": "D1", "value": "D1"},
            {"display_name": "D2", "value": "D2"},
            {"display_name": "D3", "value": "D3"},
        ],
        default="A3",
        description="Deck position for trash container",
    )
    parameters.add_str(
        display_name="Liquid type",
        variable_name="liquid_type",
        choices=[
            {"display_name": "Glycerol 99%", "value": "GLYCEROL_99"},
            {"display_name": "Water", "value": "WATER"},
            {"display_name": "DMSO", "value": "DMSO"},
            {"display_name": "Ethanol", "value": "ETHANOL"},
        ],
        default="GLYCEROL_99",
        description="Type of liquid to calibrate for",
    )
    parameters.add_str(
        display_name="Pipette type",
        variable_name="pipette_type",
        choices=[
            {"display_name": "P1000", "value": "P1000"},
            {"display_name": "P300", "value": "P300"},
            {"display_name": "P50", "value": "P50"},
        ],
        default="P1000",
        description="Type of pipette to calibrate",
    )


def run(protocol: protocol_api.ProtocolContext):
    # Access runtime parameters
    SAMPLE_COUNT = protocol.params.sample_count  # type: ignore
    PIPETTE_MOUNT = protocol.params.pipette_mount  # type: ignore
    TRASH_POSITION = protocol.params.trash_position  # type: ignore
    LIQUID_TYPE = LiquidType[protocol.params.liquid_type]  # type: ignore
    PIPETTE_TYPE = PipetteType[protocol.params.pipette_type]  # type: ignore

    # Load labware
    reservoir = protocol.load_labware("nest_12_reservoir_15ml", "D1")
    test_plate = protocol.load_labware("nest_96_wellplate_200ul_flat", "D2")
    tiprack_1000 = protocol.load_labware("opentrons_flex_96_filtertiprack_1000ul", "C1")
    tiprack_50 = protocol.load_labware("opentrons_flex_96_filtertiprack_50ul", "C2")

    # Additional tip racks needed for 8-channel pipettes (commented out)
    # tiprack_1000_2 = protocol.load_labware("opentrons_flex_96_filtertiprack_1000ul", "B1")
    # tiprack_1000_3 = protocol.load_labware("opentrons_flex_96_filtertiprack_1000ul", "B2")
    # tiprack_1000_4 = protocol.load_labware("opentrons_flex_96_filtertiprack_1000ul", "B3")
    # tiprack_1000_5 = protocol.load_labware("opentrons_flex_96_filtertiprack_1000ul", "A1")
    # tiprack_1000_6 = protocol.load_labware("opentrons_flex_96_filtertiprack_1000ul", "A2")
    # tiprack_1000_7 = protocol.load_labware("opentrons_flex_96_filtertiprack_1000ul", "A3")
    # tiprack_1000_8 = protocol.load_labware("opentrons_flex_96_filtertiprack_1000ul", "C3")

    # Define trash container
    protocol.load_trash_bin(location=TRASH_POSITION)

    # Load pipettes - using single-channel for individual well processing
    pipette_1000 = protocol.load_instrument("flex_1channel_1000", "left", tip_racks=[tiprack_1000])
    pipette_50 = protocol.load_instrument("flex_1channel_50", PIPETTE_MOUNT, tip_racks=[tiprack_50])

    # Get liquid class parameters from registry
    liquid_class_params = get_liquid_class_params(PIPETTE_TYPE, LIQUID_TYPE)

    reference_params: Dict[str, Any]
    if liquid_class_params is None:
        protocol.comment(
            f"Warning: No liquid class parameters found for {PIPETTE_TYPE.value} "
            f"and {LIQUID_TYPE.value}"
        )
        protocol.comment("Using default parameters")
        # Fallback to default parameters
        reference_params = {
            "aspiration_rate": 150.0,  # µL/s
            "aspiration_delay": 1.0,  # s
            "aspiration_withdrawal_rate": 5.0,  # mm/s
            "dispense_rate": 150.0,  # µL/s
            "dispense_delay": 1.0,  # s
            "blowout_rate": 100.0,  # µL/s
            "touch_tip": True,
        }
    else:
        protocol.comment(
            f"Using liquid class parameters for {PIPETTE_TYPE.value} and {LIQUID_TYPE.value}"
        )
        # Always convert to dict for consistency
        if LIQUID_CLASSES_AVAILABLE and hasattr(liquid_class_params, "to_dict"):
            reference_params = liquid_class_params.to_dict()
        else:
            reference_params = dict(liquid_class_params)  # type: ignore

    # Define liquid based on liquid type
    liquid_name = LIQUID_TYPE.value
    liquid_description = f"Calibration liquid for {liquid_name}"
    liquid_color = "#FFD700"  # Default gold color

    if LIQUID_TYPE == LiquidType.GLYCEROL_99:
        liquid_color = "#FFD700"  # Gold for glycerol
    elif LIQUID_TYPE == LiquidType.WATER:
        liquid_color = "#87CEEB"  # Sky blue for water
    elif LIQUID_TYPE == LiquidType.DMSO:
        liquid_color = "#98FB98"  # Pale green for DMSO
    elif LIQUID_TYPE == LiquidType.ETHANOL:
        liquid_color = "#F0E68C"  # Khaki for ethanol

    liquid = protocol.define_liquid(
        name=liquid_name,
        description=liquid_description,
        display_color=liquid_color,
    )
    reservoir["A1"].load_liquid(liquid=liquid, volume=15000)

    # Parameter bounds for constraint checking
    param_bounds = {
        "aspiration_rate": (10.0, 500.0),
        "aspiration_delay": (0.0, 5.0),
        "aspiration_withdrawal_rate": (1.0, 20.0),
        "dispense_rate": (10.0, 500.0),
        "dispense_delay": (0.0, 5.0),
        "blowout_rate": (10.0, 300.0),
    }

    # Gradient descent parameters
    gradient_step = {
        "aspiration_rate": 10.0,
        "aspiration_delay": 0.1,
        "aspiration_withdrawal_rate": 0.5,
        "dispense_rate": 10.0,
        "dispense_delay": 0.1,
        "blowout_rate": 5.0,
    }

    # Detection parameters
    expected_liquid_height = 2.0  # mm from bottom
    bubble_check_increments = [0.5, 1.0, 1.5, 2.0, 2.5]  # mm above expected height
    horizontal_sweep_points = [
        (0, 0),
        (1, 0),
        (-1, 0),
        (0, 1),
        (0, -1),
    ]  # relative positions

    # Data storage
    well_data: List[Dict[str, Any]] = []

    def apply_constraints(params):
        """Apply parameter constraints"""
        constrained_params = params.copy()
        for param, (min_val, max_val) in param_bounds.items():
            if param in constrained_params:
                constrained_params[param] = max(min_val, min(max_val, constrained_params[param]))
        return constrained_params

    def calculate_gradient_adjustment(previous_score, current_score):
        """Simple gradient descent adjustment"""
        if current_score < previous_score:
            return 1.0  # Good direction, continue
        else:
            return -0.5  # Bad direction, reverse and reduce step

    def evaluate_liquid_height_with_tip(well, pipette, expected_height):
        """Evaluate if liquid is at expected height (assumes tip is already attached)"""
        protocol.comment(f"Evaluating liquid height in {well}")

        # Move to expected height
        pipette.move_to(well.bottom(expected_height))

        # Horizontal sweep to check pressure
        height_status = True
        for x_offset, y_offset in horizontal_sweep_points:
            try:
                # Move to sweep position using well coordinates
                # Calculate relative position from well center
                target_location = well.bottom(expected_height).move(
                    types.Point(x_offset, y_offset, 0)
                )
                pipette.move_to(target_location)

                # Check for liquid presence (simulated pressure check)
                # Note: In actual implementation, this would use pressure sensor
                liquid_detected = pipette.detect_liquid_presence(well)
                if not liquid_detected:
                    height_status = False
                    break

            except Exception as e:
                protocol.comment(f"Error during height check: {e}")
                height_status = False
                break

        # Return to safe height
        pipette.move_to(well.top(10))
        return height_status

    def evaluate_bubblicity_with_tip(well, pipette, expected_height):
        """Evaluate bubble presence above liquid surface (assumes tip is already attached)"""
        protocol.comment(f"Evaluating bubblicity in {well}")

        bubblicity_score = 0

        for height_increment in bubble_check_increments:
            check_height = expected_height + height_increment
            pipette.move_to(well.bottom(check_height))

            # Check for bubbles at this height
            bubble_detected = False
            for x_offset, y_offset in horizontal_sweep_points:
                try:
                    target_location = well.bottom(check_height).move(
                        types.Point(x_offset, y_offset, 0)
                    )
                    pipette.move_to(target_location)

                    # Simulated bubble detection via pressure
                    # In real implementation, this would check pressure sensor
                    if pipette.detect_liquid_presence(well):
                        bubble_detected = True
                        bubblicity_score += height_increment  # Weight by height
                        break

                except Exception as e:
                    protocol.comment(f"Error during bubble check: {e}")
                    break

            if bubble_detected:
                break

            # Return to safe height between checks
            pipette.move_to(well.top(10))

        return bubblicity_score

    def execute_dispense_sequence(well, pipette, params, volume=100):
        """Execute liquid handling with current parameters targeting individual wells"""
        protocol.comment(f"Dispensing with parameters: {params}")

        # Pick up tip - standard operation
        pipette.pick_up_tip()

        try:
            # Set flow rates (simplified - actual implementation would set all parameters)
            pipette.flow_rate.aspirate = params["aspiration_rate"]
            pipette.flow_rate.dispense = params["dispense_rate"]
            pipette.flow_rate.blow_out = params["blowout_rate"]

            # Aspirate from reservoir - target specific well
            pipette.aspirate(volume, reservoir["A1"])
            protocol.delay(seconds=params["aspiration_delay"])

            # Dispense into specific well - 8-channel will only dispense to the well we target
            pipette.dispense(volume, well)
            protocol.delay(seconds=params["dispense_delay"])

            # Blow out
            pipette.blow_out(well.top())

            # Touch tip if enabled
            if params["touch_tip"]:
                pipette.touch_tip(well)

        except Exception as e:
            protocol.comment(f"Error during dispense: {e}")
        finally:
            pipette.drop_tip()

    # Main optimization loop - test all wells individually
    current_params = reference_params.copy()
    previous_score = float("inf")

    # Get all wells to test
    test_wells = test_plate.wells()[:SAMPLE_COUNT]

    for well_idx, well in enumerate(test_wells):
        protocol.comment(f"Processing well {well_idx + 1}/{SAMPLE_COUNT}: {well}")

        # Step 1.1: Generate parameter combination for this well
        if well_idx == 0:
            # First well - use reference parameters
            current_params = reference_params.copy()
            protocol.comment("Using reference liquid class parameters for first well")
        else:
            # Adjust parameters based on previous results using gradient descent
            if well_data:
                last_result = well_data[-1]
                adjustment_factor = calculate_gradient_adjustment(
                    previous_score, last_result["bubblicity_score"]
                )

                # Adjust parameters
                for param in ["aspiration_rate", "dispense_rate", "blowout_rate"]:
                    current_params[param] += adjustment_factor * gradient_step[param]

                for param in ["aspiration_delay", "dispense_delay"]:
                    current_params[param] += adjustment_factor * gradient_step[param] * 0.1

                current_params["aspiration_withdrawal_rate"] += (
                    adjustment_factor * gradient_step["aspiration_withdrawal_rate"]
                )

            # Apply constraints
            current_params = apply_constraints(current_params)

        # Step 1.2: Execute dispense sequence targeting individual well
        execute_dispense_sequence(well, pipette_1000, current_params)

        # Step 1.3 & 1.4: Evaluate liquid height and bubblicity using the same tip
        # Pick up one tip for both evaluations
        pipette_50.pick_up_tip()

        try:
            # Step 1.3: Evaluate liquid height targeting individual well
            height_status = evaluate_liquid_height_with_tip(
                well, pipette_50, expected_liquid_height
            )

            # Step 1.4: Evaluate bubblicity targeting individual well (only if height check passes)
            if not height_status:
                bubblicity_score = 1000.0  # Artificially high value for failed height
                protocol.comment("Liquid height check failed - setting high bubblicity score")
            else:
                bubblicity_score = evaluate_bubblicity_with_tip(
                    well, pipette_50, expected_liquid_height
                )

        finally:
            # Drop the tip after both evaluations
            pipette_50.drop_tip()

        # Step 1.5: Record well data
        well_result = {
            "well_id": str(well),
            "well_index": well_idx,
            "parameters": current_params.copy(),
            "height_status": height_status,
            "bubblicity_score": bubblicity_score,
        }
        well_data.append(well_result)

        protocol.comment(
            f"Well {well}: Height OK: {height_status}, "
            f"Bubblicity: {bubblicity_score:.2f}"  # noqa: E231
        )

        # Update previous score for next iteration
        previous_score = bubblicity_score

    # Find optimal parameters
    if well_data:
        # Filter successful height results and find minimum bubblicity
        successful_results = [r for r in well_data if r["height_status"]]

        if successful_results:
            optimal_result = min(successful_results, key=lambda x: x["bubblicity_score"])
            protocol.comment(f"Optimal parameters found in {optimal_result['well_id']}")
            protocol.comment(
                f"Optimal bubblicity score: {optimal_result['bubblicity_score']:.2f}"  # noqa: E231
            )
            protocol.comment(f"Optimal parameters: {optimal_result['parameters']}")

            # Additional analysis
            protocol.comment(f"Total wells tested: {len(well_data)}")
            protocol.comment(f"Successful height checks: {len(successful_results)}")
            protocol.comment(
                f"Success rate: {len(successful_results)/len(well_data)*100:.1f}%"  # noqa: E231, E501
            )
        else:
            protocol.comment("No successful liquid height results found")

    protocol.comment("Liquid class calibration protocol completed")
