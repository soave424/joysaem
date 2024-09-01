import streamlit as st
import requests
from bs4 import BeautifulSoup

# Streamlit 앱 제목
st.title("웹 페이지 스크래핑 도구")

# URL 입력 받기
url = st.text_input("URL을 입력하세요:")

# 사용자가 URL을 입력하고 버튼을 누르면 실행
if st.button("스크래핑 시작"):
    if url:
        try:
            # URL의 HTML을 가져옴
            response = requests.get(url)
            response.raise_for_status()  # 요청 실패 시 예외 발생

            # 인코딩을 UTF-8로 강제 설정 (한글 깨짐 방지)
            response.encoding = 'utf-8'

            # BeautifulSoup을 사용하여 HTML 파싱
            soup = BeautifulSoup(response.text, 'html.parser')

            # 페이지의 텍스트 콘텐츠 추출
            page_text = soup.get_text()

            # 페이지의 HTML 콘텐츠 출력
            st.subheader("스크래핑된 HTML 콘텐츠:")
            st.code(soup.prettify(), language='html')

            # 페이지의 텍스트 콘텐츠 출력
            st.subheader("스크래핑된 텍스트 콘텐츠:")
            st.text(page_text)

        except requests.exceptions.RequestException as e:
            st.error(f"요청 중 오류가 발생했습니다: {e}")
    else:
        st.error("유효한 URL을 입력하세요.")
