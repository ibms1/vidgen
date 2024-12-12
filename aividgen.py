import streamlit as st
from PIL import Image
import time

def set_page_config():
    """Set page configuration"""
    st.set_page_config(page_title="First Order Motion Model", layout="centered")

# Page setup
set_page_config()

# Custom CSS
CSS = """
<style>
body {
    font-family: 'Arial', sans-serif;
    margin: 0;
    padding: 0;
}

/* Main button */
.stButton>button {
    background: linear-gradient(to right, #4facfe, #00f2fe);
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 5px;
}
.stButton>button:hover {
    background: linear-gradient(to left, #4facfe, #00f2fe);
}

/* Header */
h1 {
    font-size: 2.5em;
    margin: 20px 0;
    text-align: center;
}
</style>
"""

# Insert styling
st.markdown(CSS, unsafe_allow_html=True)

# Main interface
st.title("First Order Motion Model")

# Video creation interface
st.subheader("Video Creation")
prompt = st.text_area("Enter description to create video:")

if st.button("Create Video"):
    if prompt:
        with st.spinner("Creating video..."):
            # Here you should implement the actual video generation logic
            # For now, we'll show a placeholder message
            progress_bar = st.progress(0)
            for i in range(100):
                time.sleep(0.01)
                progress_bar.progress(i + 1)
            
            # After video creation, display success and the video
            st.success("Video created successfully!")
            
            # Create a placeholder for the video display
            video_placeholder = st.empty()
            
            # You should replace this with actual video display logic
            st.write("Video preview will appear here")
            # st.video("path_to_generated_video.mp4")
    else:
        st.warning("Please enter a description for the video")

# Footer
st.markdown("""
<footer style='text-align: center; padding: 20px;'>
    <p>&copy; EASYKW</p>
</footer>
""", unsafe_allow_html=True)