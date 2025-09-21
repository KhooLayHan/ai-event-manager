
import streamlit as st
from simulation.core import run_simulation  # Assumes simulation logic is here

st.title("🔀 What-If Scenario Playground")
st.markdown("Play with AI recommendations and instantly see the impact on crowd metrics.")

# Example: Define interactive widgets for recommendations
st.header("AI Recommendations (Interactive)")

# Example widgets (replace with real recommendations/parameters)
open_gate_c = st.checkbox("Open Gate C for faster flow", value=True)
increase_signage = st.checkbox("Increase signage near exits", value=True)
extra_staff = st.slider("Extra staff deployed", min_value=0, max_value=20, value=5)
gate_open_time = st.slider("Gate C opening time (minutes earlier)", min_value=0, max_value=30, value=10)

# Collect parameters for simulation
params = {
	"open_gate_c": open_gate_c,
	"increase_signage": increase_signage,
	"extra_staff": extra_staff,
	"gate_open_time": gate_open_time,
	# Add more as needed
}

# Run the 'after' simulation with current widget values
after_metrics, after_animation_frames = run_simulation(params)

st.subheader("Updated Metrics (After)")
for metric, value in after_metrics.items():
	st.metric(label=metric, value=value.get('value'), delta=value.get('delta'), delta_color=value.get('delta_color', 'normal'))

# Optionally show updated animation/heatmap
if after_animation_frames:
	st.image(after_animation_frames[0], caption="Crowd Movement (After)")





