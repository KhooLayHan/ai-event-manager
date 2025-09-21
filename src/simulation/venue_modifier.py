import numpy as np
import pandas as pd
from pathlib import Path

def add_gates_to_venue(original_map: np.ndarray, target_entrance_gates: int, target_exit_gates: int) -> np.ndarray:
    """
    Dynamically add gates to venue map for optimized simulation.
    Only adds gates at perimeter edges (not middle space).
    
    Args:
        original_map: Original venue map array
        target_entrance_gates: Total entrance gates desired
        target_exit_gates: Total exit gates desired
        
    Returns:
        Modified venue map with additional gates
    """
    modified_map = original_map.copy()
    height, width = modified_map.shape
    
    # Count existing gates
    existing_entrance_gates = np.sum(original_map == 3)
    existing_exit_gates = np.sum(original_map == 4)
    
    entrance_gates_to_add = max(0, target_entrance_gates - existing_entrance_gates)
    exit_gates_to_add = max(0, target_exit_gates - existing_exit_gates)
    
    # Find ONLY perimeter edge locations for gates
    perimeter_locations = []
    
    # Top and bottom edges
    for j in range(1, width-1):  # Skip corners
        if modified_map[0, j] == 0:  # Top edge open space
            perimeter_locations.append((0, j, 'entrance'))
        if modified_map[height-1, j] == 0:  # Bottom edge open space  
            perimeter_locations.append((height-1, j, 'exit'))
    
    # Left and right edges
    for i in range(1, height-1):  # Skip corners
        if modified_map[i, 0] == 0:  # Left edge open space
            perimeter_locations.append((i, 0, 'entrance'))
        if modified_map[i, width-1] == 0:  # Right edge open space
            perimeter_locations.append((i, width-1, 'exit'))
    
    # Add entrance gates at suitable perimeter locations
    entrance_added = 0
    for i, j, gate_type in perimeter_locations:
        if gate_type == 'entrance' and entrance_added < entrance_gates_to_add:
            modified_map[i, j] = 3  # Entrance gate
            entrance_added += 1
    
    # Add exit gates at suitable perimeter locations
    exit_added = 0
    for i, j, gate_type in perimeter_locations:
        if gate_type == 'exit' and exit_added < exit_gates_to_add:
            modified_map[i, j] = 4  # Exit gate
            exit_added += 1
    
    return modified_map

def create_optimized_venue_map(scenario_path: str, target_entrance_gates: int, target_exit_gates: int) -> np.ndarray:
    """
    Load venue map and add gates as needed for optimization.
    
    Args:
        scenario_path: Path to scenario folder
        target_entrance_gates: Target number of entrance gates
        target_exit_gates: Target number of exit gates
        
    Returns:
        Optimized venue map array
    """
    map_path = Path(scenario_path) / "venue_map.csv"
    original_map = pd.read_csv(map_path, header=None).values
    
    return add_gates_to_venue(original_map, target_entrance_gates, target_exit_gates)

def adjust_venue_gates(venue_map: np.ndarray, target_entrance: int, target_exit: int) -> np.ndarray:
    """Dynamically adjust venue map gates based on user selection"""
    modified_map = venue_map.copy()
    
    # Count current gates
    current_entrance = np.sum(modified_map == 3)
    current_exit = np.sum(modified_map == 4)
    
    # Adjust entrance gates
    if current_entrance > target_entrance:
        # Remove excess entrance gates
        entrance_positions = np.where(modified_map == 3)
        gates_to_remove = int(current_entrance - target_entrance)
        for i in range(gates_to_remove):
            if i < len(entrance_positions[0]):
                modified_map[entrance_positions[0][i], entrance_positions[1][i]] = 1  # Convert to wall
    elif current_entrance < target_entrance:
        # Add new entrance gates
        gates_to_add = int(target_entrance - current_entrance)
        wall_positions = find_suitable_gate_positions(modified_map)
        for i in range(gates_to_add):
            if i < len(wall_positions):
                modified_map[wall_positions[i][0], wall_positions[i][1]] = 3  # Convert to entrance
    
    # Adjust exit gates similarly
    if current_exit > target_exit:
        exit_positions = np.where(modified_map == 4)
        gates_to_remove = int(current_exit - target_exit)
        for i in range(gates_to_remove):
            if i < len(exit_positions[0]):
                modified_map[exit_positions[0][i], exit_positions[1][i]] = 1
    elif current_exit < target_exit:
        gates_to_add = int(target_exit - current_exit)
        wall_positions = find_suitable_gate_positions(modified_map)
        for i in range(gates_to_add):
            if i < len(wall_positions):
                modified_map[wall_positions[i][0], wall_positions[i][1]] = 4

    return modified_map

def find_suitable_gate_positions(venue_map: np.ndarray) -> list:
    """Find suitable wall positions that can be converted to gates"""
    height, width = venue_map.shape
    suitable_positions = []
    
    # Check perimeter walls first
    for i in range(height):
        for j in range(width):
            if venue_map[i,j] == 1:  # If wall
                # Check if adjacent to open space
                if (i == 0 or i == height-1 or j == 0 or j == width-1):  # Perimeter wall
                    if has_adjacent_space(venue_map, i, j):
                        suitable_positions.append((i,j))
    
    return suitable_positions

def has_adjacent_space(venue_map: np.ndarray, i: int, j: int) -> bool:
    """Check if position has adjacent open space"""
    height, width = venue_map.shape
    for di, dj in [(-1,0), (1,0), (0,-1), (0,1)]:
        ni, nj = i + di, j + dj
        if 0 <= ni < height and 0 <= nj < width:
            if venue_map[ni,nj] == 0:  # Open space
                return True
    return False