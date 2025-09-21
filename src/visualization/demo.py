from time import sleep

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from matplotlib import colors

from src.shared_models import SimulationParameters
from src.stubs.mock_backend import get_ai_recommendations, run_simulation_step_by_step

# initialize value
if "is_simulating" not in st.session_state:
    st.session_state.is_simulating = False

if "grid_state" not in st.session_state:
    st.session_state.grid_state = None

if "metrics" not in st.session_state:
    st.session_state.metrics = {"Wait Time": [], "Peak Congestion": []}

st.title("CrowdFlow AI: Demo")

col1, col2 = st.columns([6, 4])

with col1:
    st.subheader("Simulation Visualization")
    visual_figure = st.empty()

with col2:
    st.subheader("Simulation Parameters")

    venue = st.selectbox("Select Venue", ["Venue A", "Venue B", "Venue C"])
    scenario = st.selectbox("Select Scenario", ["Entry Rush", "Mid-Event Congestion", "Evacuation"])
    attendees = st.slider("Number of Attendees", 1000, 50000, 10000, 1000)
    gate_count = st.number_input("Number of Open Gates", 1, 10, 2)

    button_container = st.container(horizontal=True)

    start_button = button_container.button("Run Simulation", icon="▶️")

    if start_button:
        # Reset the simulation state
        st.session_state.grid_state = None
        st.session_state.metrics.get("Wait Time").append([])
        st.session_state.metrics.get("Peak Congestion").append([])
        st.session_state.is_simulating = True

    stop_button = button_container.button("Stop Simulation", icon="⏹️")

    if stop_button:
        st.session_state.is_simulating = False

    st.divider()

    ai_recommand_button = st.button("Get AI Recommendations", icon="🤖")

    if ai_recommand_button:
        ai_responce_list = []

        with st.status("AI thinking...") as status:
            ai_responce_list = get_ai_recommendations(
                SimulationParameters(attendees, gate_count, scenario)
            )
            status.update(label="Done!", state="complete")

        for ai_responce in ai_responce_list:
            st.markdown(f"""
                - **Recommendation**: {ai_responce.recommendation}
                - **Reason**: {ai_responce.reason}
            """)


st.subheader("Simulation Metrics")

col1, col2 = st.columns(2)
with col1:
    avg_wait_time_metric = st.empty()

with col2:
    peak_congestion_metric = st.empty()

with st.container(horizontal=True):
    with st.container(border=True):
        st.html('<div style="text-align: center"> Average Wait Time </div>')
        avg_wait_time_line_chart = st.empty()

    with st.container(border=True):
        st.html('<div style="text-align: center"> Peak Congestion Percentage </div>')
        peak_congestion_line_chart = st.empty()


def update_ui():
    wait_time_data = st.session_state.metrics.get("Wait Time")
    peak_congestion_data = st.session_state.metrics.get("Peak Congestion")

    # update figure
    if st.session_state.grid_state is None:
        visual_figure.pyplot(plt.figure(figsize=(10, 10)))
    else:
        # figure color map
        cmap = colors.ListedColormap(["red", "blue"])
        bounds = [0, 0.5, 1]
        norm = colors.BoundaryNorm(bounds, cmap.N)

        # plot grid
        fig, ax = plt.subplots()
        ax.axis("off")
        ax.imshow(st.session_state.grid_state, cmap=cmap, norm=norm)
        visual_figure.pyplot(fig)

    # update metrics
    if len(wait_time_data) == 0 or len(wait_time_data[-1]) == 0:
        avg_wait_time_metric.metric("Average Wait Time", "0 Mins", "0 Mins")
        peak_congestion_metric.metric("Peak Congestion Percentage", "0%", "0%")
    else:
        index = len(wait_time_data[-1]) - 1
        current = wait_time_data[-1][index]
        last = wait_time_data[0][index]
        avg_wait_time_metric.metric(
            "Average Wait Time",
            f"{current} Mins",
            f"{current - last} Mins",
            delta_color="inverse",
        )
        index = len(peak_congestion_data[-1]) - 1
        current = peak_congestion_data[-1][index]
        last = peak_congestion_data[0][index]
        peak_congestion_metric.metric(
            "Peak Congestion Percentage",
            f"{current * 100:.2f}%",
            f"{(current - last) * 100:.2f}%",
            delta_color="inverse",
        )

    # update line charts
    df = pd.DataFrame(wait_time_data).T
    avg_wait_time_line_chart.line_chart(df)
    df = pd.DataFrame(peak_congestion_data).T
    peak_congestion_line_chart.line_chart(df)


update_ui()

while st.session_state.is_simulating:
    for grid_state, metrics in run_simulation_step_by_step(
        SimulationParameters(attendees, gate_count, scenario)
    ):
        # store data
        st.session_state.grid_state = grid_state
        st.session_state.metrics.get("Wait Time")[-1].append(metrics.avg_wait_time_mins)
        st.session_state.metrics.get("Peak Congestion")[-1].append(metrics.peak_congestion_percent)

        update_ui()
        sleep(0.5)

    st.session_state.is_simulating = False
    update_ui()
