# src/simulation/lifecycle_core.py
import numpy as np
import pandas as pd
import json
from typing import List, Tuple, Dict, Optional
from pathlib import Path

from .models import Attendee, VenueLocation
from .time_converter import TimeConverter

class FullEventLifecycleSimulation:
    """Complete event lifecycle simulator. THIS IS A PURE PYTHON BACKEND."""
    
    def __init__(self, map_data: np.ndarray, scenario_path: str, open_gates_override: int):
        self.map_data = map_data.copy()
        self.current_step = 0
        
        # Initialize metrics tracking properly
        self.attendees: List[Attendee] = []
        self.entry_times = {}  # Track when each attendee started waiting
        self.wait_times = []   # Track individual wait times
        self.peak_congestion = 0
        
        # Initialize wait time tracking per attendee
        self.attendees: List[Attendee] = []
        self.wait_times_distribution = []
        self.max_wait_time = 0
        
        # Initialize simulation components
        self.config = self._load_config(scenario_path)
        self.total_attendees = self.config["attendee_count"]
        self.open_gates = open_gates_override
        
        self.time_converter = TimeConverter(
            start_time_str=self.config["event_timeline"]["start_time"],
            scale_factor=self.config["simulation_time_scale_factor"]
        )
        self.timeline_steps = {
            "entry_rush_end": self.time_converter.to_step(self.config["event_timeline"]["entry_rush_end_time"]),
            "mid_event_end": self.time_converter.to_step(self.config["event_timeline"]["mid_event_end_time"]),
            "evacuation_start": self.time_converter.to_step(self.config["event_timeline"]["evacuation_start_time"])
        }
        
        self.locations = self._find_key_locations()
        self._create_attendees()
        
        # Add entry tracking
        self.successful_entries = 0  # Count of successful entries
        self.entry_progress = []     # Track entry rate progress

    def _load_config(self, scenario_path: str) -> Dict:
        config_path = Path(scenario_path) / "event_config.json"
        with open(config_path, 'r') as f:
            return json.load(f)

    def _find_key_locations(self) -> Dict[str, List[VenueLocation]]:
        """
        CRITICAL FIX: Find locations based on the map's numerical legend.
        Legend: 3=Entrance, 4=Exit, 2=Destination, 0=Open Space
        """
        return {
            'entrances': [VenueLocation(f"E{i}", x, y) for i, (x, y) in enumerate(np.argwhere(self.map_data == 3))],
            'exits': [VenueLocation(f"X{i}", x, y) for i, (x, y) in enumerate(np.argwhere(self.map_data == 4))],
            'destinations': [VenueLocation(f'D{i}', x, y) for i, (x, y) in enumerate(np.argwhere(self.map_data == 2))],
            'open_space': [VenueLocation(f'OS{i}', x, y) for i, (x, y) in enumerate(np.argwhere(self.map_data == 0))]
        }

    def _create_attendees(self):
        active_entrances = self.locations['entrances'][:self.open_gates]
        if not active_entrances: 
            return

        self.attendees = []  # Reset attendees list
        self.entry_times = {}  # Reset entry times
        
        for i in range(self.total_attendees):
            entrance = active_entrances[i % len(active_entrances)]
            # IMPROVEMENT: The goal is a random spot in the open area, not a single point.
            goal_location = self.locations['open_space'][np.random.randint(0, len(self.locations['open_space']))]
            
            attendee = Attendee(
                id=i, x=entrance.x, y=entrance.y,
                entry_time_step=self.current_step,
                goal=(goal_location.x, goal_location.y)
            )
            self.attendees.append(attendee)
            self.entry_times[i] = self.current_step  # Track entry time for wait time calculation

    def run_lifecycle_step(self):
        self.current_step += 1
        current_phase = self._get_current_phase()
        self._update_goals_for_phase(current_phase)
        self._move_attendees_smart()
        
        # Return required values for compatibility
        vis_grid = self.get_visualization_grid()
        metrics = self.get_current_metrics()
        real_time = self.time_converter.to_real_time(self.current_step)
        return vis_grid, metrics, current_phase, real_time

    def _get_current_phase(self) -> str:
        if self.current_step <= self.timeline_steps["entry_rush_end"]: return "entry_rush"
        if self.current_step <= self.timeline_steps["mid_event_end"]: return "mid_event"
        return "evacuation"

    def _update_goals_for_phase(self, phase: str):
        if phase == "evacuation" and self.attendees[0].status != "evacuating":
            for attendee in self.attendees:
                attendee.status = "evacuating"
                nearest_exit = min(self.locations['exits'], key=lambda e: abs(e.x - attendee.x) + abs(e.y - attendee.y))
                attendee.goal = (nearest_exit.x, nearest_exit.y)
                attendee.goal_reached_step = None
        elif phase == "mid_event":
            # Check if this is the first step of mid-event phase
            if self.attendees[0].status != "mingling" and self.attendees[0].status != "leaving_early":
                # ALL attendees now target destinations during mid-event
                for attendee in self.attendees:
                    # Small chance to leave early (before targeting destinations)
                    if np.random.random() < 0.02:  # 2% chance to leave early
                        nearest_exit = min(self.locations['exits'], key=lambda e: abs(e.x - attendee.x) + abs(e.y - attendee.y))
                        attendee.goal = (nearest_exit.x, nearest_exit.y)
                        attendee.status = "leaving_early"
                        attendee.goal_reached_step = None
                    else:
                        # ALL attendees target destinations (food stalls, etc.)
                        destination = self.locations['destinations'][attendee.id % len(self.locations['destinations'])]
                        attendee.goal = (destination.x, destination.y)
                        attendee.status = "mingling"
                        attendee.goal_reached_step = None

    def _move_attendees_smart(self):
        initial_occupied = {(a.x, a.y) for a in self.attendees}
        next_occupied = {(a.x, a.y) for a in self.attendees if a.goal is None or (a.x, a.y) == a.goal}
        
        agents_to_move = list(self.attendees)
        np.random.shuffle(agents_to_move)

        for attendee in agents_to_move:
            if attendee.goal is None or (attendee.x, attendee.y) == attendee.goal:
                continue

            # Check if attendee can't move due to density or no free space
            density = self._calculate_local_density(attendee.x, attendee.y, initial_occupied)
            best_move = self._find_best_neighbor(attendee, next_occupied)
            
            # Increment wait time if attendee can't move
            if (density > 0.6 and np.random.rand() < density) or not best_move:
                attendee.total_wait_time_steps += 1
                self.max_wait_time = max(self.max_wait_time, attendee.total_wait_time_steps)
                next_occupied.add((attendee.x, attendee.y))
                continue

            # Track when attendee moves from entrance to open space
            if self.map_data[attendee.x, attendee.y] == 3 and self.map_data[best_move[0], best_move[1]] == 0:
                self.successful_entries += 1
                # Add current progress to history
                current_rate = (self.successful_entries / self.total_attendees) * 100
                self.entry_progress.append(current_rate)
            
            attendee.x, attendee.y = best_move
            next_occupied.add(best_move)
            
            # Check if attendee reached goal or gate
            if (attendee.x, attendee.y) == attendee.goal and attendee.goal_reached_step is None:
                attendee.goal_reached_step = self.current_step
                attendee.status = "reached_goal"
            
            # Remove attendees who reach exit gates (evacuation OR early leavers)
            if ((attendee.status == "evacuating" or attendee.status == "leaving_early") and 
                self.map_data[attendee.x, attendee.y] == 4):
                attendee.status = "exited"
        else:
            next_occupied.add((attendee.x, attendee.y))

    def _calculate_local_density(self, x: int, y: int, occupied: set, radius: int = 2) -> float:
        count = total = 0
        for i in range(max(0, x-radius), min(self.map_data.shape[0], x+radius+1)):
            for j in range(max(0, y-radius), min(self.map_data.shape[1], y+radius+1)):
                if self.map_data[i, j] != 1:
                    total += 1
                    if (i, j) in occupied: count += 1
        return count / total if total > 0 else 0

    def _find_best_neighbor(self, attendee: Attendee, occupied: set) -> Optional[Tuple[int, int]]:
        neighbors = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0: continue
                # NOTE: Consistent (row, col) = (x, y) convention
                new_x, new_y = attendee.x + dx, attendee.y + dy
                if (0 <= new_x < self.map_data.shape[0] and 0 <= new_y < self.map_data.shape[1] and self.map_data[new_x, new_y] != 1):
                    neighbors.append((new_x, new_y))
        
        unoccupied_neighbors = [pos for pos in neighbors if pos not in occupied]
        if not unoccupied_neighbors: return None
        
        distances = [np.sqrt((nx - attendee.goal[0])**2 + (ny - attendee.goal[1])**2) for nx, ny in unoccupied_neighbors]
        return unoccupied_neighbors[np.argmin(distances)]

    def get_visualization_grid(self) -> np.ndarray:
        # Create base grid with fixed elements - NO OVERLAYS!
        vis_grid = self.map_data.copy().astype(float)
        
        # Add attendees ONLY in open spaces (value 0)
        attendee_density = np.zeros_like(vis_grid)
        for attendee in self.attendees:
            if (0 <= attendee.x < vis_grid.shape[0] and 
                0 <= attendee.y < vis_grid.shape[1] and
                self.map_data[attendee.x, attendee.y] == 0):  # Only in open space
                attendee_density[attendee.x, attendee.y] += 1
        
        # Apply attendee density only to open spaces
        for i in range(vis_grid.shape[0]):
            for j in range(vis_grid.shape[1]):
                if vis_grid[i, j] == 0 and attendee_density[i, j] > 0:
                    vis_grid[i, j] = 5 + min(attendee_density[i, j] - 1, 4)  # 5-9 range
        
        return vis_grid

    def calculate_wait_time(self):
        """Calculate real wait time in minutes based on queued attendees"""
        current_waiting = len(self.entry_times)
        if current_waiting == 0:
            return 0
            
        # Calculate average wait time for current attendees
        current_time = self.current_step
        wait_times = [current_time - start_time 
                     for start_time in self.entry_times.values()]
        
        # Convert steps to minutes using simulation time scale
        avg_wait_steps = np.mean(wait_times) if wait_times else 0
        return int(avg_wait_steps / self.config["simulation_time_scale_factor"])
    
    def get_current_metrics(self) -> dict:
        # Calculate wait times in minutes
        wait_times = [a.total_wait_time_steps for a in self.attendees]
        avg_wait_time = np.mean(wait_times) if wait_times else 0
        max_wait_time = self.max_wait_time
        
        # Create wait time distribution
        if wait_times:
            bins = [0, 5, 10, 15, float('inf')]
            hist, _ = np.histogram(wait_times, bins=bins)
            distribution = {f"{bins[i]}-{bins[i+1]}min": int(count) 
                          for i, count in enumerate(hist[:-1])}
        else:
            distribution = {}

        # Method 1: Average density across occupied cells (FIXED)
        vis_grid = self.get_visualization_grid()
        attendee_cells = vis_grid[vis_grid >= 5]  # Cells with attendees (5+ in vis_grid)
        if len(attendee_cells) > 0:
            # vis_grid values: 5=1 person, 6=2 people, 7=3 people, 8=4 people, 9=5+ people
            actual_densities = attendee_cells - 4  # Convert to actual attendee count
            avg_density = np.mean(actual_densities)  # Average attendees per occupied cell
            congestion_percent = min(avg_density / 3.0, 1.0) * 100  # 3 people per cell = 100%
        else:
            congestion_percent = 0
        
        # Calculate entry efficiency
        attendees_in_venue = [a for a in self.attendees if 
                             self.map_data[a.x, a.y] == 0 and a.status in ["reached_goal", "mingling"]]
        entry_success_rate = (len(attendees_in_venue) / len(self.attendees)) * 100 if self.attendees else 0
        
        # Calculate progressive entry rate
        if self.entry_progress:
            # Use the latest progress value
            entry_success_rate = self.entry_progress[-1]
        else:
            entry_success_rate = 0
        
        # Debug info
        total_occupied_cells = len(attendee_cells)
        total_attendees_visible = len([a for a in self.attendees if self.map_data[a.x, a.y] == 0])
        
        return {
            "peak_congestion_percent": congestion_percent,
            "real_wait_time_mins": int(avg_wait_time / self.config["simulation_time_scale_factor"]),
            "max_wait_time_mins": int(max_wait_time / self.config["simulation_time_scale_factor"]),
            "wait_time_distribution": distribution,
            "entry_success_rate": entry_success_rate,
            "debug_occupied_cells": total_occupied_cells,
            "debug_visible_attendees": total_attendees_visible
        }
    
    def get_final_summary(self) -> dict:
        """Calculates REAL metrics after the simulation is complete."""
        entry_times = [
            a.goal_reached_step - a.entry_time_step 
            for a in self.attendees 
            if a.goal_reached_step is not None and a.status == "reached_goal"
        ]
        avg_entry_time_steps = np.mean(entry_times) if entry_times else 0
        avg_entry_time_mins = avg_entry_time_steps / self.config["simulation_time_scale_factor"]
        
        return {"avg_entry_time_mins": round(avg_entry_time_mins, 2)}