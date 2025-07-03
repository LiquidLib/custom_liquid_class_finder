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

# Import optimization strategies
from protocols.optimization_strategies import OptimizationStrategyFactory, OptimizationStrategy

metadata = {
    "protocolName": "Liquid Class Calibration with Pluggable Optimization",
    "author": "Roman Gurovich",
    "description": (
        "Calibration protocol using pluggable optimization strategies "
        "for liquid handling parameters"
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
        description="Type of pipette to calibrate",
    )
    parameters.add_str(
        display_name="Optimization strategy",
        variable_name="optimization_strategy",
        choices=[
            {"display_name": "Simultaneous Gradient Descent", "value": "simultaneous"},
            {"display_name": "Hybrid Hierarchical", "value": "hybrid"},
            {"display_name": "Coordinate Descent", "value": "coordinate"},
        ],
        default="simultaneous",
        description="Optimization strategy to use for parameter tuning",
    )


def run(protocol: protocol_api.ProtocolContext):
    # Access runtime parameters
    SAMPLE_COUNT = protocol.params.sample_count  # type: ignore
    PIPETTE_MOUNT = protocol.params.pipette_mount  # type: ignore
    TRASH_POSITION = protocol.params.trash_position  # type: ignore
    LIQUID_TYPE = LiquidType[protocol.params.liquid_type]  # type: ignore
    PIPETTE_TYPE = PipetteType[protocol.params.pipette_type]  # type: ignore
    OPTIMIZATION_STRATEGY = protocol.params.optimization_strategy  # type: ignore

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

    # Calculate pipette-specific parameter bounds
    param_bounds = OptimizationStrategy.calculate_pipette_specific_bounds(
        PIPETTE_TYPE.value, LIQUID_TYPE.value
    )

    protocol.comment(
        f"📊 Using pipette-specific bounds for {PIPETTE_TYPE.value} with {LIQUID_TYPE.value}:"
    )
    for param, (min_val, max_val) in param_bounds.items():
        protocol.comment(f"    {param}: {min_val:.1f} - {max_val:.1f}")

    # Initialize optimization strategy
    try:
        optimization_strategy = OptimizationStrategyFactory.create_strategy(
            OPTIMIZATION_STRATEGY, reference_params, param_bounds, SAMPLE_COUNT
        )
        protocol.comment(
            f"✅ Using optimization strategy: {optimization_strategy.get_strategy_name()}"
        )
        protocol.comment(
            f"📝 Strategy description: {optimization_strategy.get_strategy_description()}"
        )

        # Show phase allocation for hybrid strategy
        phase_configs = getattr(optimization_strategy, "phase_configs", None)
        if phase_configs:
            protocol.comment("📊 Phase allocation:")
            for phase_name, config in phase_configs.items():
                protocol.comment(
                    f"    {phase_name}: {config['wells_per_phase']} wells - {config['description']}"
                )
    except ValueError as e:
        protocol.comment(f"❌ Error creating optimization strategy: {e}")
        protocol.comment(
            "Available strategies: "
            + ", ".join(OptimizationStrategyFactory.get_available_strategies())
        )
        return

    # Optimization parameters are now handled by the strategy classes

    # Learning rate and optimization parameters
    initial_learning_rate = 0.1
    learning_rate_decay = 0.95
    min_learning_rate = 0.01
    convergence_threshold = 0.1
    patience = 5  # Number of iterations without improvement before reducing learning rate

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
    optimization_history: List[Dict[str, Any]] = []

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

    def simulate_realistic_evaluation(well, params, well_idx):
        """Simulate realistic evaluation results based on parameters and well position"""
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

        # Log evaluation breakdown
        protocol.comment("  Evaluation breakdown:")
        protocol.comment(
            f"    Aspiration factor: {aspiration_factor:.3f} "
            f"(contribution: {aspiration_contribution:.3f})"
        )
        protocol.comment(
            f"    Dispense factor: {dispense_factor:.3f} "
            f"(contribution: {dispense_contribution:.3f})"
        )
        protocol.comment(
            f"    Blowout factor: {blowout_factor:.3f} "
            f"(contribution: {blowout_contribution:.3f})"
        )
        protocol.comment(
            f"    Delay factor: {delay_factor:.3f} " f"(contribution: {delay_contribution:.3f})"
        )
        protocol.comment(f"    Base score: {base_score:.3f}")
        protocol.comment(f"    Noise: {noise:+.3f}")
        protocol.comment(f"    Edge penalty: {edge_penalty:.3f}")
        protocol.comment(f"    Final score: {final_score:.3f}")

        return final_score

    # Main optimization loop - test all wells individually
    current_params = reference_params.copy()
    best_score = float("inf")
    best_params = reference_params.copy()
    learning_rate = initial_learning_rate
    no_improvement_count = 0

    # Get all wells to test
    test_wells = test_plate.wells()[:SAMPLE_COUNT]

    # Log initial setup
    protocol.comment("=" * 60)
    protocol.comment("PLUGGABLE OPTIMIZATION STRATEGY STARTED")
    protocol.comment("=" * 60)
    protocol.comment(f"Testing {SAMPLE_COUNT} wells with {PIPETTE_TYPE.value} pipette")
    protocol.comment(f"Liquid type: {LIQUID_TYPE.value}")
    protocol.comment(f"Optimization strategy: {optimization_strategy.get_strategy_name()}")
    protocol.comment(f"Strategy description: {optimization_strategy.get_strategy_description()}")
    protocol.comment(f"Reference parameters: {reference_params}")
    protocol.comment(f"Initial learning rate: {initial_learning_rate}")
    protocol.comment("=" * 60)

    for well_idx, well in enumerate(test_wells):
        protocol.comment(f"\n--- WELL {well_idx + 1}/{SAMPLE_COUNT}: {well} ---")

        # Generate parameters using the optimization strategy
        current_params = optimization_strategy.generate_parameters(
            well_idx, well_data, learning_rate
        )

        # Log parameter generation
        if well_idx == 0:
            protocol.comment("Using reference liquid class parameters for first well")
        else:
            protocol.comment(
                f"Generated parameters using {optimization_strategy.get_strategy_name()}"
            )
            # Check for phase information (hybrid strategy specific)
            current_phase = getattr(optimization_strategy, "current_phase", None)
            if current_phase:
                protocol.comment(f"Current phase: {current_phase}")

        protocol.comment(f"Current parameters: {current_params}")

        # Step 1.2: Execute dispense sequence targeting individual well
        protocol.comment("Executing dispense sequence...")
        execute_dispense_sequence(well, pipette_1000, current_params)

        # Step 1.3 & 1.4: Evaluate liquid height and bubblicity using the same tip
        # Pick up one tip for both evaluations
        pipette_50.pick_up_tip()

        try:
            # Step 1.3: Evaluate liquid height targeting individual well
            protocol.comment("Evaluating liquid height...")
            height_status = evaluate_liquid_height_with_tip(
                well, pipette_50, expected_liquid_height
            )

            # Step 1.4: Evaluate bubblicity targeting individual well (only if height check passes)
            if not height_status:
                bubblicity_score = 1000.0  # Artificially high value for failed height
                protocol.comment("Liquid height check failed - setting high bubblicity score")
            else:
                # Use realistic simulation for evaluation
                bubblicity_score = simulate_realistic_evaluation(well, current_params, well_idx)
                protocol.comment(f"Simulated bubblicity score: {bubblicity_score:.3f}")

        finally:
            # Drop the tip after both evaluations
            pipette_50.drop_tip()

        # Record well data
        well_result = {
            "well_id": str(well),
            "well_index": well_idx,
            "parameters": current_params.copy(),
            "height_status": height_status,
            "bubblicity_score": bubblicity_score,
        }
        well_data.append(well_result)

        # Record result in optimization strategy
        optimization_strategy.record_result(
            well_idx, current_params, bubblicity_score, height_status, learning_rate
        )

        # Track optimization progress
        if height_status and bubblicity_score < best_score:
            best_score = bubblicity_score
            best_params = current_params.copy()
            no_improvement_count = 0
            protocol.comment(f"🎉 NEW BEST SCORE: {best_score:.3f} in {well}")
            protocol.comment(f"Best parameters so far: {best_params}")
        else:
            no_improvement_count += 1
            if height_status:
                protocol.comment(
                    f"Score: {bubblicity_score:.3f} (no improvement, count: "
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
            f"Learning rate: {learning_rate:.4f}"
        )

        # Store optimization history
        optimization_history.append(
            {
                "iteration": well_idx,
                "learning_rate": learning_rate,
                "current_score": bubblicity_score,
                "best_score": best_score,
                "no_improvement_count": no_improvement_count,
            }
        )

        # Update for next iteration (parameters handled by strategy)

    # Find optimal parameters
    protocol.comment("\n" + "=" * 60)
    protocol.comment("PLUGGABLE OPTIMIZATION STRATEGY COMPLETE - FINAL ANALYSIS")
    protocol.comment("=" * 60)

    if well_data:
        # Filter successful height results and find minimum bubblicity
        successful_results = [r for r in well_data if r["height_status"]]

        if successful_results:
            # Use the best parameters found during optimization
            optimal_result = min(successful_results, key=lambda x: x["bubblicity_score"])
            protocol.comment(f"🏆 OPTIMAL PARAMETERS FOUND IN: {optimal_result['well_id']}")
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

            # Strategy-specific analysis
            protocol.comment("\n🔧 OPTIMIZATION STRATEGY ANALYSIS:")
            protocol.comment(f"    Strategy used: {optimization_strategy.get_strategy_name()}")
            protocol.comment(
                f"    Strategy description: {optimization_strategy.get_strategy_description()}"
            )

            # Show strategy-specific statistics
            if hasattr(optimization_strategy, "optimization_history"):
                strategy_history = optimization_strategy.optimization_history
                protocol.comment(f"    Strategy iterations: {len(strategy_history)}")
                if strategy_history:
                    protocol.comment(
                        f"    Strategy best score: {optimization_strategy.best_score:.3f}"
                    )

            # Additional analysis
            protocol.comment("\n📈 OPTIMIZATION STATISTICS:")
            protocol.comment(f"    Total wells tested: {len(well_data)}")
            protocol.comment(f"    Successful height checks: {len(successful_results)}")
            protocol.comment(f"    Success rate: {len(successful_results)/len(well_data)*100:.1f}%")

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
                    recent_scores = [h["current_score"] for h in optimization_history[-5:]]
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
        else:
            protocol.comment("❌ No successful liquid height results found")
            protocol.comment("   This may indicate issues with liquid handling or evaluation")

    protocol.comment("\n" + "=" * 60)
    protocol.comment("PLUGGABLE OPTIMIZATION STRATEGY PROTOCOL COMPLETED")
    protocol.comment("=" * 60)
