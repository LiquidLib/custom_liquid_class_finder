#!/usr/bin/env python3
"""
Test script to demonstrate the improved gradient descent optimization
for liquid class calibration.
"""

import random
import math
from typing import Dict, List, Any


def simulate_realistic_evaluation(params: Dict[str, float], iteration: int) -> float:
    """Simulate realistic evaluation results based on parameters"""
    # Base score that varies with parameters
    base_score = 0.0

    # Parameter effects on score (simulated)
    # Lower aspiration rate generally better for bubble reduction
    aspiration_factor = max(0.1, 1.0 - (params["aspiration_rate"] - 50) / 450)
    base_score += (1.0 - aspiration_factor) * 2.0

    # Lower dispense rate generally better
    dispense_factor = max(0.1, 1.0 - (params["dispense_rate"] - 50) / 450)
    base_score += (1.0 - dispense_factor) * 2.0

    # Moderate blowout rate is optimal
    blowout_optimal = 50.0
    blowout_factor = 1.0 - abs(params["blowout_rate"] - blowout_optimal) / blowout_optimal
    base_score += (1.0 - max(0, blowout_factor)) * 1.5

    # Delays can help but too much is bad
    delay_factor = min(1.0, (params["aspiration_delay"] + params["dispense_delay"]) / 2.0)
    base_score += delay_factor * 0.5

    # Add some randomness
    random.seed(iteration)
    noise = random.uniform(-0.2, 0.2)

    final_score = max(0.0, base_score + noise)
    return final_score


def calculate_gradient_direction(
    previous_score: float,
    current_score: float,
    previous_params: Dict[str, float],
    current_params: Dict[str, float],
) -> Dict[str, float]:
    """Calculate gradient direction for each parameter"""
    if previous_score == float("inf"):
        return {param: 0.0 for param in current_params.keys()}

    gradients = {}
    for param in current_params.keys():
        if param in previous_params:
            param_change = current_params[param] - previous_params[param]
            if abs(param_change) > 1e-6:
                score_change = current_score - previous_score
                gradients[param] = -score_change / param_change
            else:
                gradients[param] = 0.0
        else:
            gradients[param] = 0.0

    return gradients


def update_parameters_with_gradient(
    current_params: Dict[str, float],
    gradients: Dict[str, float],
    learning_rate: float,
    gradient_step: Dict[str, float],
) -> Dict[str, float]:
    """Update parameters using calculated gradients"""
    updated_params = current_params.copy()

    for param, gradient in gradients.items():
        if param in updated_params:
            step = learning_rate * gradient_step[param] * gradient
            updated_params[param] += step

    return updated_params


def apply_constraints(params: Dict[str, float], param_bounds: Dict[str, tuple]) -> Dict[str, float]:
    """Apply parameter constraints"""
    constrained_params = params.copy()
    for param, (min_val, max_val) in param_bounds.items():
        if param in constrained_params:
            constrained_params[param] = max(min_val, min(max_val, constrained_params[param]))
    return constrained_params


def test_optimization():
    """Test the improved optimization algorithm"""

    # Initial parameters
    reference_params = {
        "aspiration_rate": 150.0,
        "aspiration_delay": 1.0,
        "aspiration_withdrawal_rate": 5.0,
        "dispense_rate": 150.0,
        "dispense_delay": 1.0,
        "blowout_rate": 100.0,
    }

    # Parameter bounds
    param_bounds = {
        "aspiration_rate": (10.0, 500.0),
        "aspiration_delay": (0.0, 5.0),
        "aspiration_withdrawal_rate": (1.0, 20.0),
        "dispense_rate": (10.0, 500.0),
        "dispense_delay": (0.0, 5.0),
        "blowout_rate": (10.0, 300.0),
    }

    # Gradient step sizes
    gradient_step = {
        "aspiration_rate": 10.0,
        "aspiration_delay": 0.1,
        "aspiration_withdrawal_rate": 0.5,
        "dispense_rate": 10.0,
        "dispense_delay": 0.1,
        "blowout_rate": 5.0,
    }

    # Optimization parameters
    initial_learning_rate = 0.1
    learning_rate_decay = 0.95
    min_learning_rate = 0.01
    patience = 5

    # Initialize
    current_params = reference_params.copy()
    previous_params = reference_params.copy()
    previous_score = float("inf")
    best_score = float("inf")
    best_params = reference_params.copy()
    learning_rate = initial_learning_rate
    no_improvement_count = 0

    optimization_history = []

    print("Testing improved gradient descent optimization...")
    print(f"Initial parameters: {reference_params}")
    print()

    # Run optimization for 20 iterations
    for iteration in range(20):
        # Evaluate current parameters
        current_score = simulate_realistic_evaluation(current_params, iteration)

        # Track best result
        if current_score < best_score:
            best_score = current_score
            best_params = current_params.copy()
            no_improvement_count = 0
            print(f"Iteration {iteration}: New best score: {best_score:.3f}")
        else:
            no_improvement_count += 1

        # Learning rate decay
        if no_improvement_count >= patience:
            learning_rate = max(min_learning_rate, learning_rate * learning_rate_decay)
            no_improvement_count = 0
            print(f"Iteration {iteration}: Reducing learning rate to {learning_rate:.4f}")

        # Store history
        optimization_history.append(
            {
                "iteration": iteration,
                "params": current_params.copy(),
                "score": current_score,
                "best_score": best_score,
                "learning_rate": learning_rate,
            }
        )

        # Update parameters for next iteration
        if iteration > 0:
            # Calculate gradients
            gradients = calculate_gradient_direction(
                optimization_history[iteration - 1]["score"],
                current_score,
                optimization_history[iteration - 1]["params"],
                current_params,
            )

            # Update parameters
            current_params = update_parameters_with_gradient(
                current_params, gradients, learning_rate, gradient_step
            )

            # Apply constraints
            current_params = apply_constraints(current_params, param_bounds)
        else:
            # For first iteration, make small random adjustments
            for param in gradient_step.keys():
                adjustment = gradient_step[param] * 0.1
                current_params[param] += adjustment
            current_params = apply_constraints(current_params, param_bounds)

        previous_params = current_params.copy()
        previous_score = current_score

        print(f"Iteration {iteration}: Score = {current_score:.3f}, Best = {best_score:.3f}")

    # Final results
    print("\n" + "=" * 50)
    print("OPTIMIZATION RESULTS")
    print("=" * 50)
    print(f"Best score achieved: {best_score:.3f}")
    print(f"Best parameters: {best_params}")
    print(f"Final learning rate: {learning_rate:.4f}")

    # Show improvement
    initial_score = optimization_history[0]["score"]
    improvement = initial_score - best_score
    print(f"Total improvement: {improvement:.3f}")

    # Convergence analysis
    recent_scores = [h["score"] for h in optimization_history[-5:]]
    score_variance = sum(
        (s - sum(recent_scores) / len(recent_scores)) ** 2 for s in recent_scores
    ) / len(recent_scores)
    print(f"Recent score variance: {score_variance:.4f}")

    if score_variance < 0.1:
        print("Algorithm appears to have converged")
    else:
        print("Algorithm may need more iterations to converge")

    return best_params, best_score


if __name__ == "__main__":
    best_params, best_score = test_optimization()
