import numpy as np
import pandas as pd
from pathlib import Path
from typing import Tuple, Dict

def create_enhanced_venue_map(base_map_path: str, ai_recommendations: Dict) -> np.ndarray:
    """
    Create enhanced venue map with AI-recommended optimizations
    
    Map Legend:
    0 = Open space
    1 = Wall/obstacle  
    2 = Destination (food, facilities)
    3 = Active entry gate
    4 = Exit gate
    6 = Potential entry gate (can be activated)
    7 = Potential staff position
    """
    
    # Load base venue map
    base_map = pd.read_csv(base_map_path, header=None).values
    enhanced_map = base_map.copy()
    
    # Add potential gate positions if not already present
    enhanced_map = add_potential_gates(enhanced_map)
    
    # Activate recommended number of gates
    recommended_gates = ai_recommendations['optimized_parameters']['recommended_open_gates']
    enhanced_map = activate_optimal_gates(enhanced_map, recommended_gates)
    
    # Add staff positions
    recommended_staff = ai_recommendations['optimized_parameters']['recommended_staff']
    enhanced_map = add_staff_positions(enhanced_map, recommended_staff)
    
    return enhanced_map

def add_potential_gates(venue_map: np.ndarray) -> np.ndarray:
    """Add potential gate positions to venue map"""
    
    enhanced_map = venue_map.copy()
    rows, cols = enhanced_map.shape
    
    # Add potential gates on sides (value 6)
    # Left side potential gates
    if enhanced_map[rows//2, 0] == 0:  # If space is open
        enhanced_map[rows//2, 0] = 6
    if enhanced_map[rows//2 + 2, 0] == 0:
        enhanced_map[rows//2 + 2, 0] = 6
        
    # Right side potential gates  
    if enhanced_map[rows//2, cols-1] == 0:
        enhanced_map[rows//2, cols-1] = 6
    if enhanced_map[rows//2 + 2, cols-1] == 0:
        enhanced_map[rows//2 + 2, cols-1] = 6
    
    # Top potential gates
    if enhanced_map[0, cols//2 - 2] == 0:
        enhanced_map[0, cols//2 - 2] = 6
    if enhanced_map[0, cols//2 + 2] == 0:
        enhanced_map[0, cols//2 + 2] = 6
        
    return enhanced_map

def activate_optimal_gates(venue_map: np.ndarray, target_gates: int) -> np.ndarray:
    """Activate optimal number of gates based on AI recommendation"""
    
    enhanced_map = venue_map.copy()
    
    # Count current active gates
    current_gates = np.sum(enhanced_map == 3)
    
    # Find potential gate positions
    potential_positions = np.where(enhanced_map == 6)
    
    if target_gates > current_gates:
        # Need to activate more gates
        gates_to_activate = min(target_gates - current_gates, len(potential_positions[0]))
        
        # Activate gates with best crowd distribution
        for i in range(gates_to_activate):
            row, col = potential_positions[0][i], potential_positions[1][i]
            enhanced_map[row, col] = 3  # Convert to active gate
            
    elif target_gates < current_gates:
        # Need to deactivate some gates (convert to potential)
        active_positions = np.where(enhanced_map == 3)
        gates_to_deactivate = current_gates - target_gates
        
        # Deactivate least optimal gates
        for i in range(min(gates_to_deactivate, len(active_positions[0]))):
            row, col = active_positions[0][i], active_positions[1][i]
            enhanced_map[row, col] = 6  # Convert to potential gate
    
    return enhanced_map

def add_staff_positions(venue_map: np.ndarray, target_staff: int) -> np.ndarray:
    """Add optimal staff positions based on AI recommendations"""
    
    enhanced_map = venue_map.copy()
    rows, cols = enhanced_map.shape
    
    # Strategic staff positions
    staff_positions = [
        # Near entry gates
        (rows//2 - 1, 1), (rows//2 + 1, 1),
        (rows//2 - 1, cols-2), (rows//2 + 1, cols-2),
        
        # Central areas (high traffic)
        (rows//2, cols//2), (rows//2 - 2, cols//2), (rows//2 + 2, cols//2),
        
        # Near destinations
        (rows//4, cols//4), (rows//4, 3*cols//4),
        (3*rows//4, cols//4), (3*rows//4, 3*cols//4),
        
        # Near exits
        (2, cols//2 - 2), (2, cols//2 + 2),
        (rows-3, cols//2 - 2), (rows-3, cols//2 + 2)
    ]
    
    # Place staff in valid positions
    staff_placed = 0
    for row, col in staff_positions:
        if (staff_placed < target_staff and 
            0 <= row < rows and 0 <= col < cols and 
            enhanced_map[row, col] == 0):  # Only in open spaces
            
            enhanced_map[row, col] = 7  # Staff position
            staff_placed += 1
    
    return enhanced_map

def save_optimized_venue_map(enhanced_map: np.ndarray, scenario_path: str) -> str:
    """Save the optimized venue map"""
    
    output_path = Path(scenario_path) / "venue_map_optimized.csv"
    pd.DataFrame(enhanced_map).to_csv(output_path, header=False, index=False)
    
    return str(output_path)

def get_optimization_summary(original_map: np.ndarray, optimized_map: np.ndarray) -> Dict:
    """Generate summary of optimizations made"""
    
    original_gates = np.sum(original_map == 3)
    optimized_gates = np.sum(optimized_map == 3)
    staff_positions = np.sum(optimized_map == 7)
    
    return {
        "original_gates": int(original_gates),
        "optimized_gates": int(optimized_gates),
        "staff_positions": int(staff_positions),
        "gates_added": int(optimized_gates - original_gates),
        "total_optimizations": int(optimized_gates - original_gates + staff_positions)
    }