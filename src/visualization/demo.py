import matplotlib.pyplot as plt
import streamlit as st


@st.cache_resource
def runSimulation(scenario, attendees, gate_count):
    fig = plt.figure(figsize=(10, 6))
    plt.title("Crowd Flow: " + scenario)
    plt.bar(["Attendees", "Open Gates"], [attendees, gate_count])
    st.session_state.fig = fig


if "fig" not in st.session_state:
    st.session_state.fig = plt

st.title("AI Event Manager: Demo")

st.subheader("Simulation Parameters")

scenario = st.selectbox("Select Scenario", ["Entry Rush", "Mid-Event Congestion", "Evacuation"])
attendees = st.slider("Number of Attendees", 1000, 50000, 10000, 1000)
gate_count = st.number_input("Number of Open Gates", 1, 10, 2)
# event_start_time = st.time_input("Event Start Time")

st.subheader("Simulation")

st.button(
    "Run Simulation", icon="▶️", on_click=runSimulation, args=(scenario, attendees, gate_count)
)

st.pyplot(st.session_state.fig, width="content")