import streamlit as st
import torch
import os
import cv2
import numpy as np
from PIL import Image

# إعدادات النموذج
from diffusers import FluxPipeline

# تحميل النموذج
pipe = FluxPipeline.from_pretrained("black-forest-labs/FLUX.1-dev", torch_dtype=torch.bfloat16)
pipe.enable_model_cpu_offload()

# واجهة المستخدم لإدخال النص
st.title("Text to Video Generation")
prompt = st.text_input("Enter your text description:")

# توليد الصور من النص
if prompt:
    st.write("Generating video...")

    # توليد مجموعة من الصور
    images = []
    for i in range(10):  # لتوليد 10 صور كمثال
        image = pipe(
            prompt,
            height=512,
            width=512,
            guidance_scale=7.5,
            num_inference_steps=50,
            max_sequence_length=512,
            generator=torch.Generator("cpu").manual_seed(i)
        ).images[0]
        images.append(np.array(image))

    # إنشاء الفيديو من الصور
    video_path = "generated_video.mp4"
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video = cv2.VideoWriter(video_path, fourcc, 1, (512, 512))

    for img in images:
        video.write(cv2.cvtColor(img, cv2.COLOR_RGB2BGR))  # تحويل الصورة من RGB إلى BGR

    video.release()

    # عرض الفيديو في واجهة التطبيق
    st.video(video_path)

    # السماح للمستخدم بتحميل الفيديو إذا رغب
    st.download_button("Download Video", video_path)

    # حذف الفيديو بعد العرض
    os.remove(video_path)
