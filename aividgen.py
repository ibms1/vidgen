import streamlit as st
import torch
from diffusers import DiffusionPipeline
from PIL import Image
import numpy as np
import io

# تحميل النموذج
@st.cache_resource
def load_model():
    return DiffusionPipeline.from_pretrained("black-forest-labs/FLUX.1-dev", torch_dtype=torch.bfloat16)

pipe = load_model()

# واجهة المستخدم
st.title("توليد فيديو من نص")
prompt = st.text_area("أدخل النص هنا:")

if st.button("توليد الفيديو"):
    if prompt:
        # توليد الفيديو
        video = pipe(prompt, num_inference_steps=50).videos[0]
        # تحويل الفيديو إلى صيغة يمكن عرضها في Streamlit
        video_bytes = video.read()
        st.video(video_bytes)
    else:
        st.warning("يرجى إدخال نص لتوليد الفيديو.")
