import streamlit as st
import requests
from bs4 import BeautifulSoup

# Streamlit 앱 제목
st.title("URL에서 HTML 요소와 텍스트를 스크래핑하여 JSON으로 변환")

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

            # HTML 전체 내용을 스크래핑하여 JSON으로 변환
            page_content = {
                "title": soup.title.string if soup.title else "No title",
                "meta_description": soup.find('meta', attrs={'name': 'description'}).get('content', '') if soup.find('meta', attrs={'name': 'description'}) else "No description",
                "h1_tags": [h1.get_text(strip=True) for h1 in soup.find_all('h1')],
                "paragraphs": [p.get_text(strip=True) for p in soup.find_all('p')],
                "links": [{"text": a.get_text(strip=True), "href": a.get('href')} for a in soup.find_all('a')]
            }

            # 결과를 JSON 형태로 변환하여 출력
            st.json(page_content)

        except Exception as e:
            st.error(f"스크래핑 중 오류가 발생했습니다: {e}")
    else:
        st.error("유효한 URL을 입력하세요.")
