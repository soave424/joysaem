import streamlit as st
import requests

# Streamlit 앱 제목
st.title("URL에서 페이지 소스 가져오기")

# URL 입력 받기
url = st.text_input("URL을 입력하세요:")

# 사용자가 URL을 입력하고 버튼을 누르면 실행
if st.button("페이지 소스 가져오기"):
    if url:
        try:
            # 웹 페이지의 HTML 소스를 가져오기
            response = requests.get(url)
            response.encoding = response.apparent_encoding  # 인코딩 처리

            # 페이지 소스를 텍스트로 출력
            st.text_area("페이지 소스", response.text, height=400)

        except Exception as e:
            st.error(f"페이지 소스를 가져오는 중 오류가 발생했습니다: {e}")
    else:
        st.error("유효한 URL을 입력하세요.")
