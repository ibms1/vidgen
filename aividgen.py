import streamlit as st
import os
import tempfile
from PIL import Image, ImageDraw, ImageFont
import torch
import numpy as np
import imageio
import math
import warnings
warnings.filterwarnings("ignore")

# استيراد النموذج
from first_order_model import FirstOrderModel

def create_text_image(text: str, width: int = 512, height: int = 512) -> Image.Image:
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 40)
    except:
        font = ImageFont.load_default()
    
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    draw.text((x, y), text, fill='black', font=font)
    return image

def create_motion_frames(num_frames=60):
    """إنشاء إطارات الحركة التلقائية"""
    frames = []
    for i in range(num_frames):
        # إنشاء مصفوفة فارغة
        frame = np.zeros((256, 256, 3), dtype=np.uint8)
        frame.fill(255)  # جعل الخلفية بيضاء
        
        # إضافة بعض التأثيرات البصرية البسيطة
        angle = 2 * math.pi * i / num_frames
        scale = 1.0 + 0.2 * math.sin(angle)
        
        # إضافة بعض الألوان المتغيرة في الخلفية
        color_value = int(128 + 127 * math.sin(angle))
        frame[:, :, 0] = color_value  # تغيير القناة الحمراء
        
        frames.append(frame)
    return frames

def process_image(img):
    if isinstance(img, np.ndarray):
        img = Image.fromarray(img)
    
    img = img.convert('RGB')
    img = img.resize((256, 256), Image.Resampling.LANCZOS)
    img = np.array(img, dtype=np.float32) / 255.0
    img = np.transpose(img, (2, 0, 1))
    img = torch.from_numpy(img).unsqueeze(0)
    
    if torch.cuda.is_available():
        img = img.cuda()
    return img

def generate_frame(model, source, driving):
    with torch.no_grad():
        predictions = model(source, driving)
        result = predictions['prediction'].cpu().numpy()[0]
        result = np.transpose(result, (1, 2, 0))
        result = (result * 255).clip(0, 255).astype(np.uint8)
        return result

@st.cache_resource
def load_model():
    model = FirstOrderModel()
    if torch.cuda.is_available():
        model = model.cuda()
    model.eval()
    return model

def main():
    st.set_page_config(page_title="توليد فيديو من النص")
    
    st.title("توليد فيديو من النص")
    st.write("قم بإدخال النص لإنشاء فيديو متحرك")

    # إدخال النص
    text = st.text_input("أدخل النص:", value="اكتب نصك هنا")

    if st.button("توليد الفيديو"):
        if not text:
            st.error("يرجى إدخال النص")
            return

        try:
            with st.spinner("جاري تحميل النموذج..."):
                model = load_model()

            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as output_file:
                # إنشاء صورة النص
                text_image = create_text_image(text)
                st.image(text_image, caption="صورة النص المولدة", use_column_width=True)

                # إنشاء إطارات الحركة
                motion_frames = create_motion_frames()
                
                # معالجة الفيديو
                source = process_image(text_image)
                writer = imageio.get_writer(output_file.name, fps=30)

                # إضافة شريط التقدم
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                total_frames = len(motion_frames)
                for i, frame in enumerate(motion_frames):
                    driving = process_image(frame)
                    result_frame = generate_frame(model, source, driving)
                    writer.append_data(result_frame)
                    
                    # تحديث التقدم
                    progress = (i + 1) / total_frames
                    progress_bar.progress(progress)
                    status_text.text(f"جاري المعالجة... {progress * 100:.1f}%")

                writer.close()

                # عرض الفيديو الناتج
                with open(output_file.name, 'rb') as f:
                    video_bytes = f.read()
                st.video(video_bytes)
                st.success("تم إنشاء الفيديو بنجاح!")

                # تنظيف الملفات المؤقتة
                try:
                    os.unlink(output_file.name)
                except:
                    pass

        except Exception as e:
            st.error(f"حدث خطأ: {str(e)}")

if __name__ == "__main__":
    main()