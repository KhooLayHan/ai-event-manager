from dataclasses import dataclass


@dataclass
class SimulationParameters:
    """Input from the UI to the backend."""

    attendees: int
    open_gates: int
    optimization_goal: str  # e.g., "Maximum Safety"


@dataclass
class SimulationMetrics:
    """Final summary metrics from the simulation."""

    avg_wait_time_mins: int
    peak_congestion_percent: float


@dataclass
class AIRecommendation:
    """A single structured recommendation from the AI."""

    recommendation: str
    reason: str
