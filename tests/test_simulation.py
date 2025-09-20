from __future__ import annotations

import numpy as np

from src.shared_models import SimulationParameters
from src.simulation.core import Simulation, SimulationConfig, run_simulation_step_by_step


def test_basic_simulation_runs():
    cfg = SimulationConfig(map_path="data/venue_map.csv", n_attendees=50, max_steps=200)
    sim = Simulation(cfg)

    assert len(sim.entries) >= 1 and len(sim.exits) >= 1
    assert sim.grid.shape == (15, 20)

    # Run for a few steps
    for _ in range(30):
        sim.step()

    s = sim.stats()
    assert s["total"] == 50
    # Should have moved at least some steps and some may have completed
    assert any(a.steps_taken > 0 for a in sim.attendees)


def test_generator_interface():
    params = SimulationParameters(attendees=1000, open_gates=2, optimization_goal="Maximum Safety")
    gen = run_simulation_step_by_step(params)
    grid, metrics = next(gen)
    assert isinstance(grid, np.ndarray)
    assert grid.ndim == 2
    assert hasattr(metrics, "avg_wait_time_mins")
    # consume a few more frames
    for _ in range(5):
        grid, metrics = next(gen)
