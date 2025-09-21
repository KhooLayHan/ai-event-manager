import streamlit as st

st.set_page_config(
    page_title="CrowdFlow AI",
    page_icon="🎉",
    layout="wide",
    initial_sidebar_state="expanded",
)

demo = st.Page("demo.py", title="Demo", icon="🎉")
about = st.Page("about.py", title="About", icon="👨‍💻")

pg = st.navigation([demo, about], position="top")

pg.run()
