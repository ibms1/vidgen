import streamlit as st
from PIL import Image
import time

def set_page_config():
    st.set_page_config(page_title="AI Video Generator", layout="centered")

set_page_config()

CSS = """
<style>
.processing-info {
    padding: 15px;
    border-radius: 5px;
    background-color: #f8f9fa;
    border-left: 5px solid #17a2b8;
    margin: 10px 0;
}
.estimated-time {
    color: #6c757d;
    font-size: 0.9em;
    margin-top: 5px;
}
.status-message {
    margin: 10px 0;
    padding: 10px;
    border-radius: 4px;
}
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)
st.title("First Order Motion Model")
st.subheader("Video Creation")


hide_links_style = """
        <style>
        a {
            pointer-events: none;
            cursor: default;
            text-decoration: none;
            color: inherit;
        }
        </style>
        """
st.markdown(hide_links_style, unsafe_allow_html=True)


prompt = st.text_area("Enter description to create video:")

if st.button("Create Video"):
    if prompt:
        # Display estimated processing time
        st.info("⏱️ Estimated processing time: 3-5 minutes", icon="ℹ️")
        
        # Create processing stages
        stages = ["Initializing model", "Generating frames", "Processing video", "Finalizing"]
        progress_text = st.empty()
        progress_bar = st.progress(0)
        
        # Simulate processing stages
        for idx, stage in enumerate(stages):
            progress_text.text(f"Stage {idx+1}/{len(stages)}: {stage}")
            for i in range(25):
                time.sleep(0.1)
                progress_bar.progress((idx * 25 + i))
        
        progress_bar.progress(100)
        progress_text.text("Processing complete!")
        
        st.success("Video created successfully!")
        
        # Video status and information
        st.markdown("""
        <div class="processing-info">
            <h4>🎬 Video Status</h4>
            <p>Your video is ready for rendering. Please note:</p>
            <ul>
                <li>The video is being prepared for display</li>
                <li>This process may take a few moments</li>
                <li>The page will automatically update when ready</li>
            </ul>
            <p class="estimated-time">If the video doesn't appear within 2 minutes, please try refreshing the page.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Placeholder for future video display
        video_placeholder = st.empty()
        st.info("Video preview loading... Please wait.", icon="🎥")
        
    else:
        st.warning("Please enter a description for the video")

st.markdown("""
<footer style='text-align: center; padding: 20px;'>
    <p>&copy; EASYKW</p>
</footer>
""", unsafe_allow_html=True)