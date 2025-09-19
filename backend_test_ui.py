import matplotlib.pyplot as plt
import streamlit as st

from src.aws.bedrock import get_ai_recommendations
from src.shared_models import SimulationParameters

# --- IMPORTANT ---
# This UI imports the REAL backend functions. It's a simple harness
# for the backend team to test their logic visually.
from src.simulation.core import run_simulation_step_by_step

st.set_page_config(layout="wide")
st.title("Backend Development Test Harness 🔬")

# --- Inputs ---
st.sidebar.header("Simulation Parameters")
attendees = st.sidebar.slider("Attendees", 1000, 50000, 10000)
gates = st.sidebar.number_input("Open Gates", 1, 10, 3)
goal = st.sidebar.radio("Optimization Goal", ["Maximum Safety", "Balanced Safety & Cost"])

params = SimulationParameters(
    attendees=attendees,
    open_gates=gates,
    optimization_goal=goal,
)

# --- Outputs ---
col1, col2 = st.columns(2)

col1.header("Live Simulation Output")
simulation_placeholder = col1.empty()
metrics_placeholder = col1.empty()

col2.header("AI Recommendations")
ai_placeholder = col2.empty()

if st.sidebar.button("▶️ Run Backend Logic"):
    # --- Test AI Logic ---
    with st.spinner("Getting AI recommendations..."):
        recommendations = get_ai_recommendations(params)
        ai_placeholder.json([rec.__dict__ for rec in recommendations])

    # --- Test Simulation Logic ---
    fig, ax = plt.subplots()
    for grid_state, metrics in run_simulation_step_by_step(params):
        ax.clear()
        ax.imshow(grid_state, cmap="viridis")
        ax.axis("off")
        simulation_placeholder.pyplot(fig)
        metrics_placeholder.json(metrics.__dict__)
