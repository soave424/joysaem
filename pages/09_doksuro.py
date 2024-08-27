import streamlit as st
import requests
from bs4 import BeautifulSoup

# 예제 URL (사용자 정의)
url = "https://example.com"  # 실제 URL로 변경 필요

st.title("특정 요소 내용 추출")

if st.button('Search'):
    # URL로부터 데이터 요청
    response = requests.get(url)

    if response.status_code == 200:
        # HTML 파싱
        soup = BeautifulSoup(response.content, 'html.parser')

        # 특정 요소 추출 (예: p 태그 내 텍스트)
        # 여기서는 XPath를 기반으로 추출할 수 없으므로 해당 요소의 클래스를 기준으로 추출
        element = soup.select_one('div > div > p')

        if element:
            st.write("추출된 내용:")
            st.write(element.get_text(strip=True))
        else:
            st.write("해당 요소를 찾
