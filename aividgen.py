import streamlit as st
import google.generativeai as genai
from moviepy.editor import *
import edge_tts
import asyncio
from faster_whisper import WhisperModel
import requests
import tempfile
from pathlib import Path
import uuid
import os
import shutil
import re
import time

# Page config with custom theme
st.set_page_config(
    page_title="AI Video Generator",
    page_icon="🎬",
    layout="wide",
)

# Custom CSS with centered layout
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #FF4B4B;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        border: none;
        margin-top: 1rem;
    }
    .stButton>button:hover {
        background-color: #FF2B2B;
    }
    .title {
        text-align: center;
        padding: 2rem 0;
        color: #FF4B4B;
        font-size: 2.5rem;
        font-weight: bold;
    }
    .input-container {
        max-width: 800px;
        margin: 0 auto;
        padding: 2rem;
        background-color: #f8f9fa;
        border-radius: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stTextInput>div>div>input {
        font-size: 1.2rem;
        padding: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'temp_dir' not in st.session_state:
    st.session_state.temp_dir = tempfile.mkdtemp()

# Cleanup on session end
def cleanup():
    if hasattr(st.session_state, 'temp_dir'):
        shutil.rmtree(st.session_state.temp_dir, ignore_errors=True)

import atexit
atexit.register(cleanup)

@st.cache_resource
def load_models():
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-pro')
        whisper_model = WhisperModel("base", device="cpu", compute_type="int8")
        return model, whisper_model
    except Exception as e:
        st.error(f"Error loading models: {e}")
        st.stop()

def generate_script(topic, model):
    prompt = """Create a short, engaging video script about the following topic.
    Rules:
    - Keep it under 60 seconds (about 150 words)
    - Use natural, conversational language
    - Focus on interesting facts or stories
    - Avoid any special characters or formatting
    - Make it engaging and educational
    
    Topic: """
    
    try:
        response = model.generate_content(prompt + topic)
        script = re.sub(r'[*#\-_~`]', '', response.text)
        return script.strip()
    except Exception as e:
        st.error(f"Error generating script: {e}")
        return None

async def text_to_speech(text):
    try:
        temp_path = os.path.join(st.session_state.temp_dir, f"{uuid.uuid4()}.mp3")
        communicate = edge_tts.Communicate(text, "en-US-EricNeural")
        await communicate.save(temp_path)
        return temp_path
    except Exception as e:
        st.error(f"Error generating speech: {e}")
        return None

def search_pexels_videos(query):
    try:
        headers = {
            "Authorization": st.secrets["PEXELS_API_KEY"]
        }
        
        # Format query for better results
        search_query = f"{query} stock footage"
        api_url = f"https://api.pexels.com/videos/search?query={search_query}&per_page=1&orientation=landscape"
        
        response = requests.get(api_url, headers=headers)
        if response.status_code != 200:
            st.error(f"Error accessing Pexels API: Status code {response.status_code}")
            return None
            
        data = response.json()
        if "videos" in data and len(data["videos"]) > 0:
            # Get the highest quality video file under 100MB
            video_files = data["videos"][0]["video_files"]
            sorted_files = sorted(
                [f for f in video_files if f["width"] >= 1280 and f.get("file_size", 0) < 100000000],
                key=lambda x: x["width"],
                reverse=True
            )
            
            if sorted_files:
                return sorted_files[0]["link"]
        return None
        
    except Exception as e:
        st.error(f"Error searching videos: {e}")
        return None

def create_video(audio_path, video_urls):
    try:
        temp_video_path = os.path.join(st.session_state.temp_dir, f"{uuid.uuid4()}.mp4")
        
        # Load video clips
        clips = []
        for url in video_urls:
            if url:
                try:
                    response = requests.get(url, stream=True, timeout=10)
                    if response.status_code == 200:
                        temp_path = os.path.join(st.session_state.temp_dir, f"{uuid.uuid4()}.mp4")
                        with open(temp_path, 'wb') as f:
                            for chunk in response.iter_content(chunk_size=8192):
                                if chunk:
                                    f.write(chunk)
                        
                        clip = VideoFileClip(temp_path)
                        clips.append(clip)
                except Exception as e:
                    st.warning(f"Could not download video from {url}: {e}")
                    continue
        
        if not clips:
            st.error("No valid video clips found")
            return None
            
        # Combine clips
        final_video = concatenate_videoclips(clips)
        
        # Add audio
        audio = AudioFileClip(audio_path)
        final_video = final_video.set_audio(audio)
        
        # Write final video
        final_video.write_videofile(
            temp_video_path,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile=os.path.join(st.session_state.temp_dir, 'temp-audio.m4a'),
            remove_temp=True
        )
        
        return temp_video_path
    except Exception as e:
        st.error(f"Error creating video: {e}")
        return None

def main():
    st.markdown("<h1 class='title'>🎬 AI Video Generator</h1>", unsafe_allow_html=True)
    
    # Load models
    model, whisper_model = load_models()
    
    # Centered input container
    st.markdown("<div class='input-container'>", unsafe_allow_html=True)
    
    topic = st.text_input(
        "Enter your topic",
        placeholder="e.g., Interesting facts about space",
        help="Enter any topic you'd like to create a video about"
    )
    
    generate_btn = st.button("Generate Video 🎥", type="primary", use_container_width=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Main content
    if generate_btn and topic:
        with st.spinner("🎬 Creating your video masterpiece..."):
            # Progress bar
            progress_bar = st.progress(0)
            
            # Generate script
            progress_bar.progress(20)
            script = generate_script(topic, model)
            if not script:
                return
            
            # Generate speech
            progress_bar.progress(40)
            audio_path = asyncio.run(text_to_speech(script))
            if not audio_path:
                return
            
            # Generate captions and search videos
            progress_bar.progress(60)
            segments, _ = whisper_model.transcribe(audio_path)
            
            video_urls = []
            for segment in segments:
                # Add small delay between searches
                time.sleep(1)
                url = search_pexels_videos(segment.text)
                if url:
                    video_urls.append(url)
            
            if not video_urls:
                st.error("Could not find suitable videos")
                return
            
            # Create final video
            progress_bar.progress(80)
            final_video_path = create_video(audio_path, video_urls)
            
            if final_video_path:
                progress_bar.progress(100)
                
                # Display video
                st.markdown("<div style='max-width: 800px; margin: 2rem auto;'>", unsafe_allow_html=True)
                st.video(final_video_path)
                
                # Download button
                with open(final_video_path, 'rb') as f:
                    st.download_button(
                        label="Download Video 📥",
                        data=f,
                        file_name=f"AI_Video_{topic[:30]}.mp4",
                        mime="video/mp4",
                        use_container_width=True
                    )
                st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()