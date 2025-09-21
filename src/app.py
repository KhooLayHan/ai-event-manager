
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import streamlit as st
from src.visualization.simulation import show_simulation_dashboard

def main():
    import streamlit as st
    st.sidebar.title("Diagnostics")
    page = st.sidebar.radio("Select page", ["Dashboard", "Bedrock Diagnostics"])

    if page == "Bedrock Diagnostics":
        st.header("Amazon Bedrock Connectivity Test")
        from src.aws.bedrock import verify_bedrock_access
        result = verify_bedrock_access()
        if result["success"]:
            st.success(result["message"])
        else:
            st.error(result["message"])
        st.info("If you see an error, check your AWS credentials, region, and IAM permissions for Bedrock.")
        return

    # Example demo data (replace with real simulation results)
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

    # Titan image generation with error capture
    from src.aws.bedrock import generate_titan_image
    before_prompt = "Crowd density heatmap before AI optimization at a concert venue"
    after_prompt = "Crowd density heatmap after AI optimization at a concert venue"
    before_img = None
    after_img = None
    before_img_error = None
    after_img_error = None
    try:
        before_img = generate_titan_image(before_prompt)
        if before_img is None:
            before_img_error = "No image returned. Check AWS credentials, permissions, or Titan API error."
    except Exception as e:
        before_img_error = str(e)
    try:
        after_img = generate_titan_image(after_prompt)
        if after_img is None:
            after_img_error = "No image returned. Check AWS credentials, permissions, or Titan API error."
    except Exception as e:
        after_img_error = str(e)

    show_simulation_dashboard(
        before_metrics,
        after_metrics,
        before_animation_frames,
        after_animation_frames,
        ai_recommendations,
        before_img=before_img,
        after_img=after_img,
        before_img_error=before_img_error,
        after_img_error=after_img_error
    )

if __name__ == "__main__":
    main()
