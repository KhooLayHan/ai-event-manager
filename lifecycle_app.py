import streamlit as st
import numpy as np
import time
import json
import os
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent / "src"))

from src.simulation.simulation_runners import run_animated_simulation, run_fast_simulation
from src.aws.lifecycle_bedrock_fixed import get_lifecycle_fallback_recommendation
from src.visualization.core import grid_to_base64_image

st.set_page_config(
    page_title="CrowdFlow AI - Full Event Lifecycle",
    page_icon="🏟️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_event_config(scenario_path):
    config_path = Path(scenario_path) / "event_config.json"
    with open(config_path, 'r') as f:
        return json.load(f)

st.markdown("""
<style>
.phase-indicator {
    padding: 0.5rem 1rem;
    border-radius: 0.5rem;
    font-weight: bold;
    text-align: center;
    margin: 0.5rem 0;
}
.phase-entry { background-color: #ff6b6b; color: white; }
.phase-mid { background-color: #4ecdc4; color: white; }
.phase-evacuation { background-color: #45b7d1; color: white; }
.time-display {
    background-color: #2c3e50;
    color: white;
    padding: 0.5rem;
    border-radius: 0.3rem;
    text-align: center;
    font-family: monospace;
    font-size: 1.1em;
}
.recommendation-card {
    background-color: #f8f9fa;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 4px solid #007bff;
    margin: 0.5rem 0;
}
</style>
""", unsafe_allow_html=True)

def main():
    st.title("🏟️ CrowdFlow AI - Full Event Lifecycle Simulator")
    st.markdown("**Experience the Complete Event Journey: Entry → Mingling → Emergency Response**")
    
    # Get available scenarios
    data_path = Path(__file__).parent / "data"
    available_scenarios = [d for d in os.listdir(data_path) if os.path.isdir(data_path / d)]
    
    with st.sidebar:
        st.header("🎛️ Event Configuration")
        
        # Scenario selector
        selected_scenario = st.selectbox(
            "Select Venue/Scenario:",
            available_scenarios,
            format_func=lambda x: x.replace('_', ' ').title()
        )
        
        # Store selected path
        scenario_path = data_path / selected_scenario
        st.session_state['selected_scenario_path'] = str(scenario_path)
        
        # Load config for selected scenario
        config = load_event_config(scenario_path)
        timeline = config["event_timeline"]
        scale_factor = config["simulation_time_scale_factor"]
        
        attendee_count = st.slider(
            "Total Event Attendees",
            min_value=500,
            max_value=3000,
            value=config["attendee_count"],
            step=100
        )
        
        initial_gates = st.slider(
            "Initial Open Gates",
            min_value=1,
            max_value=4,
            value=config["gate_configurations"]["before_ai"]["open_gates"]
        )
        
        # Simulation speed option
        simulation_speed = st.radio(
            "Simulation Speed:",
            ["Animated (Slow)", "Fast (No Animation)"],
            index=0,
            help="Animated shows step-by-step, Fast runs at maximum speed"
        )
        
        st.markdown("---")
        st.markdown("### 📋 Event Timeline")
        
        from src.simulation.time_converter import TimeConverter
        converter = TimeConverter(timeline["start_time"], scale_factor)
        
        entry_duration_mins = (converter.to_step(timeline["entry_rush_end_time"]) - converter.to_step(timeline["start_time"])) / scale_factor
        mid_duration_mins = (converter.to_step(timeline["mid_event_end_time"]) - converter.to_step(timeline["entry_rush_end_time"])) / scale_factor
        
        st.markdown(f"**{timeline['start_time']}-{timeline['entry_rush_end_time']}:** Entry Rush ({entry_duration_mins:.0f} mins)")
        st.markdown(f"**{timeline['entry_rush_end_time']}-{timeline['mid_event_end_time']}:** Mid-Event ({mid_duration_mins:.0f} mins)")  
        st.markdown(f"**{timeline['evacuation_start_time']}+:** Emergency Evacuation")
        st.markdown(f"*Scale: {scale_factor} steps = 1 minute*")
        st.markdown(f"*Buffer: +5 minutes evacuation simulation*")
        
        run_lifecycle = st.button("🚀 Simulate Full Event Lifecycle", type="primary")
    
    if run_lifecycle:
        run_full_lifecycle_demo(attendee_count, initial_gates, config, selected_scenario, simulation_speed)
    else:
        show_lifecycle_welcome(config, selected_scenario)

def show_lifecycle_welcome(config, scenario_name):
    timeline = config["event_timeline"]
    
    st.markdown(f"## 🎭 {scenario_name.replace('_', ' ').title()} Event Story")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="phase-indicator phase-entry">
        🚪 ENTRY RUSH ({timeline['start_time']}-{timeline['entry_rush_end_time']})
        </div>
        Attendees arrive and move toward the main area.
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="phase-indicator phase-mid">
        🍔 MID-EVENT ({timeline['entry_rush_end_time']}-{timeline['mid_event_end_time']})  
        </div>
        People explore facilities and socialize.
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="phase-indicator phase-evacuation">
        🚨 EVACUATION ({timeline['evacuation_start_time']}+)
        </div>
        Emergency evacuation scenario.
        """, unsafe_allow_html=True)
    
    st.info("👈 **Select your venue type and configure parameters to see AI optimization!**")

def run_full_lifecycle_demo(attendee_count: int, initial_gates: int, config: dict, scenario_name: str, simulation_speed: str):
    st.markdown(f"## 📊 {scenario_name.replace('_', ' ').title()} Lifecycle Dashboard")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔴 Before AI Optimization")
        before_animation = st.empty()
        before_time_phase = st.empty()
        before_metrics = st.empty()
    
    with col2:
        st.markdown("### 🟢 After AI Optimization")
        after_animation = st.empty()
        after_time_phase = st.empty()
        after_metrics = st.empty()
    
    status_text = st.empty()
    
    # Calculate expected total steps for progress bar
    timeline = config["event_timeline"]
    scale_factor = config["simulation_time_scale_factor"]
    from src.simulation.time_converter import TimeConverter
    converter = TimeConverter(timeline["start_time"], scale_factor)
    expected_total_steps = converter.to_step(timeline["mid_event_end_time"]) + 50
    
    # Run before simulation
    before_lifecycle_summary = {}
    
    if "Fast" in simulation_speed:
        # Fast mode - run entire simulation at once
        status_text.text("⚡ Running BEFORE simulation at maximum speed...")
        before_result = run_fast_simulation(attendee_count, initial_gates, expected_total_steps)
        before_lifecycle_summary = before_result['lifecycle_summary']
        
        # Show final result
        img_data = grid_to_base64_image(before_result['final_grid'], f"Step {before_result['total_steps']}")
        before_animation.markdown(f'<img src="{img_data}" width="100%">', unsafe_allow_html=True)
        
        phase_class = f"phase-{before_result['final_phase'].replace('_', '-')}"
        phase_display = before_result['final_phase'].replace('_', ' ').title()
        before_time_phase.markdown(f"""
        <div class="time-display">Event Time: {before_result['final_time']}</div>
        <div class="phase-indicator {phase_class}">{phase_display}</div>
        """, unsafe_allow_html=True)
        
        with before_metrics.container():
            col_a, col_b, col_c = st.columns(3)
            col_a.metric("Wait Time", f"{before_result['final_metrics']['real_wait_time_mins']} min")
            col_b.metric("Congestion", f"{before_result['final_metrics']['peak_congestion_percent']:.1f}%")
            col_c.metric("Entry Rate", f"{before_result['final_metrics'].get('entry_success_rate', 0):.1f}%")
        
        # Progress tracking (removed visual progress bar)
    else:
        # Animated mode - step by step
        status_text.text("🔄 Running BEFORE simulation...")
        before_step_count = 0
        for vis_grid, metrics, phase, real_time in run_animated_simulation(attendee_count, initial_gates):
            before_step_count += 1
            before_lifecycle_summary = metrics
            
            img_data = grid_to_base64_image(vis_grid, f"Step {before_step_count}")
            before_animation.markdown(f'<img src="{img_data}" width="100%">', unsafe_allow_html=True)
            
            phase_class = f"phase-{phase.replace('_', '-')}"
            phase_display = phase.replace('_', ' ').title()
            before_time_phase.markdown(f"""
            <div class="time-display">Event Time: {real_time}</div>
            <div class="phase-indicator {phase_class}">{phase_display}</div>
            """, unsafe_allow_html=True)
            
            with before_metrics.container():
                col_a, col_b, col_c = st.columns(3)
                col_a.metric("Wait Time", f"{metrics['real_wait_time_mins']} min")
                col_b.metric("Congestion", f"{metrics['peak_congestion_percent']:.1f}%")
                col_c.metric("Entry Rate", f"{metrics.get('entry_success_rate', 0):.1f}%")
            
            # Progress tracking (removed visual progress bar)
            
            # Update status text with current phase
            if phase == "entry_rush":
                status_text.text(f"🚪 Entry Rush Phase - Step {before_step_count}")
            elif phase == "mid_event":
                status_text.text(f"🍔 Mid-Event Phase - Step {before_step_count}")
            else:
                status_text.text(f"🚨 Evacuation Phase - Step {before_step_count}")
            
            if before_step_count >= expected_total_steps:
                break
    
    # AI Analysis - REAL AWS Bedrock Integration
    status_text.text("🤖 AI analyzing event lifecycle with AWS Bedrock...")
    
    # Call REAL AWS Bedrock for AI analysis
    try:
        from src.aws.lifecycle_bedrock_fixed import get_full_lifecycle_ai_analysis
        
        # Create proper lifecycle summary structure for AWS Bedrock
        lifecycle_summary = {
            "entry_rush": {
                "peak_congestion_percent": before_lifecycle_summary.get('peak_congestion_percent', 50),
                "avg_entry_time_mins": before_lifecycle_summary.get('real_wait_time_mins', 20),
                "duration_steps": 100
            },
            "mid_event": {
                "peak_congestion_percent": before_lifecycle_summary.get('peak_congestion_percent', 40) * 0.8,
                "avg_wait_time_mins": before_lifecycle_summary.get('real_wait_time_mins', 15),
                "duration_steps": 200
            },
            "evacuation": {
                "peak_congestion_percent": before_lifecycle_summary.get('peak_congestion_percent', 60) * 1.2,
                "evacuation_time_seconds": 240,
                "duration_steps": 150
            }
        }
        
        ai_analysis = get_full_lifecycle_ai_analysis(lifecycle_summary, attendee_count, initial_gates)
        status_text.text("✅ AWS Bedrock analysis complete!")
    except Exception as e:
        status_text.text(f"⚠️ AWS Bedrock unavailable, using fallback analysis...")
        
        # Create same structure for fallback
        lifecycle_summary = {
            "entry_rush": {
                "peak_congestion_percent": before_lifecycle_summary.get('peak_congestion_percent', 50),
                "avg_entry_time_mins": before_lifecycle_summary.get('real_wait_time_mins', 20),
                "duration_steps": 100
            },
            "mid_event": {
                "peak_congestion_percent": before_lifecycle_summary.get('peak_congestion_percent', 40) * 0.8,
                "avg_wait_time_mins": before_lifecycle_summary.get('real_wait_time_mins', 15),
                "duration_steps": 200
            },
            "evacuation": {
                "peak_congestion_percent": before_lifecycle_summary.get('peak_congestion_percent', 60) * 1.2,
                "evacuation_time_seconds": 240,
                "duration_steps": 150
            }
        }
        ai_analysis = get_lifecycle_fallback_recommendation(lifecycle_summary, attendee_count, initial_gates)
    
    st.markdown("## 💡 AI Analysis")
    st.markdown(f"""
    <div class="recommendation-card">
        <h4>📋 Assessment for {scenario_name.replace('_', ' ').title()}</h4>
        <p><strong>Critical Phase:</strong> {ai_analysis['critical_phase'].replace('_', ' ').title()}</p>
        <p>{ai_analysis['overall_assessment']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    for i, rec in enumerate(ai_analysis['recommendations'], 1):
        st.markdown(f"""
        <div class="recommendation-card">
            <h5>Recommendation {i}</h5>
            <p><strong>{rec['recommendation']}</strong></p>
            <p><em>{rec['reason']}</em></p>
        </div>
        """, unsafe_allow_html=True)
    
    # Extract AI optimization parameters
    optimized_entrance_gates = ai_analysis['optimized_parameters'].get('recommended_entrance_gates', initial_gates + 2)
    optimized_exit_gates = ai_analysis['optimized_parameters'].get('recommended_exit_gates', initial_gates + 1)
    optimized_attendees = ai_analysis['optimized_parameters'].get('optimal_attendee_capacity', attendee_count)
    optimized_staff = ai_analysis['optimized_parameters'].get('recommended_staff', 40)
    
    # Show optimization summary
    st.markdown("### 🚀 AI Optimization Applied:")
    col_opt1, col_opt2, col_opt3, col_opt4 = st.columns(4)
    
    with col_opt1:
        st.metric("Entrance Gates", f"{initial_gates} → {optimized_entrance_gates}", f"+{optimized_entrance_gates - initial_gates}")
    with col_opt2:
        st.metric("Exit Gates", f"{initial_gates} → {optimized_exit_gates}", f"+{optimized_exit_gates - initial_gates}")
    with col_opt3:
        st.metric("Staff", f"20 → {optimized_staff}", f"+{optimized_staff - 20}")
    with col_opt4:
        if optimized_attendees < attendee_count:
            st.metric("Attendees", f"{attendee_count} → {optimized_attendees}", f"-{attendee_count - optimized_attendees}")
        else:
            st.metric("Attendees", "Optimal", "✓")
    
    # Run after simulation with AI optimized parameters and dynamic venue map
    if "Fast" in simulation_speed:
        # Fast mode - run entire simulation at once
        status_text.text("⚡ Running AFTER simulation with AI optimizations...")
        
        # Create optimized venue map with AI suggested gates
        from src.simulation.venue_modifier import create_optimized_venue_map
        scenario_path = st.session_state['selected_scenario_path']
        optimized_venue_map = create_optimized_venue_map(scenario_path, optimized_entrance_gates, optimized_exit_gates)
        
        # Import the new function
        from src.simulation.simulation_runners import run_fast_simulation_with_optimized_map
        
        # Run simulation with optimized parameters
        after_result = run_fast_simulation_with_optimized_map(
            optimized_attendees, 
            optimized_entrance_gates, 
            expected_total_steps,
            optimized_venue_map
        )
        
        # Show final result
        img_data = grid_to_base64_image(after_result['final_grid'], f"Step {after_result['total_steps']} (Optimized)")
        after_animation.markdown(f'<img src="{img_data}" width="100%">', unsafe_allow_html=True)
        
        phase_class = f"phase-{after_result['final_phase'].replace('_', '-')}"
        phase_display = after_result['final_phase'].replace('_', ' ').title()
        after_time_phase.markdown(f"""
        <div class="time-display">Event Time: {after_result['final_time']}</div>
        <div class="phase-indicator {phase_class}">{phase_display}</div>
        """, unsafe_allow_html=True)
        
        with after_metrics.container():
            col_a, col_b, col_c = st.columns(3)
            col_a.metric("Wait Time", f"{after_result['final_metrics']['real_wait_time_mins']} min")
            col_b.metric("Congestion", f"{after_result['final_metrics']['peak_congestion_percent']:.1f}%")
            col_c.metric("Entry Rate", f"{after_result['final_metrics'].get('entry_success_rate', 0):.1f}%")
        
        # Progress tracking (removed visual progress bar)
    else:
        # Animated mode - step by step
        status_text.text("🔄 Running AFTER simulation with AI optimizations...")
        after_step_count = 0
        # Create optimized venue map with AI suggested gates
        from src.simulation.venue_modifier import create_optimized_venue_map
        scenario_path = st.session_state['selected_scenario_path']
        optimized_venue_map = create_optimized_venue_map(scenario_path, optimized_entrance_gates, optimized_exit_gates)
        
        # Import the new function
        from src.simulation.simulation_runners import run_animated_simulation_with_optimized_map
        
        for vis_grid, metrics, phase, real_time in run_animated_simulation_with_optimized_map(
            optimized_attendees, 
            optimized_entrance_gates, 
            optimized_venue_map
        ):
            after_step_count += 1
            
            img_data = grid_to_base64_image(vis_grid, f"Step {after_step_count} (Optimized)")
            after_animation.markdown(f'<img src="{img_data}" width="100%">', unsafe_allow_html=True)
            
            phase_class = f"phase-{phase.replace('_', '-')}"
            phase_display = phase.replace('_', ' ').title()
            after_time_phase.markdown(f"""
            <div class="time-display">Event Time: {real_time}</div>
            <div class="phase-indicator {phase_class}">{phase_display}</div>
            """, unsafe_allow_html=True)
            
            with after_metrics.container():
                col_a, col_b, col_c = st.columns(3)
                col_a.metric("Wait Time", f"{metrics['real_wait_time_mins']} min")
                col_b.metric("Congestion", f"{metrics['peak_congestion_percent']:.1f}%")
                col_c.metric("Entry Rate", f"{metrics.get('entry_success_rate', 0):.1f}%")
            
            # Progress tracking (removed visual progress bar)
            
            # Update status text with current phase
            if phase == "entry_rush":
                status_text.text(f"🚪 Entry Rush Phase (Optimized) - Step {after_step_count}")
            elif phase == "mid_event":
                status_text.text(f"🍔 Mid-Event Phase (Optimized) - Step {after_step_count}")
            else:
                status_text.text(f"🚨 Evacuation Phase (Optimized) - Step {after_step_count}")
            
            if after_step_count >= expected_total_steps:
                break
    
    status_text.text("✅ Analysis Complete!")
    
    st.success(f"""
    **🎉 {scenario_name.replace('_', ' ').title()} Optimization Complete!**
    
    AI optimized:
    • Entrance gates: {initial_gates} → {optimized_entrance_gates}
    • Exit gates: {initial_gates} → {optimized_exit_gates} 
    • Attendees: {attendee_count} → {optimized_attendees}
    • Staff: 20 → {optimized_staff}
    
    Simulation mode: {simulation_speed}
    """)

if __name__ == "__main__":
    main()