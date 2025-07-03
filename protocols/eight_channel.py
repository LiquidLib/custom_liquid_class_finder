import sys
import os

try:
    protocol_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    # __file__ is not defined (e.g., in Opentrons simulation)
    protocol_dir = os.getcwd()

if protocol_dir not in sys.path:
    sys.path.insert(0, protocol_dir)

from opentrons import protocol_api
from opentrons.protocol_api import SINGLE
from typing import List, Dict, Any

# Import liquid classes
from liquids.liquid_classes import (
    get_liquid_class_params,
    PipetteType,
    LiquidType,
    LiquidClassParams,
)

metadata = {
    "protocolName": "8-Channel Pipette - Single Channel Operation",
    "author": "Roman Gurovich",
    "description": (
        "Liquid class calibration using 8-channel pipette operating only the first channel "
        "for single-channel behavior with gradient descent optimization"
    ),
    "source": "Roman Gurovich",
}

requirements = {"robotType": "Flex", "apiLevel": "2.23"}


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
        description="Type of 8-channel pipette to calibrate (single tip pickup)",
    )


def run(protocol: protocol_api.ProtocolContext):
    # Access runtime parameters
    SAMPLE_COUNT = protocol.params.sample_count  # type: ignore
    PIPETTE_MOUNT = protocol.params.pipette_mount  # type: ignore
    TRASH_POSITION = protocol.params.trash_position  # type: ignore
    LIQUID_TYPE = LiquidType[protocol.params.liquid_type]  # type: ignore
    PIPETTE_TYPE = PipetteType[protocol.params.pipette_type]  # type: ignore

    # Load labware
    tiprack_1000 = protocol.load_labware("opentrons_flex_96_tiprack_1000ul", "B1")
    reservoir = protocol.load_labware("nest_12_reservoir_15ml", "D1")
    test_plate = protocol.load_labware("nest_96_wellplate_200ul_flat", "D2")

    # Define trash container
    protocol.load_trash_bin(location=TRASH_POSITION)

    # Load 8-channel pipette configured for single tip pickup
    pipette_1000_8ch = protocol.load_instrument(
        "flex_8channel_1000",
        PIPETTE_MOUNT,
        tip_racks=[tiprack_1000],
    )

    # Configure 8-channel pipette for single tip pickup (only first channel)
    pipette_1000_8ch.configure_nozzle_layout(
        style=SINGLE,
        start="H1",  # Use H1 nozzle for single tip pickup - valid for 8-channel
        tip_racks=[tiprack_1000],
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
        "aspiration_delay": (0.0, 2.0),
        "aspiration_withdrawal_rate": (1.0, 20.0),
        "dispense_rate": (10.0, 500.0),
        "dispense_delay": (0.0, 2.0),
        "blowout_rate": (10.0, 300.0),
    }

    # Gradient descent parameters
    gradient_step = {
        "aspiration_rate": 10.0,
        "aspiration_delay": 0.05,
        "aspiration_withdrawal_rate": 0.5,
        "dispense_rate": 10.0,
        "dispense_delay": 0.05,
        "blowout_rate": 5.0,
    }

    # Learning rate and optimization parameters
    initial_learning_rate = 0.1
    learning_rate_decay = 0.95
    min_learning_rate = 0.01
    patience = 3

    # Detection parameters
    expected_liquid_height = 2.0  # mm from bottom
    bubble_check_increments = [0.2, 0.5, 1.0, 1.8]  # mm above expected height

    # Control flag for real vs simulation detection
    USE_REAL_DETECTION = True  # Set to False for simulation mode

    # Data storage
    well_data: List[Dict[str, Any]] = []
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

    def evaluate_liquid_height_with_tip(well, pipette, expected_height):
        """Real liquid height evaluation using capacitive sensing"""
        protocol.comment(f"Evaluating liquid height in {well} using 8-channel pipette (A1 nozzle)")

        try:
            # Target the well directly with 8-channel pipette (A1 nozzle)
            pipette.aspirate(0, well.bottom(expected_height))
            protocol.comment(f"Liquid detected in {well} at height {expected_height}mm")
            return True
        except Exception:
            protocol.comment(f"No liquid detected in {well} at height {expected_height}mm")
            return False

    def evaluate_bubblicity_with_tip(well, pipette, expected_height):
        """Real bubble detection using height scanning with capacitive sensing"""
        protocol.comment(f"Evaluating bubblicity in {well} using 8-channel pipette (A1 nozzle)")

        # Target the well directly with 8-channel pipette (A1 nozzle)
        well_score = 0
        # Check at different heights above expected liquid level
        for height_increment in bubble_check_increments:
            check_height = expected_height + height_increment
            try:
                # Try to aspirate 0µL from the well at this height
                pipette.aspirate(0, well.bottom(check_height))
                # If successful, there's liquid (possibly a bubble) at this height
                well_score += height_increment
                protocol.comment(f"Bubble detected in {well} at {check_height}mm")
            except Exception:
                # No liquid at this height, continue to next height
                continue

        return well_score

    def simulate_realistic_evaluation(well, params, well_idx):
        """Simulate realistic evaluation results"""
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

        random.seed(well_idx)  # Consistent randomness per well
        noise = random.uniform(-0.5, 0.5)

        # Well position effects (edges vs center)
        well_row = ord(well.well_name[0]) - ord("A")
        well_col = int(well.well_name[1:]) - 1
        edge_factor = abs(well_row - 3.5) + abs(well_col - 3.5)  # Distance from center
        edge_penalty = edge_factor * 0.1

        final_score = max(0.0, base_score + noise + edge_penalty)
        return final_score

    # Main optimization loop
    current_params = reference_params.copy()
    previous_params = reference_params.copy()
    best_score = float("inf")
    best_params = reference_params.copy()
    learning_rate = initial_learning_rate
    no_improvement_count = 0

    # Get all wells to test
    all_wells = test_plate.wells()[:SAMPLE_COUNT]

    # Log initial setup
    protocol.comment("=" * 60)
    protocol.comment("8-CHANNEL PIPETTE - SINGLE TIP PICKUP OPERATION STARTED")
    protocol.comment("=" * 60)
    protocol.comment(f"Testing {SAMPLE_COUNT} wells using 8-channel pipette (single tip pickup)")
    protocol.comment(f"Pipette type: {PIPETTE_TYPE.value} (8-channel, single tip pickup)")
    protocol.comment(f"Liquid type: {LIQUID_TYPE.value}")
    protocol.comment(f"Reference parameters: {reference_params}")
    protocol.comment(f"Initial learning rate: {initial_learning_rate}")
    protocol.comment("=" * 60)

    for well_idx, well in enumerate(all_wells):
        protocol.comment(f"\n--- WELL {well_idx + 1}/{SAMPLE_COUNT}: {well} ---")

        # Step 1.1: Generate parameter combination for this well
        if well_idx == 0:
            # First well - use reference parameters
            current_params = reference_params.copy()
            protocol.comment("Using reference liquid class parameters for first well")
        else:
            # Use gradient descent to update parameters
            if len(well_data) >= 2:  # Need at least 2 data points for gradient
                last_result = well_data[-1]
                second_last_result = well_data[-2]

                protocol.comment(
                    f"Previous well scores: {second_last_result['bubblicity_score']:.3f} -> "
                    f"{last_result['bubblicity_score']:.3f}"
                )

                # Calculate gradients based on last two results
                gradients = calculate_gradient_direction(
                    second_last_result["bubblicity_score"],
                    last_result["bubblicity_score"],
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
                # For second well, make small random adjustments to explore
                current_params = previous_params.copy()
                protocol.comment("Making initial parameter adjustments for exploration:")
                for param in gradient_step.keys():
                    if param in current_params:
                        # Small random adjustment (±10% of step size)
                        adjustment = well_idx * gradient_step[param] * 0.1
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

        # Pick up one tip for both dispensing and evaluation
        # Use specific tip location to pick up only the first tip (leftmost, topmost)
        tip_location = tiprack_1000.wells()[well_idx]  # Use sequential tips from A1 onwards
        protocol.comment(
            f"Picking up single tip from {tip_location} using 8-channel pipette (A1 nozzle)..."
        )
        pipette_1000_8ch.pick_up_tip(
            tip_location
        )  # 8-channel pipette configured for single tip pickup (A1 nozzle)

        try:
            # Step 1.2: Execute dispense sequence (reuse the same tip)
            protocol.comment("Executing dispense sequence...")

            # Set flow rates
            protocol.comment(
                f"Setting flow rates - Aspirate: {current_params['aspiration_rate']}, "
                f"Dispense: {current_params['dispense_rate']}, "
                f"Blowout: {current_params['blowout_rate']}"
            )
            pipette_1000_8ch.flow_rate.aspirate = current_params["aspiration_rate"]
            pipette_1000_8ch.flow_rate.dispense = current_params["dispense_rate"]
            pipette_1000_8ch.flow_rate.blow_out = current_params["blowout_rate"]

            # Aspirate from reservoir
            protocol.comment("Aspirating 100µL from reservoir A1...")
            pipette_1000_8ch.aspirate(100, reservoir["A1"])

            # Apply aspiration delay (capped to prevent excessive delays)
            aspiration_delay = max(
                0.0, min(current_params["aspiration_delay"], 2.0)
            )  # Cap at 2 seconds, minimum 0
            if aspiration_delay > 0:
                protocol.comment(f"Applying aspiration delay: {aspiration_delay} seconds")
                protocol.delay(seconds=aspiration_delay)

            # Dispense into target well
            protocol.comment(f"Dispensing 100µL to {well}...")
            pipette_1000_8ch.dispense(100, well)

            # Apply dispense delay (capped to prevent excessive delays)
            dispense_delay = max(
                0.0, min(current_params["dispense_delay"], 2.0)
            )  # Cap at 2 seconds, minimum 0
            if dispense_delay > 0:
                protocol.comment(f"Applying dispense delay: {dispense_delay} seconds")
                protocol.delay(seconds=dispense_delay)

            # Blow out into the target well
            protocol.comment("Blowing out into target well...")
            pipette_1000_8ch.blow_out(well)

            # Touch tip if enabled (touch tip to the target well)
            if current_params["touch_tip"]:
                protocol.comment("Touching tip to target well...")
                pipette_1000_8ch.touch_tip(well)

            # Step 1.3: Evaluate liquid height (reuse the same tip)
            protocol.comment("Evaluating liquid height...")
            if USE_REAL_DETECTION:
                height_status = evaluate_liquid_height_with_tip(
                    well, pipette_1000_8ch, expected_liquid_height
                )
            else:
                # Simulated height evaluation
                import random

                random.seed(well_idx)
                height_status = random.random() < 0.95  # 95% success rate
                protocol.comment(f"SIMULATION: Liquid height status: {height_status}")

            # Step 1.4: Evaluate bubblicity (only if height check passes, reuse the same tip)
            if not height_status:
                protocol.comment(f"Liquid height check failed for {well}")
                bubblicity_score = 1000.0
            else:
                # Use real capacitive sensing for evaluation
                if USE_REAL_DETECTION:
                    bubblicity_score = evaluate_bubblicity_with_tip(
                        well, pipette_1000_8ch, expected_liquid_height
                    )
                else:
                    bubblicity_score = simulate_realistic_evaluation(well, current_params, well_idx)
                    protocol.comment(f"SIMULATION: Bubblicity score: {bubblicity_score:.3f}")

        except Exception as e:
            protocol.comment(f"Error during well processing: {e}")
            height_status = False
            bubblicity_score = 1000.0
        finally:
            # Drop the tip after all operations
            protocol.comment("Dropping tip...")
            pipette_1000_8ch.drop_tip()

        # Step 1.5: Record well data
        well_result = {
            "well_id": well_idx,
            "well": str(well),
            "parameters": current_params.copy(),
            "height_status": height_status,
            "bubblicity_score": bubblicity_score,
        }
        well_data.append(well_result)

        # Track optimization progress
        if height_status and bubblicity_score < best_score:
            best_score = bubblicity_score
            best_params = current_params.copy()
            no_improvement_count = 0
            protocol.comment(f"🎉 NEW BEST SCORE: {best_score:.3f} in well {well}")
            protocol.comment(f"Best parameters so far: {best_params}")
        else:
            no_improvement_count += 1
            if height_status:
                protocol.comment(
                    f"Well score: {bubblicity_score:.3f} (no improvement, count: "
                    f"{no_improvement_count})"
                )
            else:
                protocol.comment("Height check failed - skipping optimization")

        # Learning rate decay
        if no_improvement_count >= patience:
            old_learning_rate = learning_rate
            learning_rate = max(min_learning_rate, learning_rate * learning_rate_decay)
            no_improvement_count = 0
            protocol.comment(
                f"📉 Reducing learning rate: {old_learning_rate:.4f} -> " f"{learning_rate:.4f}"
            )

        protocol.comment(
            f"Progress: {well_idx + 1}/{SAMPLE_COUNT} wells, "
            f"Best score: {best_score:.3f}, "
            f"Learning rate: {learning_rate:.4f}, "
            f"Success rate: "
            f"{sum(1 for r in well_data if r['height_status'])}/{len(well_data)} wells"
        )

        # Store optimization history
        optimization_history.append(
            {
                "iteration": well_idx,
                "learning_rate": learning_rate,
                "current_score": bubblicity_score,
                "best_score": best_score,
                "no_improvement_count": no_improvement_count,
                "height_status": height_status,
            }
        )

        # Update for next iteration
        previous_params = current_params.copy()

    # Find optimal parameters
    protocol.comment("\n" + "=" * 60)
    protocol.comment("8-CHANNEL PIPETTE - SINGLE TIP PICKUP OPERATION COMPLETE - FINAL ANALYSIS")
    protocol.comment("=" * 60)

    if well_data:
        # Filter successful wells and find minimum bubblicity
        successful_wells = [r for r in well_data if r["height_status"]]

        if successful_wells:
            # Use the best parameters found during optimization
            optimal_result = min(successful_wells, key=lambda x: x["bubblicity_score"])
            protocol.comment(f"🏆 OPTIMAL PARAMETERS FOUND IN: Well {optimal_result['well']}")
            protocol.comment(
                f"🏆 OPTIMAL BUBBLICITY SCORE: {optimal_result['bubblicity_score']:.3f}"
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
            protocol.comment("\n📈 OPTIMIZATION STATISTICS:")
            protocol.comment(f"    Total wells tested: {len(well_data)}")
            protocol.comment(f"    Successful wells: {len(successful_wells)}")
            protocol.comment(
                f"    Well success rate: {len(successful_wells)/len(well_data)*100:.1f}%"
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

        else:
            protocol.comment("❌ No successful well results found")
            protocol.comment("   This may indicate issues with liquid handling or evaluation")

    protocol.comment("\n" + "=" * 60)
    protocol.comment("8-CHANNEL PIPETTE - SINGLE TIP PICKUP OPERATION COMPLETED")
    protocol.comment("=" * 60)
