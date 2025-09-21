# src/simulation/models.py
from dataclasses import dataclass
from typing import Optional, Tuple

@dataclass
class VenueLocation:
    name: str
    x: int
    y: int

@dataclass
class Attendee:
    """Represents a single person in our simulation."""
    id: int
    x: int
    y: int
    entry_time_step: int
    goal: Optional[Tuple[int, int]] = None
    status: str = "moving_to_goal"  # States: moving_to_goal, reached_goal, mingling, evacuating
    goal_reached_step: Optional[int] = None