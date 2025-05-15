import requests
from urllib.parse import unquote
import streamlit as st

# Streamlit Secrets에서 API 키 불러오기
encoded_api_key = st.secrets["PlankDrawD_API_Key"]

# 인증키 디코딩 (두 번 디코딩)
api_key = unquote(unquote(encoded_api_key))

# API URL
API_URL = "https://apis.data.go.kr/1400119/PlantMiniService/miniatureSearch"

params = {
    'serviceKey': api_key,  # 디코딩된 인증키 사용
    'st': 1,  # 국명으로 검색
    'sw': "가는",  # 검색어
    'numOfRows': 10,  # 한 페이지에 결과 10개
    'pageNo': 1,  # 페이지 번호
}

# API 요청 보내기
try:
    response = requests.get(API_URL, params=params, verify=True)  # 인증서 검증 활성화
    response.raise_for_status()  # HTTP 오류가 있을 경우 예외 발생
    
    # 성공적인 응답 처리
    if response.status_code == 200:
        st.write(response.json())  # JSON 데이터 출력
    else:
        st.error(f"Error: {response.status_code}")
except requests.exceptions.SSLError as ssl_err:
    st.error(f"SSL 오류 발생: {ssl_err}")
except requests.exceptions.RequestException as req_err:
    st.error(f"요청 오류 발생: {req_err}")
except Exception as e:
    st.error(f"기타 오류 발생: {e}")
