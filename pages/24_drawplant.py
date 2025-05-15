import streamlit as st
import requests

# API 키를 Streamlit의 설정에서 불러오기
API_KEY = st.secrets["PlankDraw_API_Key"]

API_URL = "https://apis.data.go.kr/1400119/PlantMiniService/miniatureSearch"

params = {
    'serviceKey': API_KEY,
    'st': 1,  # 국명으로 검색
    'sw': "가는",  # 검색어
    'numOfRows': 10,  # 한 페이지에 결과 10개
    'pageNo': 1,  # 페이지 번호
}

response = requests.get(API_URL, params=params)
if response.status_code == 200:
    print(response.json())
else:
    print(f"Error: {response.status_code}")