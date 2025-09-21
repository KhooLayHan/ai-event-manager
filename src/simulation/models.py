from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

Coord = Tuple[int, int]  # (row, col)


@dataclass
class Attendee:
    """
    Represents an individual attendee in the crowd.

    Attributes:
        id: Unique identifier for the attendee.
        pos: Current grid position (row, col).
        destination: Optional destination cell (for future use). For now, any 'exit' cell qualifies.
        reached: Whether the attendee has reached an exit.
        steps_taken: Number of simulation steps moved.
    """

    id: int
    pos: Coord
    destination: Optional[Coord] = None
    reached: bool = False
    steps_taken: int = 0

    def decide_next_step(
        self,
        distance_map: list[list[int]],
        walkable: set[Coord],
        exits: set[Coord],
        occupied: set[Coord],
    ) -> Coord:
        """
        Choose the neighboring cell that greedily reduces the distance to the nearest exit.

    - Attendees can move in 4 directions (up, down, left, right).
    - They cannot enter non-walkable cells or cells currently occupied by others.
        - If multiple neighbors have the same best distance, the first found is chosen.
    - If already at an exit, the attendee stays.

        Returns the desired next position (may be the current position to stay).
        """

        if self.pos in exits:
            self.reached = True
            return self.pos

        r, c = self.pos
        neighbors: list[Coord] = [(r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)]

        best_pos = self.pos
        best_dist = distance_map[r][c]

        for nr, nc in neighbors:
            if (nr, nc) in walkable and (nr, nc) not in occupied:
                nd = distance_map[nr][nc]
                if nd >= 0 and (best_dist < 0 or nd < best_dist):
                    best_dist = nd
                    best_pos = (nr, nc)

        return best_pos

    def apply_move(self, new_pos: Coord) -> None:
        if new_pos != self.pos:
            self.steps_taken += 1
        self.pos = new_pos
