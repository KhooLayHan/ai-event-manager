
import matplotlib.pyplot as plt
import streamlit as st

st.title("CrowdFlow AI: Scenario Setup")

# Introductory Text
st.info("Define the event parameters to simulate crowd dynamics and get AI-powered recommendations.")

# Venue Selector
venue = st.selectbox(
    "Select a Venue",
    ["Axiata Arena (Concert)", "KLCC (Exhibition)"]
)

# Venue Map Display (for MVP, only first option needs to work)
if venue == "Axiata Arena (Concert)":
    st.markdown("**Venue Map Preview:**")
    # For demo, display a placeholder plot. Replace with actual venue_map.csv visualization if available.
    fig, ax = plt.subplots(figsize=(5, 3))
    ax.set_title("Axiata Arena Layout")
    ax.plot([0, 1, 2], [0, 1, 0], label="Gates")
    ax.legend()
    st.pyplot(fig)

# Simulation Parameters
st.markdown("**Simulation Parameters**")
attendees = st.slider("Number of Attendees", min_value=1000, max_value=50000, value=15000, step=1000)
gate_count = st.number_input("Number of Open Gates", min_value=1, max_value=10, value=3)

# The "X-Factor" Input
optimization_goal = st.radio(
    "Optimization Goal",
    ["Maximum Safety", "Balanced Safety & Cost"]
)

# Run Button
if st.button("▶️ Run Simulation & Get AI Insights"):
    st.session_state["venue"] = venue
    st.session_state["attendees"] = attendees
    st.session_state["gate_count"] = gate_count
    st.session_state["optimization_goal"] = optimization_goal
    st.success("Parameters saved! Switch to the Simulation Dashboard to view results.")
