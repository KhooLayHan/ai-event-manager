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

# If using streamlit-image-comparison, import it (uncomment if installed)
from streamlit_image_comparison import image_comparison


def show_simulation_dashboard(before_metrics, after_metrics, before_animation_frames, after_animation_frames, ai_recommendations, before_img_path=None, after_img_path=None):
	# Inject custom CSS to set the image comparison slider color to black
		st.markdown(
		"""
		<style>
		/* Aggressively target the slider and handle for streamlit-image-comparison */
		.image-comparison-slider {
			background: #000 !important;
			border-color: #000 !important;
			box-shadow: 0 0 0 2px #000 !important;
		}
		.image-comparison-slider:before, .image-comparison-slider:after {
			background: #000 !important;
			border-color: #000 !important;
		}
		/* Target the handle arrow icons */
		.image-comparison-slider svg {
			fill: #000 !important;
		}
		/* Target the vertical line */
		.image-comparison-divider {
			background: #000 !important;
		}
		</style>
		""",
		unsafe_allow_html=True
	)

	st.title("📊 Simulation Dashboard")
	st.markdown("**Goal:** A visually stunning and instantly understandable showcase of your project's impact.")

	# Main Layout: Side-by-side columns
	col1, col2 = st.columns(2)

	# Column Headers
	col1.header("Before AI Optimization")
	col2.header("After AI Optimization")

	# Animation Placeholders
	anim_placeholder1 = col1.empty()
	anim_placeholder2 = col2.empty()

	# Key Performance Metrics
	with col1:
		for metric, value in before_metrics.items():
			st.metric(label=metric, value=value.get('value'), delta=value.get('delta'), delta_color=value.get('delta_color', 'normal'))
	with col2:
		for metric, value in after_metrics.items():
			st.metric(label=metric, value=value.get('value'), delta=value.get('delta'), delta_color=value.get('delta_color', 'normal'))

	# Animation update loop (example: show first frame)
	# Replace with actual animation logic as needed
	if before_animation_frames:
		anim_placeholder1.image(before_animation_frames[0], caption="Crowd Movement (Before)")
	if after_animation_frames:
		anim_placeholder2.image(after_animation_frames[0], caption="Crowd Movement (After)")

	# AI "Thinking" Spinner (wrap Bedrock call in actual usage)
	with st.spinner("🤖 AI is analyzing scenarios..."):
		# Simulate AI processing (replace with actual call)
		pass

	# AI Recommendations Display (Explainable AI)
	with st.expander("💡 AI Recommendations", expanded=True):
		for rec in ai_recommendations:
			st.markdown(f"**Recommendation:** {rec['recommendation']}")
			st.markdown(f"**Reason:** {rec['reason']}")

	# Stretch Goal: Comparison Slider (if images provided)
	import io
	import os
	from urllib.parse import urlparse

	import requests
	from PIL import Image
	def load_image(path):
		# Check if local file
		if os.path.exists(path):
			try:
				return Image.open(path)
			except Exception as e:
				st.error(f"Failed to load local image: {path}. Error: {e}")
				return None
		# Check if valid URL
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

	if before_img_path and after_img_path:
		st.markdown("### 🔀 Before vs After Heatmap Comparison")
		before_img = load_image(before_img_path)
		after_img = load_image(after_img_path)
		if before_img and after_img:
			image_comparison(
				img1=before_img,
				img2=after_img,
				label1="Before",
				label2="After"
			)
		else:
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
	# Use placeholder images (can be replaced with actual frames)
	before_animation_frames = ["https://via.placeholder.com/300x200?text=Before"]
	after_animation_frames = ["https://via.placeholder.com/300x200?text=After"]
	ai_recommendations = [
		{"recommendation": "Open Gate C for faster flow.", "reason": "Simulation shows congestion at Gate B."},
		{"recommendation": "Increase signage near exits.", "reason": "Evacuation time reduced by 30%."}
	]
	# Optional: demo images for comparison slider
	before_img_path = "./mock_image/before-crowd-control.png"
	after_img_path = "./mock_image/after-crowd-control.png"
	show_simulation_dashboard(
		before_metrics,
		after_metrics,
		before_animation_frames,
		after_animation_frames,
		ai_recommendations,
		before_img_path,
		after_img_path
	)
