import os
import sys
import time

import matplotlib.pyplot as plt
import streamlit as st

# Ensure project root is on sys.path so `src` can be imported when run via Streamlit
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
	sys.path.insert(0, PROJECT_ROOT)

from src.shared_models import SimulationParameters
from src.simulation.core import run_simulation_step_by_step



st.title("AI Event Manager: Demo")

st.subheader("Simulation Parameters")

scenario = st.selectbox("Select Scenario", ["Entry Rush", "Mid-Event Congestion", "Evacuation"])
attendees = st.slider("Number of Attendees", 1000, 50000, 10000, 1000)
gate_count = st.number_input("Number of Open Gates", 1, 10, 2)
# event_start_time = st.time_input("Event Start Time")

st.subheader("Simulation")
st.info("Press Run to stream the simulation.")

# Map scenario to an optimization goal label (optional informational use)
goal = "Maximum Safety" if scenario in ("Evacuation",) else "Balanced Safety & Cost"

final_only = st.checkbox("Show final result only", value=False)
run_clicked = st.button("Run Simulation", icon="▶️")


frame_placeholder = st.empty()
metrics_placeholder = st.empty()

# Add colours represtation
st.markdown("""
<div style='margin-top: 1em; margin-bottom: 1em;'>
<b>Legend:</b><br>
<span style='display:inline-block;width:18px;height:18px;background:#1f77b4;border-radius:50%;margin-right:6px;vertical-align:middle;'></span> Entry<br>
<span style='display:inline-block;width:18px;height:18px;background:#2ca02c;border-radius:50%;margin-right:6px;vertical-align:middle;'></span> Exit<br>
<span style='display:inline-block;width:18px;height:18px;background:#d62728;border-radius:50%;margin-right:6px;vertical-align:middle;'></span> Attendee<br>
<span style='display:inline-block;width:18px;height:18px;background:#111111;border-radius:50%;margin-right:6px;vertical-align:middle;'></span> Wall/Obstacle<br>
<span style='display:inline-block;width:18px;height:18px;background:#FFFFFF;border-radius:50%;margin-right:6px;vertical-align:middle;border:1px solid #ccc;'></span> Empty/Walkable
</div>
""", unsafe_allow_html=True)

if run_clicked:
	params = SimulationParameters(attendees=attendees, open_gates=gate_count, optimization_goal=goal)
	total_attendees = attendees  # value from the frontend user choice

	if final_only:
		# Consume the generator and keep the last frame/metrics/stats
		step = 0
		last_grid = None
		last_metrics = None
		last_stats = None
		for grid, metrics, stats in run_simulation_step_by_step(params):
			step += 1
			last_grid = grid
			last_metrics = metrics
			last_stats = stats

		if last_grid is not None and last_metrics is not None and last_stats is not None:
			fig, ax = plt.subplots(figsize=(6, 4))
			cmap = plt.matplotlib.colors.ListedColormap(
				["#FFFFFF", "#111111", "#1f77b4", "#2ca02c", "#d62728"]
			)
			im = ax.imshow(last_grid, cmap=cmap, interpolation="nearest", vmin=0, vmax=4)
			ax.set_xticks([])
			ax.set_yticks([])
			ax.set_title(f"{scenario} — Final Result")
			frame_placeholder.pyplot(fig, clear_figure=True)
			plt.close(fig)

			active_attendees = last_stats["active_attendees"]
			completed = last_stats["completed"]
			efficiency = last_stats["efficiency"]

			metrics_placeholder.markdown(
				f"- Step: **{step}**\n"
				f"- Total attendees: **{total_attendees}**\n"
				f"- Active attendees: **{active_attendees}**\n"
				f"- Completed: **{completed}**\n"
				f"- Throughput efficiency: **{efficiency:.2%}**\n"
				f"- Avg wait (mins): **{last_metrics.avg_wait_time_mins}**\n"
				f"- Peak congestion: **{last_metrics.peak_congestion_percent:.2f}**"
			)
			if active_attendees == 0:
				st.success("All attendees reached exits. Final result shown.")
		else:
			st.warning("No frames produced by simulation.")
	else:
		# Stream frame-by-frame
		step = 0
		for grid, metrics, stats in run_simulation_step_by_step(params):
			step += 1
			# Render grid as a discrete heatmap
			fig, ax = plt.subplots(figsize=(6, 4))
			cmap = plt.matplotlib.colors.ListedColormap(
				["#FFFFFF", "#111111", "#1f77b4", "#2ca02c", "#d62728"]
			)
			im = ax.imshow(grid, cmap=cmap, interpolation="nearest", vmin=0, vmax=4)
			ax.set_xticks([])
			ax.set_yticks([])
			ax.set_title(f"{scenario} — Step {step}")
			frame_placeholder.pyplot(fig, clear_figure=True)
			plt.close(fig)

			# Use simulation stats for metrics
			active_attendees = stats["active_attendees"]
			completed = stats["completed"]
			efficiency = stats["efficiency"]

			metrics_placeholder.markdown(
				f"- Step: **{step}**\n"
				f"- Total attendees: **{total_attendees}**\n"
				f"- Active attendees: **{active_attendees}**\n"
				f"- Completed: **{completed}**\n"
				f"- Throughput efficiency: **{efficiency:.2%}**\n"
				f"- Avg wait (mins): **{metrics.avg_wait_time_mins}**\n"
				f"- Peak congestion: **{metrics.peak_congestion_percent:.2f}**"
			)

			# Stop condition: all attendees finished
			if active_attendees == 0:
				st.success("All attendees reached exits. Simulation complete.")
				break

			# Small delay to visualize progression smoothly
			time.sleep(0.05)
