import streamlit as st

# Streamlit secrets에서 API 키 불러오기
API_KEY = st.secrets["PlankDraw_API_Key"]["key"]

st.write(f"API Key: {API_KEY}")  # 정상적으로 API Key가 불러와지는지 확인
