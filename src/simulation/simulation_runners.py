# src/simulation/simulation_runners.py
import streamlit as st
import pandas as pd
import time
import json
import numpy as np
from pathlib import Path
from typing import Generator, Tuple, Dict

from .lifecycle_core import FullEventLifecycleSimulation

def _create_simulation_instance(open_gates_override: int) -> FullEventLifecycleSimulation:
    """Helper function to create a simulation instance based on UI controls."""
    scenario_path = st.session_state.get('selected_scenario_path', 'data/concert_venue')
    map_path = Path(scenario_path) / "venue_map.csv"
    venue_map = pd.read_csv(map_path, header=None).values
    
    return FullEventLifecycleSimulation(venue_map, scenario_path, open_gates_override)

def run_animated_simulation(attendees: int, open_gates: int) -> Generator[Tuple[np.ndarray, dict, str, str], None, None]:
    """
    Main generator for running the animated simulation for the UI.
    """
    simulation = _create_simulation_instance(open_gates)
    
    last_event_step = max(simulation.timeline_steps.values())
    buffer_steps = simulation.config.get("simulation_buffer_steps", 200)
    total_steps = last_event_step + buffer_steps
    
    for step in range(total_steps):
        simulation.run_lifecycle_step()
        
        vis_grid = simulation.get_visualization_grid()
        metrics = simulation.get_current_metrics() # Get live metrics
        phase = simulation._get_current_phase()
        real_time = simulation.time_converter.to_real_time(simulation.current_step)
        
        yield vis_grid, metrics, phase, real_time
        time.sleep(0.01) # Animation delay

def run_fast_simulation(attendees: int, open_gates: int, max_steps: int) -> Dict:
    """Fast simulation - runs at maximum speed and returns final results only"""
    simulation = _create_simulation_instance(open_gates)
    
    # Run at maximum speed - no delays, no yielding
    for step in range(max_steps):
        simulation.run_lifecycle_step()
    
    # Return final results
    return {
        'final_grid': simulation.get_visualization_grid(),
        'final_metrics': simulation.get_current_metrics(),
        'final_phase': simulation._get_current_phase(),
        'final_time': simulation.time_converter.to_real_time(simulation.current_step),
        'lifecycle_summary': simulation.get_current_metrics(),
        'total_steps': step + 1
    }