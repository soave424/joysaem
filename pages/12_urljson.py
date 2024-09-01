import streamlit as st
import requests
from bs4 import BeautifulSoup

# Streamlit 앱 제목
st.title("URL에서 li 요소를 추출하여 JSON으로 변환")

# URL 입력 받기
url = st.text_input("URL을 입력하세요:")

# 사용자가 URL을 입력하고 버튼을 누르면 실행
if st.button("스크래핑 시작"):
    if url:
        try:
            # 웹 페이지의 HTML을 가져오기
            response = requests.get(url)
            response.encoding = response.apparent_encoding  # 인코딩 처리

            # BeautifulSoup으로 HTML 파싱
            soup = BeautifulSoup(response.text, 'html.parser')

            # ul 또는 ol 요소 안의 li 요소들을 추출
            list_data = {}
            for ul in soup.find_all(['ul', 'ol']):
                list_name = ul.get('class', ['unnamed-list'])[0]
                items = [li.get_text(strip=True) for li in ul.find_all('li')]
                list_data[list_name] = items

            # 결과를 JSON 형태로 변환하여 출력
            st.json(list_data)

        except Exception as e:
            st.error(f"스크래핑 중 오류가 발생했습니다: {e}")
    else:
        st.error("유효한 URL을 입력하세요.")
