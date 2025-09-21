#!/usr/bin/env python3
"""Demonstrate how wait time is actually calculated"""

from src.simulation.lifecycle_core import FullEventLifecycleSimulation
import numpy as np

def demonstrate_wait_time_calculation():
    """Show exactly when and how wait time accumulates"""
    print("🔍 DEMONSTRATING WAIT TIME CALCULATION")
    print("=" * 50)
    
    # Load test data
    venue_map = np.loadtxt('data/concert_venue/venue_map.csv', delimiter=',')
    sim = FullEventLifecycleSimulation(venue_map, 'data/concert_venue', 2)
    
    print("📊 Wait time is accumulated when attendees:")
    print("   1. ❌ Cannot move due to HIGH DENSITY (density > 0.6)")
    print("   2. ❌ Cannot find any free neighboring space")
    print("   3. ⏰ This happens ANYWHERE in the venue, not just entrance→open space")
    print()
    
    # Track specific attendees
    tracked_attendees = sim.attendees[:5]  # Track first 5 attendees
    
    print("🎯 Tracking 5 specific attendees through simulation...")
    print("Step | ID | Position  | Map Type | Wait Steps | Wait Mins | Status")
    print("-" * 75)
    
    for step in range(15):
        sim.run_lifecycle_step()
        
        if step % 3 == 0:  # Every 3 steps
            for attendee in tracked_attendees:
                map_type_names = {0: "Open", 1: "Wall", 2: "Dest", 3: "Entrance", 4: "Exit"}
                map_type = sim.map_data[attendee.x, attendee.y]
                map_name = map_type_names.get(map_type, "Unknown")
                wait_mins = attendee.total_wait_time_steps / sim.config["simulation_time_scale_factor"]
                
                print(f"{step+1:4d} | {attendee.id:2d} | ({attendee.x:2d},{attendee.y:2d}) | {map_name:8s} | {attendee.total_wait_time_steps:10d} | {wait_mins:8.1f} | {attendee.status}")
    
    # Final metrics
    final_metrics = sim.get_current_metrics()
    
    print(f"\n📈 FINAL WAIT TIME CALCULATION:")
    print(f"   • Average Wait Time: {final_metrics['real_wait_time_mins']:.1f} minutes")
    print(f"   • Maximum Wait Time: {final_metrics['max_wait_time_mins']:.1f} minutes")
    print(f"   • Distribution: {final_metrics['wait_time_distribution']}")
    
    print(f"\n🎯 KEY POINTS ABOUT WAIT TIME:")
    print(f"   ✅ Wait time = TOTAL time attendee couldn't move (anywhere in venue)")
    print(f"   ✅ Accumulates at entrance gates, in corridors, at destinations, etc.")
    print(f"   ✅ Based on congestion density and available neighboring spaces")
    print(f"   ✅ NOT just entrance→open space transition time")
    
    print(f"\n📊 ENTRY RATE vs WAIT TIME:")
    print(f"   • Entry Rate = % who moved from entrance (3) to any other space")
    print(f"   • Wait Time = Average time ALL attendees spent unable to move")
    print(f"   • These are DIFFERENT metrics measuring DIFFERENT things!")

if __name__ == "__main__":
    demonstrate_wait_time_calculation()