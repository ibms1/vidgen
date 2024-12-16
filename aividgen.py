import streamlit as st
import os
import tempfile
from PIL import Image, ImageDraw, ImageFont
import torch
import numpy as np
import imageio
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

def process_image(img):
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
    st.write("قم بإدخال النص وتحميل فيديو الحركة لإنشاء فيديو متحرك")

    # إدخال النص
    text = st.text_input("أدخل النص:", value="اكتب نصك هنا")

    # تحميل فيديو الحركة
    driving_video = st.file_uploader("قم بتحميل فيديو الحركة:", type=['mp4', 'avi'])

    if st.button("توليد الفيديو"):
        if not text or not driving_video:
            st.error("يرجى إدخال النص وتحميل فيديو الحركة")
            return

        try:
            with st.spinner("جاري تحميل النموذج..."):
                model = load_model()

            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as source_file, \
                 tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as driving_file, \
                 tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as output_file:

                # حفظ صورة النص
                text_image = create_text_image(text)
                text_image.save(source_file.name)
                st.image(text_image, caption="صورة النص المولدة", use_column_width=True)

                # حفظ فيديو الحركة
                with open(driving_file.name, 'wb') as f:
                    f.write(driving_video.getvalue())

                # معالجة الفيديو
                source = process_image(text_image)
                reader = imageio.get_reader(driving_file.name)
                fps = reader.get_meta_data()['fps']
                writer = imageio.get_writer(output_file.name, fps=fps)

                # إضافة شريط التقدم
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                frames = reader.count_frames()
                for i, frame in enumerate(reader):
                    driving = process_image(Image.fromarray(frame))
                    result_frame = generate_frame(model, source, driving)
                    writer.append_data(result_frame)
                    
                    # تحديث التقدم
                    progress = (i + 1) / frames
                    progress_bar.progress(progress)
                    status_text.text(f"جاري المعالجة... {progress * 100:.1f}%")

                reader.close()
                writer.close()

                # عرض الفيديو الناتج
                with open(output_file.name, 'rb') as f:
                    video_bytes = f.read()
                st.video(video_bytes)
                st.success("تم إنشاء الفيديو بنجاح!")

                # تنظيف الملفات المؤقتة
                for file in [source_file.name, driving_file.name, output_file.name]:
                    try:
                        os.unlink(file)
                    except:
                        pass

        except Exception as e:
            st.error(f"حدث خطأ: {str(e)}")

if __name__ == "__main__":
    main()