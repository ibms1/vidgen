import argparse
import os
import time
import cv2
import numpy as np
import torch
from PIL import Image, ImageDraw, ImageFont
import tempfile
from typing import Union
import imageio
import warnings
warnings.filterwarnings("ignore")

def create_text_image(text: str, width: int = 512, height: int = 512) -> Image.Image:
    """
    تحويل النص إلى صورة
    """
    # إنشاء صورة بيضاء
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    try:
        # محاولة تحميل خط عربي إذا كان متوفراً
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 40)
    except:
        # استخدام الخط الافتراضي إذا لم يكن الخط العربي متوفراً
        font = ImageFont.load_default()
    
    # حساب موقع النص
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    # رسم النص
    draw.text((x, y), text, fill='black', font=font)
    
    return image

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
    verbose: bool = True
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
            
            if verbose:
                progress = (frame_idx + 1) / total_frames * 100
                print(f"\rالتقدم: {progress:.1f}%", end="")
                
        if verbose:
            print("\nاكتمل توليد الفيديو!")
            
        cap.release()
        writer.close()
        return True
        
    except Exception as e:
        print(f"خطأ في معالجة الفيديو: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description='تحويل النص إلى فيديو متحرك')
    parser.add_argument('--text', type=str, required=True, help='النص المراد تحويله')
    parser.add_argument('--driving', type=str, required=True, help='مسار فيديو الحركة')
    parser.add_argument('--output', type=str, required=True, help='مسار الفيديو الناتج')
    parser.add_argument('--quiet', action='store_true', help='إيقاف عرض رسائل التقدم')
    
    args = parser.parse_args()
    
    try:
        # إنشاء مجلد مؤقت
        temp_dir = tempfile.mkdtemp()
        
        # تحويل النص إلى صورة
        print("جاري تحويل النص إلى صورة...")
        text_image = create_text_image(args.text)
        source_path = os.path.join(temp_dir, "text_image.png")
        text_image.save(source_path)
        
        # تحميل النموذج
        print("جاري تحميل النموذج...")
        model = load_first_order_model()
        
        # معالجة الفيديو
        print("جاري توليد الفيديو...")
        start_time = time.time()
        
        success = process_video(
            model,
            source_path,
            args.driving,
            args.output,
            verbose=not args.quiet
        )
        
        if success:
            end_time = time.time()
            processing_time = end_time - start_time
            print(f"\nتم إنشاء الفيديو بنجاح في {processing_time:.1f} ثانية")
            print(f"تم حفظ الفيديو في: {args.output}")
        
    except Exception as e:
        print(f"حدث خطأ: {str(e)}")
    
    finally:
        # تنظيف الملفات المؤقتة
        try:
            import shutil
            shutil.rmtree(temp_dir)
        except:
            pass

if __name__ == "__main__":
    main()