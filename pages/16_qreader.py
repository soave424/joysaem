import cv2
import streamlit as st
from PIL import Image
import numpy as np

def extract_url_from_qr_opencv(image):
    detector = cv2.QRCodeDetector()
    data, bbox, straight_qrcode = detector.detectAndDecode(image)
    if bbox is not None:
        return data
    return "No QR code found"

st.title('QR Code URL Extractor with OpenCV')

uploaded_file = st.file_uploader("Choose a QR code image...", type=["png", "jpg", "jpeg"])
if uploaded_file is not None:
    image = Image.open(uploaded_file).convert('RGB')
    open_cv_image = np.array(image)
    # Convert RGB to BGR
    open_cv_image = open_cv_image[:, :, ::-1].copy()

    result = extract_url_from_qr_opencv(open_cv_image)
    st.image(image, caption='Uploaded QR Image', use_column_width=True)
    st.write('Extracted URL:', result)
