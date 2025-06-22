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
from typing import List, Dict, Any

# Import liquid classes
from liquids.liquid_classes import (
    get_liquid_class_params,
    PipetteType,
    LiquidType,
    LiquidClassParams,
)

metadata = {
    "protocolName": "Liquid Class Calibration with 8-Channel Pipettes",
    "author": "Roman Gurovich",
    "description": (
        "Batch calibration protocol using 8-channel pipettes and gradient descent to optimize "
        "liquid handling parameters across multiple wells simultaneously"
    ),
    "source": "Roman Gurovich",
}

requirements = {"robotType": "Flex", "apiLevel": "2.22"}


def get_default_liquid_class_params(pipette: PipetteType, liquid: LiquidType) -> LiquidClassParams:
    """Get default liquid class parameters for combinations not in the registry"""

    # Initialize base_params with default values
    base_params: Dict[str, Any] = {
        "aspiration_rate": 150.0,
        "aspiration_delay": 1.0,
        "aspiration_withdrawal_rate": 5.0,
        "dispense_rate": 150.0,
        "dispense_delay": 1.0,
        "blowout_rate": 100.0,
        "touch_tip": True,
    }

    # Adjust parameters based on pipette type
    if pipette == PipetteType.P1000:
        # Use default values (already set above)
        pass
    elif pipette == PipetteType.P300:
        base_params.update(
            {
                "aspiration_rate": 50.0,
                "dispense_rate": 50.0,
                "blowout_rate": 10.0,
            }
        )
    elif pipette == PipetteType.P50:
        base_params.update(
            {
                "aspiration_rate": 10.0,
                "dispense_rate": 10.0,
                "blowout_rate": 5.0,
            }
        )
    else:  # P20
        base_params.update(
            {
                "aspiration_rate": 5.0,
                "dispense_rate": 5.0,
                "blowout_rate": 1.0,
            }
        )

    # Adjust parameters based on liquid type
    if liquid == LiquidType.WATER:
        # Water is easy to handle
        pass
    elif liquid == LiquidType.DMSO:
        # DMSO is volatile, reduce rates
        base_params["aspiration_rate"] *= 0.7
        base_params["dispense_rate"] *= 0.7
        base_params["blowout_rate"] *= 0.5
    elif liquid == LiquidType.ETHANOL:
        # Ethanol is volatile, reduce rates further
        base_params["aspiration_rate"] *= 0.5
        base_params["dispense_rate"] *= 0.5
        base_params["blowout_rate"] *= 0.3
        base_params["touch_tip"] = True

    return LiquidClassParams(
        pipette=pipette,
        liquid=liquid,
        aspiration_rate=base_params["aspiration_rate"],
        aspiration_delay=base_params["aspiration_delay"],
        aspiration_withdrawal_rate=base_params["aspiration_withdrawal_rate"],
        dispense_rate=base_params["dispense_rate"],
        dispense_delay=base_params["dispense_delay"],
        blowout_rate=base_params["blowout_rate"],
        touch_tip=bool(base_params["touch_tip"]),
    )


def add_parameters(parameters):
    parameters.add_int(
        display_name="Sample count",
        variable_name="sample_count",
        default=96,
        minimum=8,
        maximum=96,
        description="Number of wells to test (8-96, must be multiple of 8 for 8-channel)",
    )
    parameters.add_str(
        display_name="Pipette mount",
        variable_name="pipette_mount",
        choices=[
            {"display_name": "Left", "value": "left"},
            {"display_name": "Right", "value": "right"},
        ],
        default="right",
        description="Mount position for 8-channel pipette",
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
            {"display_name": "Glycerol 10%", "value": "GLYCEROL_10"},
            {"display_name": "Glycerol 50%", "value": "GLYCEROL_50"},
            {"display_name": "Glycerol 90%", "value": "GLYCEROL_90"},
            {"display_name": "Glycerol 99%", "value": "GLYCEROL_99"},
            {"display_name": "PEG 8000 50% w/v", "value": "PEG_8000_50"},
            {"display_name": "Sanitizer 62% Alcohol", "value": "SANITIZER_62_ALCOHOL"},
            {"display_name": "Tween 20 100%", "value": "TWEEN_20_100"},
            {"display_name": "Engine oil 100%", "value": "ENGINE_OIL_100"},
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
            {"display_name": "P20", "value": "P20"},
            {"display_name": "P50", "value": "P50"},
            {"display_name": "P300", "value": "P300"},
            {"display_name": "P1000", "value": "P1000"},
        ],
        default="P1000",
        description="Type of 8-channel pipette to calibrate",
    )
    parameters.add_int(
        display_name="Batch size",
        variable_name="batch_size",
        default=8,
        minimum=8,
        maximum=8,
        description="Number of wells to process in each batch (fixed at 8 for 8-channel)",
    )


def run(protocol: protocol_api.ProtocolContext):
    # Access runtime parameters
    SAMPLE_COUNT = protocol.params.sample_count  # type: ignore
    PIPETTE_MOUNT = protocol.params.pipette_mount  # type: ignore
    TRASH_POSITION = protocol.params.trash_position  # type: ignore
    LIQUID_TYPE = LiquidType[protocol.params.liquid_type]  # type: ignore
    PIPETTE_TYPE = PipetteType[protocol.params.pipette_type]  # type: ignore
    BATCH_SIZE = protocol.params.batch_size  # type: ignore

    # Validate sample count is multiple of batch size
    if SAMPLE_COUNT % BATCH_SIZE != 0:
        protocol.comment(
            f"Warning: Sample count {SAMPLE_COUNT} is not a multiple of batch size {BATCH_SIZE}. "
            f"Adjusting to {(SAMPLE_COUNT // BATCH_SIZE) * BATCH_SIZE}"
        )
        SAMPLE_COUNT = (SAMPLE_COUNT // BATCH_SIZE) * BATCH_SIZE

    # Load labware
    reservoir = protocol.load_labware("nest_12_reservoir_15ml", "D1")
    test_plate = protocol.load_labware("nest_96_wellplate_200ul_flat", "D2")

    # Multiple tip racks for 8-channel pipettes
    tiprack_1000_1 = protocol.load_labware("opentrons_flex_96_filtertiprack_1000ul", "C1")
    tiprack_1000_2 = protocol.load_labware("opentrons_flex_96_filtertiprack_1000ul", "C2")
    tiprack_1000_3 = protocol.load_labware("opentrons_flex_96_filtertiprack_1000ul", "C3")
    tiprack_1000_4 = protocol.load_labware("opentrons_flex_96_filtertiprack_1000ul", "B1")
    tiprack_1000_5 = protocol.load_labware("opentrons_flex_96_filtertiprack_1000ul", "B2")
    tiprack_1000_6 = protocol.load_labware("opentrons_flex_96_filtertiprack_1000ul", "B3")
    tiprack_1000_7 = protocol.load_labware("opentrons_flex_96_filtertiprack_1000ul", "A1")
    tiprack_1000_8 = protocol.load_labware("opentrons_flex_96_filtertiprack_1000ul", "A2")

    # Define trash container
    protocol.load_trash_bin(location=TRASH_POSITION)

    # Load 8-channel pipettes
    pipette_1000_8ch = protocol.load_instrument(
        "flex_8channel_1000",
        PIPETTE_MOUNT,
        tip_racks=[
            tiprack_1000_1,
            tiprack_1000_2,
            tiprack_1000_3,
            tiprack_1000_4,
            tiprack_1000_5,
            tiprack_1000_6,
            tiprack_1000_7,
            tiprack_1000_8,
        ],
    )

    # Get liquid class parameters from registry
    liquid_class_params = get_liquid_class_params(PIPETTE_TYPE, LIQUID_TYPE)

    if liquid_class_params is None:
        protocol.comment(
            f"No liquid class parameters found for {PIPETTE_TYPE.value} "
            f"and {LIQUID_TYPE.value}, using default parameters"
        )
        liquid_class_params = get_default_liquid_class_params(PIPETTE_TYPE, LIQUID_TYPE)
    else:
        protocol.comment(
            f"Using liquid class parameters for {PIPETTE_TYPE.value} and {LIQUID_TYPE.value}"
        )

    # Convert to dictionary for consistency
    reference_params = liquid_class_params.to_dict()

    # Define liquid based on liquid type
    liquid_name = LIQUID_TYPE.value
    liquid_description = f"Calibration liquid for {liquid_name}"
    liquid_color = "#FFD700"  # Default gold color

    if LIQUID_TYPE == LiquidType.GLYCEROL_10:
        liquid_color = "#FFE4B5"  # Light gold for 10% glycerol
    elif LIQUID_TYPE == LiquidType.GLYCEROL_50:
        liquid_color = "#FFD700"  # Gold for 50% glycerol
    elif LIQUID_TYPE == LiquidType.GLYCEROL_90:
        liquid_color = "#FFA500"  # Orange for 90% glycerol
    elif LIQUID_TYPE == LiquidType.GLYCEROL_99:
        liquid_color = "#FF8C00"  # Dark orange for 99% glycerol
    elif LIQUID_TYPE == LiquidType.PEG_8000_50:
        liquid_color = "#DDA0DD"  # Plum for PEG
    elif LIQUID_TYPE == LiquidType.SANITIZER_62_ALCOHOL:
        liquid_color = "#98FB98"  # Pale green for sanitizer
    elif LIQUID_TYPE == LiquidType.TWEEN_20_100:
        liquid_color = "#F0E68C"  # Khaki for Tween
    elif LIQUID_TYPE == LiquidType.ENGINE_OIL_100:
        liquid_color = "#2F4F4F"  # Dark slate gray for engine oil
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

    # Learning rate and optimization parameters
    initial_learning_rate = 0.1
    learning_rate_decay = 0.95
    min_learning_rate = 0.01
    convergence_threshold = 0.1
    patience = 3  # Reduced patience for batch processing

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
    batch_data: List[Dict[str, Any]] = []
    optimization_history: List[Dict[str, Any]] = []

    def apply_constraints(params):
        """Apply parameter constraints"""
        constrained_params = params.copy()
        for param, (min_val, max_val) in param_bounds.items():
            if param in constrained_params:
                constrained_params[param] = max(min_val, min(max_val, constrained_params[param]))
        return constrained_params

    def calculate_gradient_direction(
        previous_score, current_score, previous_params, current_params
    ):
        """Calculate gradient direction for each parameter"""
        if previous_score == float("inf"):
            return {param: 0.0 for param in gradient_step.keys()}

        # Calculate gradient for each parameter
        gradients = {}
        for param in gradient_step.keys():
            if param in previous_params and param in current_params:
                param_change = current_params[param] - previous_params[param]
                if abs(param_change) > 1e-6:  # Avoid division by zero
                    # Gradient is negative of score change divided by parameter change
                    score_change = current_score - previous_score
                    gradients[param] = -score_change / param_change
                else:
                    gradients[param] = 0.0
            else:
                gradients[param] = 0.0

        return gradients

    def update_parameters_with_gradient(current_params, gradients, learning_rate):
        """Update parameters using calculated gradients"""
        updated_params = current_params.copy()

        for param, gradient in gradients.items():
            if param in updated_params:
                # Apply gradient with learning rate and step size
                step = learning_rate * gradient_step[param] * gradient
                updated_params[param] += step

        return updated_params

    def evaluate_batch_liquid_height(wells, pipette, expected_height):
        """Evaluate if liquid is at expected height for a batch of wells"""
        protocol.comment(f"Evaluating liquid height in batch of {len(wells)} wells")

        height_statuses = []

        for well in wells:
            # Move to expected height
            pipette.move_to(well.bottom(expected_height))

            # Horizontal sweep to check pressure
            well_height_status = True
            for x_offset, y_offset in horizontal_sweep_points:
                try:
                    # Move to sweep position using well coordinates
                    target_location = well.bottom(expected_height).move(
                        types.Point(x_offset, y_offset, 0)
                    )
                    pipette.move_to(target_location)

                    # Check for liquid presence (simulated pressure check)
                    liquid_detected = pipette.detect_liquid_presence(well)
                    if not liquid_detected:
                        well_height_status = False
                        break

                except Exception as e:
                    protocol.comment(f"Error during height check in {well}: {e}")
                    well_height_status = False
                    break

            height_statuses.append(well_height_status)

        # Return to safe height
        pipette.move_to(wells[0].top(10))
        return height_statuses

    def evaluate_batch_bubblicity(wells, pipette, expected_height):
        """Evaluate bubble presence for a batch of wells"""
        protocol.comment(f"Evaluating bubblicity in batch of {len(wells)} wells")

        bubblicity_scores = []

        for well in wells:
            well_bubblicity_score = 0

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
                        if pipette.detect_liquid_presence(well):
                            bubble_detected = True
                            well_bubblicity_score += height_increment  # Weight by height
                            break

                    except Exception as e:
                        protocol.comment(f"Error during bubble check in {well}: {e}")
                        break

                if bubble_detected:
                    break

                # Return to safe height between checks
                pipette.move_to(well.top(10))

            bubblicity_scores.append(well_bubblicity_score)

        return bubblicity_scores

    def execute_batch_dispense_sequence(wells, pipette, params, volume=100):
        """Execute liquid handling with current parameters for a batch of wells"""
        protocol.comment(f"Dispensing to batch of {len(wells)} wells with parameters: {params}")

        # Pick up tip - 8-channel operation
        pipette.pick_up_tip()

        try:
            # Set flow rates
            pipette.flow_rate.aspirate = params["aspiration_rate"]
            pipette.flow_rate.dispense = params["dispense_rate"]
            pipette.flow_rate.blow_out = params["blowout_rate"]

            # Aspirate from reservoir - 8-channel will aspirate from A1
            pipette.aspirate(volume, reservoir["A1"])
            protocol.delay(seconds=params["aspiration_delay"])

            # Dispense into batch of wells - 8-channel will dispense to all wells in batch
            pipette.dispense(volume, wells)
            protocol.delay(seconds=params["dispense_delay"])

            # Blow out
            pipette.blow_out(wells[0].top())

            # Touch tip if enabled
            if params["touch_tip"]:
                pipette.touch_tip(wells)

        except Exception as e:
            protocol.comment(f"Error during batch dispense: {e}")
        finally:
            pipette.drop_tip()

    def simulate_batch_realistic_evaluation(wells, params, batch_idx):
        """Simulate realistic evaluation results for a batch of wells"""
        batch_scores = []

        for well_idx, well in enumerate(wells):
            # Calculate global well index
            global_well_idx = batch_idx * BATCH_SIZE + well_idx

            # Base score that varies with parameters
            base_score = 0.0

            # Parameter effects on score (simulated)
            # Lower aspiration rate generally better for bubble reduction
            aspiration_factor = max(0.1, 1.0 - (params["aspiration_rate"] - 50) / 450)
            aspiration_contribution = (1.0 - aspiration_factor) * 2.0
            base_score += aspiration_contribution

            # Lower dispense rate generally better
            dispense_factor = max(0.1, 1.0 - (params["dispense_rate"] - 50) / 450)
            dispense_contribution = (1.0 - dispense_factor) * 2.0
            base_score += dispense_contribution

            # Moderate blowout rate is optimal
            blowout_optimal = 50.0
            blowout_factor = 1.0 - abs(params["blowout_rate"] - blowout_optimal) / blowout_optimal
            blowout_contribution = (1.0 - max(0, blowout_factor)) * 1.5
            base_score += blowout_contribution

            # Delays can help but too much is bad
            delay_factor = min(1.0, (params["aspiration_delay"] + params["dispense_delay"]) / 2.0)
            delay_contribution = delay_factor * 0.5
            base_score += delay_contribution

            # Add some randomness and well position effects
            import random

            random.seed(global_well_idx)  # Consistent randomness per well
            noise = random.uniform(-0.5, 0.5)

            # Well position effects (edges vs center)
            well_row = ord(well.well_name[0]) - ord("A")
            well_col = int(well.well_name[1:]) - 1
            edge_factor = abs(well_row - 3.5) + abs(well_col - 3.5)  # Distance from center
            edge_penalty = edge_factor * 0.1

            # Add batch-specific effects (8-channel pipettes may have slight variations)
            batch_effect = (well_idx - 3.5) * 0.05  # Center channels slightly better

            final_score = max(0.0, base_score + noise + edge_penalty + batch_effect)
            batch_scores.append(final_score)

        return batch_scores

    # Main optimization loop - process wells in batches
    current_params = reference_params.copy()
    previous_params = reference_params.copy()
    best_score = float("inf")
    best_params = reference_params.copy()
    learning_rate = initial_learning_rate
    no_improvement_count = 0

    # Get all wells to test and organize into batches
    all_wells = test_plate.wells()[:SAMPLE_COUNT]
    batches = [
        all_wells[i : i + BATCH_SIZE] for i in range(0, len(all_wells), BATCH_SIZE)  # noqa: E203
    ]  # noqa: E203

    # Log initial setup
    protocol.comment("=" * 60)
    protocol.comment("8-CHANNEL LIQUID CLASS OPTIMIZATION STARTED")
    protocol.comment("=" * 60)
    protocol.comment(f"Testing {SAMPLE_COUNT} wells in {len(batches)} batches of {BATCH_SIZE}")
    protocol.comment(f"Pipette type: {PIPETTE_TYPE.value} (8-channel)")
    protocol.comment(f"Liquid type: {LIQUID_TYPE.value}")
    protocol.comment(f"Reference parameters: {reference_params}")
    protocol.comment(f"Initial learning rate: {initial_learning_rate}")
    protocol.comment("=" * 60)

    for batch_idx, batch_wells in enumerate(batches):
        well_start = batch_idx * BATCH_SIZE + 1
        well_end = batch_idx * BATCH_SIZE + len(batch_wells)
        protocol.comment(
            f"\n--- BATCH {batch_idx + 1}/{len(batches)}: " f"Wells {well_start}-{well_end} ---"
        )

        # Step 1.1: Generate parameter combination for this batch
        if batch_idx == 0:
            # First batch - use reference parameters
            current_params = reference_params.copy()
            protocol.comment("Using reference liquid class parameters for first batch")
        else:
            # Use gradient descent to update parameters
            if len(batch_data) >= 2:  # Need at least 2 data points for gradient
                last_result = batch_data[-1]
                second_last_result = batch_data[-2]

                protocol.comment(
                    f"Previous batch scores: {second_last_result['avg_bubblicity_score']:.3f} -> "
                    f"{last_result['avg_bubblicity_score']:.3f}"
                )

                # Calculate gradients based on last two results
                gradients = calculate_gradient_direction(
                    second_last_result["avg_bubblicity_score"],
                    last_result["avg_bubblicity_score"],
                    second_last_result["parameters"],
                    last_result["parameters"],
                )

                protocol.comment(f"Calculated gradients: {gradients}")

                # Update parameters using gradients
                current_params = update_parameters_with_gradient(
                    last_result["parameters"], gradients, learning_rate
                )

                protocol.comment(f"Learning rate: {learning_rate:.4f}")
                protocol.comment("Parameter changes:")
                for param in current_params:
                    if param in last_result["parameters"]:
                        change = current_params[param] - last_result["parameters"][param]
                        protocol.comment(
                            f"  {param}: {last_result['parameters'][param]:.2f} -> "
                            f"{current_params[param]:.2f} (Δ{change:+.2f})"
                        )
            else:
                # For second batch, make small random adjustments to explore
                current_params = previous_params.copy()
                protocol.comment("Making initial parameter adjustments for exploration:")
                for param in gradient_step.keys():
                    if param in current_params:
                        # Small random adjustment (±10% of step size)
                        adjustment = batch_idx * gradient_step[param] * 0.1
                        current_params[param] += adjustment
                        protocol.comment(
                            f"  {param}: {previous_params[param]:.2f} -> "
                            f"{current_params[param]:.2f} (Δ{adjustment:+.2f})"
                        )

            # Apply constraints
            constrained_params = apply_constraints(current_params)
            if constrained_params != current_params:
                protocol.comment("Parameters constrained to bounds:")
                for param in current_params:
                    if (
                        param in constrained_params
                        and current_params[param] != constrained_params[param]
                    ):
                        protocol.comment(
                            f"  {param}: {current_params[param]:.2f} -> "
                            f"{constrained_params[param]:.2f}"
                        )
            current_params = constrained_params

        protocol.comment(f"Current parameters: {current_params}")

        # Step 1.2: Execute batch dispense sequence
        protocol.comment("Executing batch dispense sequence...")
        execute_batch_dispense_sequence(batch_wells, pipette_1000_8ch, current_params)

        # Step 1.3 & 1.4: Evaluate liquid height and bubblicity for the batch
        # Pick up one tip for batch evaluations
        pipette_1000_8ch.pick_up_tip()

        try:
            # Step 1.3: Evaluate liquid height for batch
            protocol.comment("Evaluating liquid height for batch...")
            height_statuses = evaluate_batch_liquid_height(
                batch_wells, pipette_1000_8ch, expected_liquid_height
            )

            # Step 1.4: Evaluate bubblicity for batch (only if height checks pass)
            if not all(height_statuses):
                failed_wells = [
                    well for well, status in zip(batch_wells, height_statuses) if not status
                ]
                protocol.comment(
                    f"Liquid height check failed for wells: {[str(w) for w in failed_wells]}"
                )
                bubblicity_scores = [1000.0 if not status else 0.0 for status in height_statuses]
            else:
                # Use realistic simulation for evaluation
                bubblicity_scores = simulate_batch_realistic_evaluation(
                    batch_wells, current_params, batch_idx
                )
                protocol.comment(
                    f"Simulated bubblicity scores: {[f'{s:.3f}' for s in bubblicity_scores]}"
                )

        finally:
            # Drop the tip after batch evaluations
            pipette_1000_8ch.drop_tip()

        # Step 1.5: Record batch data
        avg_bubblicity_score = sum(bubblicity_scores) / len(bubblicity_scores)
        successful_wells = sum(height_statuses)

        batch_result = {
            "batch_id": batch_idx,
            "wells": [str(well) for well in batch_wells],
            "parameters": current_params.copy(),
            "height_statuses": height_statuses,
            "bubblicity_scores": bubblicity_scores,
            "avg_bubblicity_score": avg_bubblicity_score,
            "successful_wells": successful_wells,
            "total_wells": len(batch_wells),
        }
        batch_data.append(batch_result)

        # Track optimization progress
        if successful_wells > 0 and avg_bubblicity_score < best_score:
            best_score = avg_bubblicity_score
            best_params = current_params.copy()
            no_improvement_count = 0
            protocol.comment(f"🎉 NEW BEST BATCH SCORE: {best_score:.3f} in batch {batch_idx + 1}")
            protocol.comment(f"Best parameters so far: {best_params}")
        else:
            no_improvement_count += 1
            if successful_wells > 0:
                protocol.comment(
                    f"Batch score: {avg_bubblicity_score:.3f} (no improvement, count: "
                    f"{no_improvement_count})"
                )
            else:
                protocol.comment("All height checks failed - skipping optimization")

        # Learning rate decay
        if no_improvement_count >= patience:
            old_learning_rate = learning_rate
            learning_rate = max(min_learning_rate, learning_rate * learning_rate_decay)
            no_improvement_count = 0
            protocol.comment(
                f"📉 Reducing learning rate: {old_learning_rate:.4f} -> " f"{learning_rate:.4f}"
            )

        protocol.comment(
            f"Progress: {batch_idx + 1}/{len(batches)} batches, "
            f"Best score: {best_score:.3f}, "
            f"Learning rate: {learning_rate:.4f}, "
            f"Success rate: {successful_wells}/{len(batch_wells)} wells"
        )

        # Store optimization history
        optimization_history.append(
            {
                "iteration": batch_idx,
                "learning_rate": learning_rate,
                "current_score": avg_bubblicity_score,
                "best_score": best_score,
                "no_improvement_count": no_improvement_count,
                "successful_wells": successful_wells,
            }
        )

        # Update for next iteration
        previous_params = current_params.copy()

    # Find optimal parameters
    protocol.comment("\n" + "=" * 60)
    protocol.comment("8-CHANNEL OPTIMIZATION COMPLETE - FINAL ANALYSIS")
    protocol.comment("=" * 60)

    if batch_data:
        # Filter successful batches and find minimum bubblicity
        successful_batches = [r for r in batch_data if r["successful_wells"] > 0]

        if successful_batches:
            # Use the best parameters found during optimization
            optimal_result = min(successful_batches, key=lambda x: x["avg_bubblicity_score"])
            protocol.comment(
                f"🏆 OPTIMAL PARAMETERS FOUND IN: Batch {optimal_result['batch_id'] + 1}"
            )
            protocol.comment(
                f"🏆 OPTIMAL BUBBLICITY SCORE: {optimal_result['avg_bubblicity_score']:.3f}"
            )
            protocol.comment("🏆 OPTIMAL PARAMETERS:")
            for param, value in optimal_result["parameters"].items():
                protocol.comment(f"    {param}: {value:.2f}")

            # Compare with reference parameters
            protocol.comment("\n📊 PARAMETER COMPARISON (Reference → Optimal):")
            for param in optimal_result["parameters"]:
                if param in reference_params:
                    ref_val = reference_params[param]
                    opt_val = optimal_result["parameters"][param]
                    change = opt_val - ref_val
                    change_pct = (change / ref_val) * 100 if ref_val != 0 else 0
                    protocol.comment(
                        f"    {param}: {ref_val:.2f} → {opt_val:.2f} "
                        f"(Δ{change:+.2f}, {change_pct:+.1f}%)"
                    )

            # Additional analysis
            protocol.comment("\n📈 BATCH OPTIMIZATION STATISTICS:")
            protocol.comment(f"    Total batches tested: {len(batch_data)}")
            protocol.comment(f"    Successful batches: {len(successful_batches)}")
            protocol.comment(
                f"    Batch success rate: {len(successful_batches)/len(batch_data)*100:.1f}%"
            )

            # Well-level statistics
            total_wells_tested = sum(batch["total_wells"] for batch in batch_data)
            total_successful_wells = sum(batch["successful_wells"] for batch in batch_data)
            protocol.comment(f"    Total wells tested: {total_wells_tested}")
            protocol.comment(f"    Successful wells: {total_successful_wells}")
            protocol.comment(
                f"    Well success rate: {total_successful_wells/total_wells_tested*100:.1f}%"
            )

            # Optimization statistics
            if optimization_history:
                final_learning_rate = optimization_history[-1]["learning_rate"]
                best_score_found = optimization_history[-1]["best_score"]
                protocol.comment(f"    Final learning rate: {final_learning_rate:.4f}")
                protocol.comment(f"    Best score achieved: {best_score_found:.3f}")

                # Show improvement over iterations
                if len(optimization_history) > 1:
                    initial_score = optimization_history[0]["current_score"]
                    improvement = initial_score - best_score_found
                    improvement_pct = (
                        (improvement / initial_score) * 100 if initial_score != 0 else 0
                    )
                    protocol.comment(
                        f"    Total improvement: {improvement:.3f} (" f"{improvement_pct:+.1f}%)"
                    )

                    # Show convergence analysis
                    recent_scores = [h["current_score"] for h in optimization_history[-3:]]
                    if len(recent_scores) >= 2:
                        score_variance = sum(
                            (s - sum(recent_scores) / len(recent_scores)) ** 2
                            for s in recent_scores
                        ) / len(recent_scores)
                        protocol.comment(f"    Recent score variance: {score_variance:.4f}")
                        if score_variance < convergence_threshold:
                            protocol.comment("    ✅ Algorithm appears to have converged")
                        else:
                            protocol.comment(
                                "    ⚠️  Algorithm may need more iterations to converge"
                            )

                # Show learning rate history
                learning_rate_changes = []
                for i in range(1, len(optimization_history)):
                    if (
                        optimization_history[i]["learning_rate"]
                        != optimization_history[i - 1]["learning_rate"]
                    ):
                        learning_rate_changes.append(
                            {
                                "iteration": optimization_history[i]["iteration"],
                                "old_rate": optimization_history[i - 1]["learning_rate"],
                                "new_rate": optimization_history[i]["learning_rate"],
                            }
                        )

                if learning_rate_changes:
                    protocol.comment(f"    Learning rate changes: {len(learning_rate_changes)}")
                    for change in learning_rate_changes:
                        protocol.comment(
                            f"      Iteration {change['iteration']}: "
                            f"{change['old_rate']:.4f} → {change['new_rate']:.4f}"
                        )

                # Show score progression
                protocol.comment("\n📉 SCORE PROGRESSION:")
                protocol.comment(
                    f"    Initial score: {optimization_history[0]['current_score']:.3f}"
                )
                protocol.comment(
                    f"    Final score: {optimization_history[-1]['current_score']:.3f}"
                )

                # Find iterations with improvements
                improvements = []
                for i in range(1, len(optimization_history)):
                    if (
                        optimization_history[i]["best_score"]
                        < optimization_history[i - 1]["best_score"]
                    ):
                        improvements.append(
                            {
                                "iteration": optimization_history[i]["iteration"],
                                "improvement": optimization_history[i - 1]["best_score"]
                                - optimization_history[i]["best_score"],
                            }
                        )

                if improvements:
                    protocol.comment(f"    Major improvements: {len(improvements)}")
                    for imp in improvements:
                        protocol.comment(
                            f"      Iteration {imp['iteration']}: +{imp['improvement']:.3f}"
                        )

                # 8-channel specific analysis
                protocol.comment("\n🔬 8-CHANNEL SPECIFIC ANALYSIS:")
                avg_success_rate = sum(h["successful_wells"] for h in optimization_history) / len(
                    optimization_history
                )
                protocol.comment(
                    f"    Average successful wells per batch: {avg_success_rate:.1f}/{BATCH_SIZE}"
                )

                # Channel consistency analysis
                if batch_data:
                    channel_variations = []
                    for batch in batch_data:
                        if batch["successful_wells"] > 0:
                            scores = batch["bubblicity_scores"]
                            if len(scores) > 1:
                                variation = max(scores) - min(scores)
                                channel_variations.append(variation)

                    if channel_variations:
                        avg_variation = sum(channel_variations) / len(channel_variations)
                        protocol.comment(
                            f"    Average channel-to-channel variation: {avg_variation:.3f}"
                        )
                        if avg_variation < 0.5:
                            protocol.comment("    ✅ Good channel consistency")
                        elif avg_variation < 1.0:
                            protocol.comment("    ⚠️  Moderate channel variation")
                        else:
                            protocol.comment("    ❌ High channel variation detected")

        else:
            protocol.comment("❌ No successful batch results found")
            protocol.comment("   This may indicate issues with liquid handling or evaluation")

    protocol.comment("\n" + "=" * 60)
    protocol.comment("8-CHANNEL LIQUID CLASS CALIBRATION PROTOCOL COMPLETED")
    protocol.comment("=" * 60)
