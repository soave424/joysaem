import streamlit as st
import requests

# Streamlit secrets에서 API 키 불러오기
API_KEY = st.secrets["PlankDraw_API_Key"]

# API 호출 함수 예시
def search_plants(keyword, page=1):
    API_URL = "http://apis.data.go.kr/1400119/PlantMiniService/miniatureSearch"
    params = {
        'serviceKey': API_KEY,  # secrets에서 불러온 API 키 사용
        'st': 1,  # 1: 국명으로 검색, 2: 학명으로 검색
        'sw': keyword,  # 검색어
        'numOfRows': 10,  # 페이지당 결과 수
        'pageNo': page,  # 페이지 번호
    }
    response = requests.get(API_URL, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"HTTP 오류: {response.status_code}")
        return None
