import time
from typing import Generator, List, Tuple

import numpy as np

from src.shared_models import AIRecommendation, SimulationMetrics, SimulationParameters

# This is a FAKE backend. It produces predictable, hardcoded data so the
# frontend team can build the UI without waiting for the real simulation.


def run_simulation_step_by_step(
    params: SimulationParameters,
) -> Generator[Tuple[np.ndarray, SimulationMetrics], None, None]:
    """
    A mock generator function that yields a new simulation state at each step.
    This simulates the animation data stream.
    """
    print("MOCK BACKEND: Running MOCK simulation...")
    # Create a simple 10x10 grid for the mock animation
    grid = np.zeros((20, 20))

    # Simulate a simple movement from left to right
    for i in range(10):
        grid.fill(0)  # Clear the grid
        grid[8:12, i * 2 : i * 2 + 2] = 1  # A block representing a crowd moving

        # Create some fake metrics that update with the simulation
        mock_metrics = SimulationMetrics(
            avg_wait_time_mins=30 - i * 2, peak_congestion_percent=0.9 - i * 0.05
        )

        yield grid, mock_metrics
        time.sleep(0.1)  # Simulate the time it takes to compute a step


def get_ai_recommendations(params: SimulationParameters) -> List[AIRecommendation]:
    """
    A mock function that returns a hardcoded list of AI recommendations.
    This simulates the call to Amazon Bedrock.
    """
    print(f"MOCK BACKEND: Getting MOCK AI recommendations for goal: {params.optimization_goal}")
    time.sleep(1.5)  # Simulate the delay of an API call

    if params.optimization_goal == "Maximum Safety":
        return [
            AIRecommendation(
                recommendation="Open Gates C and D immediately.",
                reason="Gate B congestion is at a critical level. Opening more gates will redirect crowd flow and reduce density.",
            ),
            AIRecommendation(
                recommendation="Deploy 20 additional staff to the main plaza.",
                reason="Increased staff presence is needed to guide attendees and manage potential incidents in high-traffic zones.",
            ),
        ]
    else:  # Balanced Safety & Cost
        return [
            AIRecommendation(
                recommendation="Create a temporary queuing snake with existing barriers at Gate B.",
                reason="This organizes the crowd flow without requiring additional staff, making it a cost-effective solution.",
            ),
            AIRecommendation(
                recommendation="Use pre-event announcements to encourage staggered arrival times.",
                reason="Informing attendees can naturally spread out the arrival curve, reducing peak congestion.",
            ),
        ]
