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

# AWS Bedrock Titan integration
import boto3
import base64

def generate_titan_image(prompt: str) -> "PIL.Image.Image":
    """
    Generate an image using AWS Bedrock Titan Image Generator G1 v2.
    Returns a PIL Image object or None if generation fails.
    """
    try:
        bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")
        response = bedrock.invoke_model(
            modelId="amazon.titan-image-generator-g1-v2",
            contentType="application/json",
            accept="application/json",
            body=f'{{"prompt": "{prompt}"}}'
        )
        result = response["body"].read()
        # Titan returns base64-encoded image in JSON
        import json
        img_b64 = json.loads(result)["generated_image"]
        img_bytes = base64.b64decode(img_b64)
        from PIL import Image
        import io
        return Image.open(io.BytesIO(img_bytes))
    except Exception as e:
        st.error(f"Failed to generate image with Titan: {e}")
        return None

def show_simulation_dashboard(
    before_metrics, after_metrics,
    before_animation_frames, after_animation_frames,
    ai_recommendations,
    before_img_path=None, after_img_path=None,
    use_titan=False
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

    # Stretch Goal: Titan-generated images for comparison slider
    import io
    import os
    from urllib.parse import urlparse
    import requests
    from PIL import Image

    def load_image(path):
        if os.path.exists(path):
            try:
                return Image.open(path)
            except Exception as e:
                st.error(f"Failed to load local image: {path}. Error: {e}")
                return None
        parsed = urlparse(path)
        if parsed.scheme in ("http", "https"):
            try:
                resp = requests.get(path, timeout=5)
                resp.raise_for_status()
                return Image.open(io.BytesIO(resp.content))
            except Exception as e:
                st.error(f"Failed to load image from URL: {path}. Error: {e}")
                return None
        st.error(f"Image path is not a valid file or URL: {path}")
        return None

    if use_titan:
        st.markdown("### 🔀 Before vs After Heatmap Comparison (Titan Generated)")
        before_prompt = "Crowd density heatmap before AI optimization at a concert venue"
        after_prompt = "Crowd density heatmap after AI optimization at a concert venue"
        before_img = generate_titan_image(before_prompt)
        after_img = generate_titan_image(after_prompt)
    elif before_img_path and after_img_path:
        st.markdown("### 🔀 Before vs After Heatmap Comparison")
        before_img = load_image(before_img_path)
        after_img = load_image(after_img_path)
    else:
        before_img = after_img = None

    # If before_img_path and after_img_path are PIL images, use them directly
    if isinstance(before_img_path, Image.Image) and isinstance(after_img_path, Image.Image):
        before_img = before_img_path
        after_img = after_img_path
    elif before_img_path and after_img_path:
        before_img = load_image(before_img_path)
        after_img = load_image(after_img_path)
    else:
        before_img = after_img = None

    if before_img and after_img:
        image_comparison(
            img1=before_img,
            img2=after_img,
            label1="Before",
            label2="After"
        )
    elif use_titan:
        st.warning("Could not generate one or both images with Titan. See error messages above.")
    elif before_img_path and after_img_path:
        st.warning("Could not load one or both images for comparison. See error messages above.")

# Demo: Show dashboard with sample data if run directly
if __name__ == "__main__":
    # Sample metrics
    before_metrics = {
        "Avg. Wait Time": {"value": "28 Mins", "delta": "High Risk", "delta_color": "inverse"},
        "Gate Utilization": {"value": "65%", "delta": "-", "delta_color": "normal"}
    }
    after_metrics = {
        "Avg. Wait Time": {"value": "7 Mins", "delta": "-75%", "delta_color": "normal"},
        "Gate Utilization": {"value": "90%", "delta": "+25%", "delta_color": "normal"}
    }
    # Remove mock image URLs; animation frames can be empty or replaced with Titan-generated images if desired
    before_animation_frames = []
    after_animation_frames = []
    ai_recommendations = [
        {"recommendation": "Open Gate C for faster flow.", "reason": "Simulation shows congestion at Gate B."},
        {"recommendation": "Increase signage near exits.", "reason": "Evacuation time reduced by 30%."}
    ]

    # Generate images using Titan
    before_prompt = "Crowd density heatmap before AI optimization at a concert venue"
    after_prompt = "Crowd density heatmap after AI optimization at a concert venue"
    before_img = generate_titan_image(before_prompt)
    after_img = generate_titan_image(after_prompt)

    # Pass generated images directly to the dashboard
    show_simulation_dashboard(
        before_metrics,
        after_metrics,
        before_animation_frames,
        after_animation_frames,
        ai_recommendations,
        before_img_path=before_img,   # Pass Titan-generated PIL image object
        after_img_path=after_img      # Pass Titan-generated PIL image object
    )
