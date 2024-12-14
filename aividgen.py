import streamlit as st
import tempfile
import os
import time
import cv2
import numpy as np
import torch
from PIL import Image
import shutil
from typing import Union
import imageio
import warnings
warnings.filterwarnings("ignore")

def create_temp_directory():
    """إنشاء مجلد مؤقت"""
    return tempfile.mkdtemp()

def cleanup_temp_directory(temp_dir: str):
    """تنظيف المجلد المؤقت"""
    try:
        shutil.rmtree(temp_dir)
    except Exception as e:
        st.warning(f"خطأ في تنظيف المجلد المؤقت: {e}")

def load_first_order_model():
    """
    تحميل نموذج First Order Motion
    """
    from first_order_model import FirstOrderModel
    model = FirstOrderModel()
    if torch.cuda.is_available():
        model = model.cuda()
    else:
        model = model.cpu()
    model.eval()
    return model

def process_image(img_input: Union[str, np.ndarray, Image.Image]) -> torch.Tensor:
    """
    معالجة الصورة للنموذج
    """
    if isinstance(img_input, str):
        img = Image.open(img_input)
    elif isinstance(img_input, np.ndarray):
        img = Image.fromarray(img_input)
    elif isinstance(img_input, Image.Image):
        img = img_input
    else:
        raise TypeError("نوع الإدخال غير مدعوم")
    
    # تغيير الحجم وتحويل الصورة
    img = img.convert('RGB')
    img = img.resize((256, 256), Image.Resampling.LANCZOS)
    img = np.array(img, dtype=np.float32) / 255.0
    img = np.transpose(img, (2, 0, 1))
    img = torch.from_numpy(img).unsqueeze(0)
    
    if torch.cuda.is_available():
        img = img.cuda()
    return img

def generate_frame(model, source: torch.Tensor, driving: torch.Tensor) -> np.ndarray:
    """
    توليد إطار واحد
    """
    with torch.no_grad():
        predictions = model(source, driving)
        result = predictions['prediction'].cpu().numpy()[0]
        result = np.transpose(result, (1, 2, 0))
        result = (result * 255).clip(0, 255).astype(np.uint8)
        return result

def process_video(
    model,
    source_path: str,
    driving_path: str,
    output_path: str,
    progress_callback=None
) -> bool:
    """
    معالجة الفيديو بأكمله
    """
    try:
        source = process_image(source_path)
        cap = cv2.VideoCapture(driving_path)
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        
        writer = imageio.get_writer(output_path, fps=fps)
        
        for frame_idx in range(total_frames):
            ret, frame = cap.read()
            if not ret:
                break
                
            driving = process_image(frame)
            result_frame = generate_frame(model, source, driving)
            writer.append_data(result_frame)
            
            if progress_callback:
                progress = (frame_idx + 1) / total_frames
                progress_callback(progress, frame_idx + 1, total_frames)
                
        cap.release()
        writer.close()
        return True
        
    except Exception as e:
        st.error(f"خطأ في معالجة الفيديو: {str(e)}")
        return False

def main():
    st.set_page_config(
        page_title="مولد الفيديو المتحرك",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("محول الصور إلى فيديو متحرك")
    
    # تحميل الملفات
    col1, col2 = st.columns(2)
    
    with col1:
        source_image = st.file_uploader(
            "صورة المصدر",
            type=['png', 'jpg', 'jpeg'],
            help="اختر صورة المصدر التي تريد تحريكها"
        )
        
    with col2:
        driving_video = st.file_uploader(
            "فيديو الحركة",
            type=['mp4', 'avi'],
            help="اختر فيديو الحركة المرجعي"
        )
    
    if st.button("بدء التحويل", use_container_width=True):
        if not all([source_image, driving_video]):
            st.warning("يرجى تحميل جميع الملفات المطلوبة")
            return
            
        try:
            temp_dir = create_temp_directory()
            
            # حفظ الملفات المؤقتة
            source_temp = os.path.join(temp_dir, "source.png")
            Image.open(source_image).save(source_temp)
            
            driving_temp = os.path.join(temp_dir, "driving.mp4")
            with open(driving_temp, 'wb') as f:
                f.write(driving_video.read())
            
            output_temp = os.path.join(temp_dir, "result.mp4")
            
            # تحميل النموذج
            with st.spinner("جاري تحميل النموذج..."):
                model = load_first_order_model()
            
            # إعداد عناصر التقدم
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            def update_progress(progress, current_frame, total_frames):
                progress_bar.progress(progress)
                status_text.text(f"معالجة الإطار {current_frame}/{total_frames}")
            
            # معالجة الفيديو
            start_time = time.time()
            success = process_video(
                model,
                source_temp,
                driving_temp,
                output_temp,
                update_progress
            )
            
            if success:
                end_time = time.time()
                processing_time = end_time - start_time
                
                st.success(f"تم إنشاء الفيديو بنجاح! (المدة: {processing_time:.1f} ثانية)")
                
                # عرض النتيجة
                st.video(output_temp)
                
                # زر التحميل
                with open(output_temp, 'rb') as file:
                    st.download_button(
                        label="تحميل الفيديو",
                        data=file,
                        file_name="animated_video.mp4",
                        mime="video/mp4"
                    )
            
            cleanup_temp_directory(temp_dir)
            
        except Exception as e:
            st.error(f"حدث خطأ غير متوقع: {str(e)}")
            if 'temp_dir' in locals():
                cleanup_temp_directory(temp_dir)

if __name__ == "__main__":
    main()