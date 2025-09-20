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

# Cap aligned with backend default (was 300 in UI)
MAX_STEPS_UI = 200

st.title("AI Event Manager: Demo")

st.subheader("Simulation Parameters")

scenario = st.selectbox("Select Scenario", ["Entry Rush", "Mid-Event Congestion", "Evacuation"])
attendees = st.slider("Number of Attendees", 1000, 50000, 10000, 1000)
gate_count = st.number_input("Number of Open Gates", 1, 10, 2)
# event_start_time = st.time_input("Event Start Time")

st.subheader("Simulation")
st.info("Press Run to stream the simulation.")
st.caption(f"Stop conditions: all attendees finished OR {MAX_STEPS_UI} steps cap (aligned with backend).")

# Map scenario to an optimization goal label (optional informational use)
goal = "Maximum Safety" if scenario in ("Evacuation",) else "Balanced Safety & Cost"

final_only = st.checkbox("Show final result only", value=False)
run_clicked = st.button("Run Simulation", icon="▶️")

frame_placeholder = st.empty()
metrics_placeholder = st.empty()

if run_clicked:
	params = SimulationParameters(attendees=attendees, open_gates=gate_count, optimization_goal=goal)
	# Backend scales down attendees: n_attendees = max(1, attendees // 20)
	total_attendees = max(1, attendees // 20)

	if final_only:
		# Consume the generator and keep the last frame/metrics
		step = 0
		last_grid = None
		last_metrics = None
		for grid, metrics in run_simulation_step_by_step(params):
			step += 1
			last_grid = grid
			last_metrics = metrics

		if last_grid is not None and last_metrics is not None:
			fig, ax = plt.subplots(figsize=(6, 4))
			cmap = plt.matplotlib.colors.ListedColormap(
				["#FFFFFF", "#111111", "#1f77b4", "#2ca02c", "#d62728"]
			)
			ax.imshow(last_grid, cmap=cmap, interpolation="nearest")
			ax.set_xticks([])
			ax.set_yticks([])
			ax.set_title(f"{scenario} — Final Result (Step {step})")
			frame_placeholder.pyplot(fig, clear_figure=True)
			plt.close(fig)

			active_attendees = int((last_grid == 4).sum())
			completed = max(0, total_attendees - active_attendees)
			efficiency = (completed / total_attendees) if total_attendees else 0.0

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
		for grid, metrics in run_simulation_step_by_step(params):
			step += 1
			# Render grid as a discrete heatmap
			fig, ax = plt.subplots(figsize=(6, 4))
			cmap = plt.matplotlib.colors.ListedColormap(
				["#FFFFFF", "#111111", "#1f77b4", "#2ca02c", "#d62728"]
			)
			ax.imshow(grid, cmap=cmap, interpolation="nearest")
			ax.set_xticks([])
			ax.set_yticks([])
			ax.set_title(f"{scenario} — Step {step}")
			frame_placeholder.pyplot(fig, clear_figure=True)
			plt.close(fig)

			# Compute live attendee metrics from the grid visualization
			active_attendees = int((grid == 4).sum())
			completed = max(0, total_attendees - active_attendees)
			efficiency = (completed / total_attendees) if total_attendees else 0.0

			metrics_placeholder.markdown(
				f"- Step: **{step}**\n"
				f"- Total attendees: **{total_attendees}**\n"
				f"- Active attendees: **{active_attendees}**\n"
				f"- Completed: **{completed}**\n"
				f"- Throughput efficiency: **{efficiency:.2%}**\n"
				f"- Avg wait (mins): **{metrics.avg_wait_time_mins}**\n"
				f"- Peak congestion: **{metrics.peak_congestion_percent:.2f}**"
			)

			# Stop conditions to avoid endless runs
			if active_attendees == 0:
				st.success("All attendees reached exits. Simulation complete.")
				break
			# Cap aligned with backend default
			if step >= MAX_STEPS_UI:
				st.warning(f"Stopped after {MAX_STEPS_UI} steps (cap).")
				break

			# Small delay to visualize progression smoothly
			time.sleep(0.05)
