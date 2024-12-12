import streamlit as st
import tempfile
import os
import time
import cv2
import numpy as np
from moviepy.editor import VideoFileClip, ImageClip, concatenate_videoclips
import torch
from PIL import Image
import shutil

def set_page_config():
    st.set_page_config(
        page_title="AI Video Generator",
        layout="centered",
        initial_sidebar_state="collapsed"
    )

def create_temp_directory():
    """Create a temporary directory for video processing"""
    temp_dir = tempfile.mkdtemp()
    return temp_dir

def cleanup_temp_directory(temp_dir):
    """Clean up temporary directory and its contents"""
    try:
        shutil.rmtree(temp_dir)
    except Exception as e:
        st.error(f"Error cleaning up temporary files: {e}")

def generate_video_frames(prompt, temp_dir, progress_bar, status_text):
    """Generate video frames based on the prompt"""
    try:
        # Create a sequence of frames
        frames = []
        frame_count = 60  # 60 frames for 2 seconds at 30fps
        
        for i in range(frame_count):
            # Create a blank frame
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            
            # Add some animation (example: moving text)
            cv2.putText(
                frame,
                f"Frame {i+1}",
                (200 + i*3, 240),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 255, 255),
                2
            )
            
            frames.append(frame)
            
            # Update progress
            progress = (i + 1) / frame_count
            progress_bar.progress(progress)
            status_text.text(f"Generating frame {i+1}/{frame_count}")
            
        # Save frames as video
        output_path = os.path.join(temp_dir, "generated_video.mp4")
        height, width = frames[0].shape[:2]
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, 30, (width, height))
        
        for frame in frames:
            out.write(frame)
        
        out.release()
        
        return output_path
        
    except Exception as e:
        st.error(f"Error in video generation: {e}")
        return None

def main():
    set_page_config()
    
    # Custom CSS
    st.markdown("""
        <style>
        .stApp {
            max-width: 800px;
            margin: 0 auto;
        }
        .status-container {
            padding: 20px;
            background-color: #f0f2f6;
            border-radius: 10px;
            margin: 20px 0;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.title("AI Video Generator")
    st.subheader("Video Creation")
    
    # Text input for video description
    prompt = st.text_area(
        "Enter description to create video:",
        placeholder="Describe the video you want to create..."
    )
    
    if st.button("Create Video", key="create_video"):
        if not prompt:
            st.warning("Please enter a description for the video")
            return
            
        try:
            # Create temporary directory
            temp_dir = create_temp_directory()
            
            # Create status containers
            status_container = st.container()
            with status_container:
                st.markdown("<div class='status-container'>", unsafe_allow_html=True)
                progress_bar = st.progress(0)
                status_text = st.empty()
                time_text = st.empty()
                
                # Process start time
                start_time = time.time()
                
                # Generate video
                video_path = generate_video_frames(
                    prompt,
                    temp_dir,
                    progress_bar,
                    status_text
                )
                
                if video_path and os.path.exists(video_path):
                    # Process end time
                    end_time = time.time()
                    processing_time = end_time - start_time
                    
                    # Update status
                    status_text.text("Video generation completed!")
                    time_text.text(f"Processing time: {processing_time:.2f} seconds")
                    
                    # Display video
                    st.video(video_path)
                    
                    # Add download button
                    with open(video_path, 'rb') as file:
                        st.download_button(
                            label="Download Video",
                            data=file,
                            file_name="generated_video.mp4",
                            mime="video/mp4"
                        )
                else:
                    st.error("Failed to generate video")
                
                st.markdown("</div>", unsafe_allow_html=True)
            
            # Cleanup
            cleanup_temp_directory(temp_dir)
            
        except Exception as e:
            st.error(f"An error occurred: {e}")
            if 'temp_dir' in locals():
                cleanup_temp_directory(temp_dir)

if __name__ == "__main__":
    main()