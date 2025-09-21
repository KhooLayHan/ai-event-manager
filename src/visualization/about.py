import os

import streamlit as st

st.set_page_config(
    page_title="About CrowdFlow AI",
    page_icon="👨‍💻",
    layout="centered"
)

st.title("About CrowdFlow AI")

# System Architecture
with st.expander("System Architecture"):
    st.image(
        os.path.join(os.path.dirname(__file__), "./image/system-architecture-diagram.png"),
        caption="System Architecture Diagram",
    )
    st.markdown(
        "This diagram shows the planned implementation and integration of all major components."
    )

# Technology Stack
with st.expander("Technology Stack"):
    st.markdown(
        """
        - **Frontend**: Streamlit
        - **Simulation Engine**: NumPy
        - **Visualization**: Matplotlib
        - **AWS Integration**: Amazon Bedrock
        """
    )

# Novelty & Impact (X-Factors)
with st.expander("Our Winning Strategy (The X-Factors)"):
    st.markdown(
        """
        - **Explainable AI (XAI):** Recommendations are always accompanied by clear, data-driven reasons.
        - **Cost-Aware AI:** The system can optimize for either maximum safety or a balanced safety/cost scenario, reflecting real-world business constraints.
        - **Interactive 'What-If' Scenarios:** Users can tweak AI suggestions and instantly see the impact in the dashboard.
        """
    )

# Team Credits
with st.expander("Meet the Team"):
    st.markdown(
        """
        - Khoo Lay Han (tp079817@mail.apu.edu.my)
        - Soo Zhan Thong (soo.zhan.thong@student.mmu.edu.my)
        - Chow Yong Xiang (xiang05127@1utar.my)
        - Tan Zheng Ye (B2201278@helplive.edu.my)
        - Chia Kai-Jun (B2300232@helplive.edu.my)
        """
    )
