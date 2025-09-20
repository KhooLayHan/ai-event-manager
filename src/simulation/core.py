from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Generator, Iterable, List, Sequence, Set, Tuple

import numpy as np
import pandas as pd

from src.shared_models import SimulationMetrics, SimulationParameters
from src.simulation.models import Attendee

Coord = Tuple[int, int]  # (row, col)


def _load_map(csv_path: str) -> np.ndarray:
    """Load a CSV venue map and return a 2D numpy array of strings.

    Expected cell values:
    - 'W' walkable
    - 'X' obstacle/wall
    - 'E' entry
    - 'O' exit (think "Out")
    """

    df = pd.read_csv(csv_path, header=None, dtype=str)
    return df.fillna("X").values.astype(str)


def _find_cells(grid: np.ndarray, kinds: Sequence[str]) -> Set[Coord]:
    kinds_set = set(kinds)
    cells: Set[Coord] = set()
    for r in range(grid.shape[0]):
        for c in range(grid.shape[1]):
            if grid[r, c] in kinds_set:
                cells.add((r, c))
    return cells


def _bfs_distance_to_exits(grid: np.ndarray, exits: Set[Coord]) -> List[List[int]]:
    """Compute shortest 4-neighbor distance from each cell to nearest exit.
    Obstacles ('X') are not traversable. Returns -1 for unreachable.
    """

    rows, cols = grid.shape
    dist = [[-1 for _ in range(cols)] for _ in range(rows)]
    q: deque[Coord] = deque()

    for r, c in exits:
        dist[r][c] = 0
        q.append((r, c))

    def neighbors(r: int, c: int) -> Iterable[Coord]:
        for nr, nc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr, nc] != "X":
                yield nr, nc

    while q:
        r, c = q.popleft()
        for nr, nc in neighbors(r, c):
            if dist[nr][nc] == -1:
                dist[nr][nc] = dist[r][c] + 1
                q.append((nr, nc))
    return dist


@dataclass
class SimulationConfig:
    map_path: str
    n_attendees: int
    max_steps: int = 200


class Simulation:
    def __init__(self, config: SimulationConfig):
        self.config = config
        self.grid = _load_map(config.map_path)
        self.rows, self.cols = self.grid.shape
        self.entries = _find_cells(self.grid, ["E"])
        self.exits = _find_cells(self.grid, ["O"])  # 'O' for out/exit
        if not self.entries or not self.exits:
            raise ValueError("Map must contain at least one 'E' entry and one 'O' exit")

        # Build walkable set (including entries and exits)
        self.walkable: Set[Coord] = _find_cells(self.grid, ["W", "E", "O"])
        self.distance_map = _bfs_distance_to_exits(self.grid, self.exits)

        # Spawn attendees at entries (round-robin across entry cells)
        entry_list = list(self.entries)
        self.attendees: List[Attendee] = []
        for i in range(config.n_attendees):
            start = entry_list[i % len(entry_list)]
            self.attendees.append(Attendee(id=i, pos=start))

        self.time_step = 0
        self.completed_ids: Set[int] = set()

    def step(self) -> None:
        self.time_step += 1
        occupied = {a.pos for a in self.attendees if not a.reached}
        desired: List[Tuple[int, Coord, Coord]] = []  # (id, from, to)

        # Phase 1: each attendee decides desired next position
        for a in self.attendees:
            if a.reached:
                continue
            nxt = a.decide_next_step(self.distance_map, self.walkable, self.exits, occupied)
            desired.append((a.id, a.pos, nxt))

        # Phase 2: resolve simple conflicts (two attendees wanting same cell). Priority by lower id.
        claims: dict[Coord, int] = {}
        final_moves: dict[int, Coord] = {}
        for aid, frm, to in sorted(desired, key=lambda x: x[0]):
            if to not in claims and (to == frm or to not in occupied):
                claims[to] = aid
                final_moves[aid] = to
            else:
                final_moves[aid] = frm  # stay put

        # Phase 3: apply moves
        for a in self.attendees:
            if a.reached:
                continue
            a.apply_move(final_moves[a.id])
            if a.pos in self.exits:
                a.reached = True
                self.completed_ids.add(a.id)

    def stats(self) -> dict:
        completed = len(self.completed_ids)
        total = len(self.attendees)
        in_system = total - completed
        avg_steps = (
            sum(a.steps_taken for a in self.attendees) / total if total > 0 else 0.0
        )
        # Efficiency: completed / total
        efficiency = completed / total if total else 0.0
        # Peak congestion: 1 - completion_rate
        peak_congestion_percent = float(1.0 - efficiency)
        # Average wait time (mins): estimate as (max_steps - time_step) / 2
        avg_wait_time_mins = int(max(0, (self.config.max_steps - self.time_step) / 2))
        # Active attendees: those not yet completed
        active_attendees = in_system
        return {
            "time_step": self.time_step,
            "completed": completed,
            "total": total,
            "active_attendees": active_attendees,
            "efficiency": efficiency,
            "avg_steps": avg_steps,
            "avg_wait_time_mins": avg_wait_time_mins,
            "peak_congestion_percent": peak_congestion_percent,
        }

    def render_grid(self) -> np.ndarray:
        """Return an array visualization for plotting/streaming to UI.

        Codes:
        0 empty/walkable, 1 obstacle, 2 entry, 3 exit, 4 attendee
        """
        vis = np.zeros((self.rows, self.cols), dtype=int)
        vis[self.grid == "X"] = 1
        vis[self.grid == "E"] = 2
        vis[self.grid == "O"] = 3
        for a in self.attendees:
            if not a.reached:
                r, c = a.pos
                vis[r, c] = 4
        return vis


def run_simulation_step_by_step(
    params: SimulationParameters,
) -> Generator[Tuple[np.ndarray, SimulationMetrics], None, None]:
    """
    Real backend generator: runs the grid simulation step-by-step.
    It yields a visualization grid and rolling metrics each step.
    """

    # Map path from config/data directory; we assume working dir root.
    map_path = "data/venue_map.csv"
    n_attendees = max(1, int(params.attendees / 20))  # scale down for demo speed
    sim = Simulation(SimulationConfig(map_path=map_path, n_attendees=n_attendees, max_steps=200))

    for _ in range(sim.config.max_steps):
        sim.step()
        grid = sim.render_grid()
        s = sim.stats()
        # Pass all stats as a dict for now (or update SimulationMetrics to accept all fields)
        metrics = SimulationMetrics(
            avg_wait_time_mins=s["avg_wait_time_mins"],
            peak_congestion_percent=s["peak_congestion_percent"],
        )
        # Yield grid, metrics, and all stats for the frontend
        yield grid, metrics, s
        if s["completed"] == s["total"]:
            break

