import streamlit as st
from streamlit.components.v1 import html
import time
from PIL import Image

def set_page_config():
    """تعيين إعدادات الصفحة"""
    st.set_page_config(page_title="First Order Motion Model", layout="centered")

# إعداد الصفحة
set_page_config()

# إنشاء واجهة جافا سكريبت مخصصة
CSS = """
<style>
body {
    font-family: 'Arial', sans-serif;
    margin: 0;
    padding: 0;
}

/* خلفية الوضع النهاري والليلي */
body[data-theme='light'] {
    background-color: #f0f0f0;
    color: #333;
}
body[data-theme='dark'] {
    background-color: #121212;
    color: #eee;
}

/* الزر الرئيسي */
button {
    background: linear-gradient(to right, #4facfe, #00f2fe);
    border: none;
    padding: 10px 20px;
    color: white;
    font-size: 1em;
    border-radius: 5px;
    cursor: pointer;
}
button:hover {
    background: linear-gradient(to left, #4facfe, #00f2fe);
}

/* رأس الصفحة */
h1 {
    font-size: 2.5em;
    margin: 20px 0;
    text-align: center;
}
</style>
"""

# إدراج التنسيق
html(CSS, unsafe_allow_html=True)

# تحديد الوضع الليلي والنهاري
st.sidebar.title("خيارات العرض")
mode = st.sidebar.radio("اختر الوضع:", ["نهار", "ليل"], index=0)
st.write(f"<body data-theme='{ 'light' if mode == 'نهار' else 'dark' }'>", unsafe_allow_html=True)

# واجهة التطبيق
st.title("First Order Motion Model")

# اختيار الوضعية (تحريك صورة أو موجه لإنشاء الفيديو)
choice = st.radio("اختر العملية:", ["تحريك صورة", "موجه لإنشاء فيديو"])

if choice == "تحريك صورة":
    st.subheader("رفع صورة لتحريكها")
    uploaded_image = st.file_uploader("ارفع الصورة هنا", type=["jpg", "png"])

    if uploaded_image is not None:
        image = Image.open(uploaded_image)
        st.image(image, caption="الصورة التي تم رفعها")

        if st.button("بدء التحريك"):
            with st.spinner("جاري التحريك..."):
                time.sleep(2)  # محاكاة زمن التنفيذ
            st.success("تم التحريك بنجاح!")
            st.image(image, caption="الصورة المتحركة (عينة)")

elif choice == "موجه لإنشاء فيديو":
    st.subheader("إنشاء فيديو")
    prompt = st.text_area("أدخل الوصف لإنشاء الفيديو:")

    if st.button("إنشاء الفيديو"):
        with st.spinner("جاري إنشاء الفيديو..."):
            time.sleep(3)  # محاكاة زمن التنفيذ
        st.success("تم إنشاء الفيديو بنجاح!")
        st.video("https://www.example.com/sample-video.mp4")  # وضع رابط عينة

# تضمين حقوق وإضافة جمالية
st.markdown("""<footer style='text-align: center;'>
    <p>&copy; 2024 First Order Motion Model - All rights reserved</p>
</footer>""", unsafe_allow_html=True)
