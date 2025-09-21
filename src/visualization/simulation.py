"""
Simulation Dashboard Structure & Component Guide
------------------------------------------------
This module implements the main event dashboard for the AI Event Manager project.
It is designed for a visually stunning and instantly understandable showcase of project impact.

Component Overview:

| Component                        | Streamlit Command         | Purpose & Key Details |
| -------------------------------- | ------------------------- | --------------------- |
| Main Layout                      | st.columns(2)             | Side-by-side "before and after" comparison. All components placed inside col1 or col2. |
| Column Headers                   | col1.header(), col2.header() | Clear labels: "Before AI Optimization" and "After AI Optimization". |
| Animation Placeholder            | col1.empty(), col2.empty() | Key for animations. Containers updated in a loop to show agent movement. |
| Key Performance Metrics          | st.metric()                | Quantifiable results. E.g., col1.metric("Avg. Wait Time", "28 Mins", delta="High Risk", delta_color="inverse") |
| AI "Thinking" Spinner            | st.spinner()               | Improves UX. Wrap Bedrock call in with st.spinner("🤖 AI is analyzing scenarios...") |
| AI Recommendations Display       | st.info(), st.expander()   | Display Explainable AI output. Use markdown for bullet points. |
| (Stretch Goal) Comparison Slider | image_comparison()         | High-impact visual "wow" factor. Displays before/after heatmaps. |

Refer to PLAN_FRONTEND_COMPONENTS.md for further details and rationale.
"""

import streamlit as st
from streamlit_image_comparison import image_comparison
try:
    from src.aws.bedrock import generate_titan_image
except ModuleNotFoundError:
    import sys, os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
    from src.aws.bedrock import generate_titan_image

def show_simulation_dashboard(
    before_metrics, after_metrics,
    before_animation_frames, after_animation_frames,
    ai_recommendations,
    before_img=None, after_img=None,
    before_img_error=None, after_img_error=None
):
    st.title("📊 Simulation Dashboard")
    st.markdown("**Goal:** A visually stunning and instantly understandable showcase of your project's impact.")

    col1, col2 = st.columns(2)
    col1.header("Before AI Optimization")
    col2.header("After AI Optimization")

    anim_placeholder1 = col1.empty()
    anim_placeholder2 = col2.empty()

    with col1:
        for metric, value in before_metrics.items():
            st.metric(label=metric, value=value.get('value'), delta=value.get('delta'), delta_color=value.get('delta_color', 'normal'))
    with col2:
        for metric, value in after_metrics.items():
            st.metric(label=metric, value=value.get('value'), delta=value.get('delta'), delta_color=value.get('delta_color', 'normal'))

    # Animation update loop (example: show first frame)
    if before_animation_frames:
        anim_placeholder1.image(before_animation_frames[0], caption="Crowd Movement (Before)")
    if after_animation_frames:
        anim_placeholder2.image(after_animation_frames[0], caption="Crowd Movement (After)")

    with st.spinner("🤖 AI is analyzing scenarios..."):
        pass

    with st.expander("💡 AI Recommendations", expanded=True):
        for rec in ai_recommendations:
            st.markdown(f"**Recommendation:** {rec['recommendation']}")
            st.markdown(f"**Reason:** {rec['reason']}")

    # Titan-generated images for comparison slider
    st.markdown("### 🔀 Before vs After Heatmap Comparison (Titan Generated)")
    if before_img and after_img:
        image_comparison(
            img1=before_img,
            img2=after_img,
            label1="Before",
            label2="After"
        )
    else:
        st.warning("Could not generate one or both images with Titan.")
        if before_img_error:
            st.error(f"Titan error (before): {before_img_error}")
        if after_img_error:
            st.error(f"Titan error (after): {after_img_error}")

# Demo: Show dashboard with sample data if run directly
if __name__ == "__main__":
    before_metrics = {
        "Avg. Wait Time": {"value": "28 Mins", "delta": "High Risk", "delta_color": "inverse"},
        "Gate Utilization": {"value": "65%", "delta": "-", "delta_color": "normal"}
    }
    after_metrics = {
        "Avg. Wait Time": {"value": "7 Mins", "delta": "-75%", "delta_color": "normal"},
        "Gate Utilization": {"value": "90%", "delta": "+25%", "delta_color": "normal"}
    }
    before_animation_frames = []
    after_animation_frames = []
    ai_recommendations = [
        {"recommendation": "Open Gate C for faster flow.", "reason": "Simulation shows congestion at Gate B."},
        {"recommendation": "Increase signage near exits.", "reason": "Evacuation time reduced by 30%."}
    ]

    # Ensure sys.path is set for direct execution
    import sys, os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
    from src.aws.bedrock import generate_titan_image

    before_prompt = "Crowd density heatmap before AI optimization at a concert venue"
    after_prompt = "Crowd density heatmap after AI optimization at a concert venue"
    before_img = generate_titan_image(before_prompt)
    after_img = generate_titan_image(after_prompt)

    show_simulation_dashboard(
        before_metrics,
        after_metrics,
        before_animation_frames,
        after_animation_frames,
        ai_recommendations,
        before_img=before_img,
        after_img=after_img
    )
