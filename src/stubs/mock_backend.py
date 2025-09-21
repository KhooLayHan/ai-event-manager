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
    """Mock implementation of AI recommendations for development and testing.

    This function returns different recommendations based on the optimization goal.

    Args:
        params (SimulationParameters): The simulation parameters including attendees, open gates, and optimization goal.

    Returns:
        List[AIRecommendation]: A list of mock AI recommendations.
    """
    print(f"MOCK BACKEND: Getting MOCK AI recommendations for goal: {params.optimization_goal}")
    time.sleep(1.5)  # Simulate the delay of an API call

    attendee_count = params.attendees
    # open_gates = params.open_gates
    optimization_goal = params.optimization_goal

    # Base recommendations for all scenarios
    if attendee_count <= 1_000:
        crowd_size = "small"
    elif attendee_count <= 5_000:
        crowd_size = "medium"
    else:
        crowd_size = "large"

    # Different recommendations based on optimization goal

    if optimization_goal == "Maximum Safety":
        # Safety-focused recommendations
        if crowd_size == "small":
            return [
                # AIRecommendation(
                #     recommendation="Ensure all gates are staffed.",
                #     reason="Even with a small crowd, having staff at all gates ensures quick response to any issues.",
                # ),
                # AIRecommendation(
                #     recommendation="Set up clear signage for emergency exits.",
                #     reason="Clear signage helps in case of emergencies, ensuring safety for all attendees.",
                # ),
                AIRecommendation(
                    recommendation="Open all available gates for entry",
                    reason="Even with a small crowd, distributing attendees across all gates minimizes congestion and wait times, ensuring the safest possible entry experience.",
                ),
                AIRecommendation(
                    recommendation="Deploy security personnel at each gate and high-traffic areas",
                    reason="Having security personnel visible at all entry points enhances safety monitoring and rapid response capabilities in case of incidents.",
                ),
            ]
        elif crowd_size == "medium":
            return [
                # AIRecommendation(
                #     recommendation="Open Gates C and D immediately.",
                #     reason="Gate B congestion is at a critical level. Opening more gates will redirect crowd flow and reduce density.",
                # ),
                # AIRecommendation(
                #     recommendation="Deploy 20 additional staff to the main plaza.",
                #     reason="Increased staff presence is needed to guide attendees and manage potential incidents in high-traffic zones.",
                # ),
                AIRecommendation(
                    recommendation="Deploy medical response teams at strategic locations",
                    reason="With a medium-sized crowd, having medical personnel stationed throughout the venue ensures rapid response to health emergencies.",
                ),
                AIRecommendation(
                    recommendation="Implement real-time crowd density monitoring system",
                    reason="A comprehensive monitoring system allows staff to identify potential congestion points before they become hazardous.",
                ),
            ]
        else:  # large crowd
            return [
                # AIRecommendation(
                #     recommendation="Establish multiple first aid stations throughout the venue",
                #     reason="In a large crowd, having several first aid stations ensures that medical assistance is readily available, reducing response times during emergencies.",
                # ),
                # AIRecommendation(
                #     recommendation="Increase the number of security personnel and deploy them in high-density areas",
                #     reason="A larger security presence helps manage crowd behavior, deter potential incidents, and provide assistance where needed.",
                # ),
                AIRecommendation(
                    recommendation="Install emergency communication system with multiple redundancies",
                    reason="For large crowds, a robust emergency communication system is essential to coordinate evacuations and manage incidents safely.",
                ),
                AIRecommendation(
                    recommendation="Establish multiple triage and first aid stations throughout the venue",
                    reason="With many attendees, multiple medical response locations ensure adequate coverage and minimize response times to emergencies.",
                ),
            ]
    else:  # Balanced Safety & Cost
        # Cost-conscious recommendations
        if crowd_size == "small":
            return [
                # AIRecommendation(
                #     recommendation="Open all available gates for entry",
                #     reason="Even with a small crowd, distributing attendees across all gates minimizes congestion and wait times, ensuring an efficient entry experience.",
                # ),
                # AIRecommendation(
                #     recommendation="Deploy staff at key gates rather than all gates",
                #     reason="Staffing key entry points optimizes resource allocation while still providing necessary guidance and oversight.",
                # ),
                AIRecommendation(
                    recommendation="Open gates strategically based on expected arrival patterns",
                    reason="For a small crowd, opening select gates based on arrival patterns maintains safety while optimizing staff resource allocation.",
                ),
                AIRecommendation(
                    recommendation="Use existing staff with enhanced communication tools",
                    reason="Rather than hiring additional security, equipping current staff with radios or communication apps improves coordination without additional personnel costs.",
                ),
            ]
        elif crowd_size == "medium":
            return [
                # AIRecommendation(
                #     recommendation="Create a temporary queuing snake with existing barriers at Gate B.",
                #     reason="This organizes the crowd flow without requiring additional staff, making it a cost-effective solution.",
                # ),
                # AIRecommendation(
                #     recommendation="Use pre-event announcements to encourage staggered arrival times.",
                #     reason="Informing attendees can naturally spread out the arrival curve, reducing peak congestion.",
                # ),
                AIRecommendation(
                    recommendation="Stagger entry times using existing ticketing system",
                    reason="Implementing phased entry times distributes arrivals more evenly, reducing congestion without requiring additional infrastructure.",
                ),
                AIRecommendation(
                    recommendation="Repurpose underutilized spaces for queueing",
                    reason="Using available spaces more effectively creates natural crowd flow patterns without expensive infrastructure modifications.",
                ),
            ]
        else:  # large crowd
            return [
                # AIRecommendation(
                #     recommendation="Utilize technology for crowd management",
                #     reason="Implementing mobile apps or SMS alerts to inform attendees of optimal arrival times and gate usage can reduce congestion without significant infrastructure costs.",
                # ),
                # AIRecommendation(
                #     recommendation="Leverage volunteer staff for crowd guidance",
                #     reason="Recruiting volunteers from local communities or organizations provides additional manpower for crowd management at minimal cost.",
                # ),
                AIRecommendation(
                    recommendation="Implement a mobile app-based crowd notification system",
                    reason="A mobile app leverages attendees' own devices for communications, avoiding costly installation of physical announcement systems.",
                ),
                AIRecommendation(
                    recommendation="Train volunteer teams for basic crowd management assistance",
                    reason="Volunteer teams can supplement paid staff at a fraction of the cost while still maintaining appropriate safety levels for the event.",
                ),
            ]
