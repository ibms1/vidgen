# Importing required libraries
import torch
from transformers import pipeline
import numpy as np
from PIL import Image
import imageio
import streamlit as st

# تحميل النموذج من Hugging Face
model = pipeline("image-generation", model="huggingface/biggan-deep-256")

# تحديد التصنيف (مثل cat, airplane)
category = "cat"

# توليد صورة
def generate_image(category):
    generated_image = model(category)
    return generated_image[0]['image']

# توليد مجموعة من الصور
def generate_images(num_images=10, category="cat"):
    images = []
    for _ in range(num_images):
        img = generate_image(category)
        images.append(img)
    return images

# تحويل الصور المولدة إلى صور متحركة (GIF)
def create_gif(images, filename="animated_image.gif", duration=0.5):
    # تحويل صور PIL إلى numpy arrays
    images_np = [np.array(img) for img in images]
    imageio.mimsave(filename, images_np, duration=duration)

# توليد 10 صور (على سبيل المثال)
images = generate_images(10, category)

# إنشاء GIF من الصور المولدة
create_gif(images, filename="cat_animation.gif", duration=0.5)

# عرض الـ GIF في Streamlit
st.image("cat_animation.gif", caption="القط المتحرك", use_column_width=True)
