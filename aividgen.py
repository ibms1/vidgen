import streamlit as st
import torch
from diffusers import StableDiffusionPipeline
from PIL import Image
import imageio
import os
import numpy as np
import cairosvg
import io
from pathlib import Path
import tempfile

class LightweightMotionGenerator:
    """نسخة خفيفة من مولد الحركة تعمل على CPU"""
    
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        self.frame_size = (512, 512)
    
    def generate_motion_frames(self, motion_type: str, num_frames: int = 8) -> list:
        """توليد إطارات الحركة باستخدام SVG"""
        frames = []
        for i in range(num_frames):
            phase = 2 * np.pi * i / num_frames
            if motion_type == "wave":
                svg = self._create_wave_svg(phase)
            elif motion_type == "cloud":
                svg = self._create_cloud_svg(phase)
            else:
                svg = self._create_default_svg(phase)
            
            png_data = cairosvg.svg2png(bytestring=svg.encode('utf-8'))
            frame = Image.open(io.BytesIO(png_data))
            frames.append(frame)
        return frames
    
    def _create_wave_svg(self, phase: float) -> str:
        """إنشاء موجة SVG"""
        width, height = self.frame_size
        return f"""
        <svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
            <path d="M0 {height/2}
                     C {width/4} {height/2 + 50*np.sin(phase)},
                       {3*width/4} {height/2 + 50*np.sin(phase + np.pi)},
                       {width} {height/2}"
                  stroke="blue" fill="none" stroke-width="5"/>
        </svg>
        """
    
    def _create_cloud_svg(self, phase: float) -> str:
        """إنشاء سحاب SVG"""
        width, height = self.frame_size
        x_offset = width/4 + width/4 * np.sin(phase)
        return f"""
        <svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
            <g transform="translate({x_offset},0)">
                <circle cx="100" cy="100" r="30" fill="#cccccc"/>
                <circle cx="130" cy="100" r="35" fill="#cccccc"/>
                <circle cx="160" cy="100" r="30" fill="#cccccc"/>
            </g>
        </svg>
        """
    
    def _create_default_svg(self, phase: float) -> str:
        """إنشاء حركة افتراضية SVG"""
        width, height = self.frame_size
        return f"""
        <svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
            <circle cx="{width/2 + 50*np.sin(phase)}" cy="{height/2}"
                    r="20" fill="red"/>
        </svg>
        """

def create_lightweight_sd_pipeline():
    """إنشاء نسخة خفيفة من Stable Diffusion pipeline"""
    model_id = "stabilityai/sd-turbo"
    pipe = StableDiffusionPipeline.from_pretrained(
        model_id,
        torch_dtype=torch.float32,  # استخدام float32 بدلاً من float16 للـ CPU
        use_safetensors=True
    )
    return pipe

def main():
    st.title("مولد الصور المتحركة")
    
    # إعداد النماذج عند بدء التطبيق
    if 'pipe' not in st.session_state:
        with st.spinner('جارِ تحميل النموذج...'):
            st.session_state.pipe = create_lightweight_sd_pipeline()
            st.session_state.motion_generator = LightweightMotionGenerator()
    
    # واجهة المستخدم
    prompt = st.text_input("أدخل وصف الصورة", "شاطئ جميل مع غروب الشمس")
    motion_type = st.selectbox(
        "اختر نوع الحركة",
        ["wave", "cloud", "default"]
    )
    num_frames = st.slider("عدد الإطارات", 4, 16, 8)
    
    if st.button("توليد الصورة المتحركة"):
        with st.spinner('جارِ توليد الصورة...'):
            try:
                # توليد الصورة الأساسية
                image = st.session_state.pipe(
                    prompt,
                    num_inference_steps=20
                ).images[0]
                
                # توليد إطارات الحركة
                motion_frames = st.session_state.motion_generator.generate_motion_frames(
                    motion_type,
                    num_frames
                )
                
                # دمج الصورة مع الحركة
                final_frames = []
                for frame in motion_frames:
                    # هنا يمكن إضافة منطق لدمج الصورة الأصلية مع إطار الحركة
                    final_frames.append(image)
                
                # حفظ كـ GIF
                with tempfile.NamedTemporaryFile(suffix='.gif', delete=False) as tmp_file:
                    image.save(
                        tmp_file.name,
                        save_all=True,
                        append_images=final_frames[1:],
                        duration=100,
                        loop=0
                    )
                    st.image(tmp_file.name)
                    
            except Exception as e:
                st.error(f"حدث خطأ: {str(e)}")

if __name__ == "__main__":
    main()