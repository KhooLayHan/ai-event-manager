from time import sleep

import matplotlib.pyplot as plt
import streamlit as st
from matplotlib import colors

from src.shared_models import SimulationParameters
from src.stubs.mock_backend import run_simulation_step_by_step

st.title("AI Event Manager: Demo")

button_container = st.container(horizontal=True)

start_button = button_container.button("Run Simulation", icon="▶️")

if start_button:
    # Reset the simulation state
    st.session_state.fig = plt.figure()
    st.session_state.metrics = {"Wait Time": [], "Peak Congestion": []}

    st.session_state.is_simulating = True

stop_button = button_container.button("Stop Simulation", icon="⏹️")

if stop_button:
    st.session_state.is_simulating = False

col1, col2 = st.columns(2)

with col1:
    if "fig" not in st.session_state:
        st.session_state.fig = plt.figure()

    st.subheader("Simulation Visualization")
    visual_figure = st.pyplot(st.session_state.fig)

with col2:
    if "metrics" not in st.session_state:
        st.session_state.metrics = {"Wait Time": [], "Peak Congestion": []}

    st.subheader("Simulation Metrics")

    with st.container(border=True):
        st.html('<div style="text-align: center"> Average Wait Time </div>')
        avg_wait_time_line_chart = st.line_chart(st.session_state.metrics, y="Wait Time")

    with st.container(border=True):
        st.html('<div style="text-align: center"> Peak Congestion Percentage </div>')
        peak_congestion_line_chart = st.line_chart(st.session_state.metrics, y="Peak Congestion")

    avg_wait_time_label = st.empty()
    avg_wait_time_label.write("Average Wait Time: 0 minutes")
    peak_congestion_label = st.empty()
    peak_congestion_label.write("Peak Congestion: 0%")


st.subheader("Simulation Parameters")

venue = st.selectbox("Select Venue", ["Venue A", "Venue B", "Venue C"])
scenario = st.selectbox("Select Scenario", ["Entry Rush", "Mid-Event Congestion", "Evacuation"])
attendees = st.slider("Number of Attendees", 1000, 50000, 10000, 1000)
gate_count = st.number_input("Number of Open Gates", 1, 10, 2)

# Initialize the is_simulating flag
if "is_simulating" not in st.session_state:
    st.session_state.is_simulating = False

while st.session_state.is_simulating:
    for grid_state, metrics in run_simulation_step_by_step(SimulationParameters(attendees, gate_count, scenario)):

        # figure color map
        cmap = colors.ListedColormap(['red', 'blue'])
        bounds = [0,0.5,1]
        norm = colors.BoundaryNorm(bounds, cmap.N)

        # plot grid
        fig, ax = plt.subplots()
        ax.axis("off")
        ax.imshow(grid_state, cmap=cmap, norm=norm)

        # update UI
        visual_figure.pyplot(fig)
        avg_wait_time_line_chart.add_rows({"Wait Time": [metrics.avg_wait_time_mins]})
        peak_congestion_line_chart.add_rows({"Peak Congestion": [metrics.peak_congestion_percent * 100]})
        avg_wait_time_label.write(f"Average Wait Time: {metrics.avg_wait_time_mins} minutes")
        peak_congestion_label.write(f"Peak Congestion: {metrics.peak_congestion_percent * 100}%")

        # store data
        st.session_state.fig = fig
        st.session_state.metrics.get("Wait Time").append(metrics.avg_wait_time_mins)
        st.session_state.metrics.get("Peak Congestion").append(metrics.peak_congestion_percent * 100)

        sleep(0.5)

    st.session_state.is_simulating = False
