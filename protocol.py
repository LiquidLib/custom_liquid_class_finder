from opentrons import protocol_api
import math
from typing import List, Dict, Any

metadata = {
    "protocolName": "Liquid Class Calibration with Gradient Descent",
    "author": "Roman Gurovich",
    "description": (
        "Calibration protocol using gradient descent to optimize liquid handling parameters"
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
        display_name="8-channel pipette mount",
        variable_name="pipette_mount",
        choices=[
            {"display_name": "Left", "value": "left"},
            {"display_name": "Right", "value": "right"},
        ],
        default="right",
        description="Mount position for 8-channel pipette",
    )


def run(protocol: protocol_api.ProtocolContext):
    # Access runtime parameters
    SAMPLE_COUNT = protocol.params.sample_count
    PIPETTE_MOUNT = protocol.params.pipette_mount

    # Load labware
    reservoir = protocol.load_labware("nest_12_reservoir_15ml", "D1")
    test_plate = protocol.load_labware("nest_96_wellplate_200ul_flat", "D2")
    tiprack_1000 = protocol.load_labware("opentrons_flex_96_filtertiprack_1000ul", "C1")
    tiprack_50 = protocol.load_labware("opentrons_flex_96_filtertiprack_50ul", "C2")

    # Load pipettes
    pipette_8ch_1000 = protocol.load_instrument(
        "flex_8channel_1000", "left", tip_racks=[tiprack_1000]
    )
    pipette_8ch_50 = protocol.load_instrument(
        "flex_8channel_50", PIPETTE_MOUNT, tip_racks=[tiprack_50]
    )

    # Define liquid
    glycerol = protocol.define_liquid(
        name="100% Glycerol",
        description="Calibration liquid for parameter optimization",
        display_color="#FFD700",
    )
    reservoir["A1"].load_liquid(liquid=glycerol, volume=15000)

    # Reference liquid class parameters (starting point)
    reference_params = {
        "aspiration_rate": 150.0,  # µL/s
        "aspiration_delay": 1.0,  # s
        "aspiration_withdrawal_rate": 5.0,  # mm/s
        "dispense_rate": 150.0,  # µL/s
        "dispense_delay": 1.0,  # s
        "blowout_rate": 100.0,  # µL/s
        "touch_tip": True,
    }

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

    def evaluate_liquid_height(well, pipette, expected_height):
        """Evaluate if liquid is at expected height"""
        protocol.comment(f"Evaluating liquid height in {well}")

        # Move to expected height
        pipette.move_to(well.bottom(expected_height))

        # Horizontal sweep to check pressure
        height_status = True
        for x_offset, y_offset in horizontal_sweep_points:
            try:
                # Move to sweep position
                target_location = well.bottom(expected_height).move(
                    protocol.geometry.Point(x_offset, y_offset, 0)
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

    def evaluate_bubblicity(well, pipette, expected_height):
        """Evaluate bubble presence above liquid surface"""
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
                        protocol.geometry.Point(x_offset, y_offset, 0)
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
        """Execute liquid handling with current parameters"""
        protocol.comment(f"Dispensing with parameters: {params}")

        # Pick up tip
        pipette.pick_up_tip()

        try:
            # Set flow rates (simplified - actual implementation would set all parameters)
            pipette.flow_rate.aspirate = params["aspiration_rate"]
            pipette.flow_rate.dispense = params["dispense_rate"]
            pipette.flow_rate.blow_out = params["blowout_rate"]

            # Aspirate from reservoir
            pipette.aspirate(volume, reservoir["A1"])
            protocol.delay(seconds=params["aspiration_delay"])

            # Dispense into well
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

    # Main optimization loop
    current_params = reference_params.copy()
    previous_score = float("inf")

    # Calculate number of columns for 8-channel pipette
    num_columns = math.ceil(SAMPLE_COUNT / 8)

    for col_idx in range(num_columns):
        well = test_plate.columns()[col_idx][0]  # Use first well of column for 8-channel
        protocol.comment(f"Processing column {col_idx + 1}, well {well}")

        # Step 1.1: Determine current well parameters
        if col_idx == 0:
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

        # Step 1.2: Execute dispense sequence
        execute_dispense_sequence(well, pipette_8ch_1000, current_params)

        # Step 1.3: Evaluate liquid height
        height_status = evaluate_liquid_height(well, pipette_8ch_50, expected_liquid_height)

        # Step 1.4: Evaluate bubblicity
        if not height_status:
            bubblicity_score = 1000.0  # Artificially high value for failed height
            protocol.comment("Liquid height check failed - setting high bubblicity score")
        else:
            bubblicity_score = evaluate_bubblicity(well, pipette_8ch_50, expected_liquid_height)

        # Step 1.5: Record well data
        well_result = {
            "well_id": str(well),
            "column": col_idx + 1,
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

        # Stop if we've processed the requested number of samples
        if (col_idx + 1) * 8 >= SAMPLE_COUNT:
            break

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
        else:
            protocol.comment("No successful liquid height results found")

    protocol.comment("Liquid class calibration protocol completed")
