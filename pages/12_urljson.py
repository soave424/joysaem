import streamlit as st
import requests
from bs4 import BeautifulSoup

def extract_element(url, selector):
    try:
        response = requests.get(url)
        response.raise_for_status()

        # 인코딩 설정
        response.encoding = response.apparent_encoding

        soup = BeautifulSoup(response.text, 'html.parser')

        # 지정된 CSS 선택자를 사용하여 요소를 추출
        element = soup.select_one(selector)
        if element:
            return element.prettify()  # 요소를 HTML 형식으로 반환
        else:
            return "선택자에 해당하는 요소를 찾을 수 없습니다."
    
    except requests.exceptions.RequestException as e:
        return f"에러 발생: {str(e)}"

st.title("웹 페이지에서 특정 요소 추출하기")

# URL 및 CSS 선택자 입력
url = st.text_input("웹사이트 URL을 입력하세요:")
selector = st.text_input("CSS 선택자를 입력하세요:", value="#content > article.sub-page-content.search-page.pb-xxl.mb-lg > div > div.result-area > div.inner.float-wrap.pt-md > div.result-content.fl-right > ul")

if st.button("요소 추출"):
    if url and selector:
        element_html = extract_element(url, selector)
        st.text_area("추출된 요소 (HTML):", element_html, height=300)
    else:
        st.error("URL 및 CSS 선택자를 모두 입력하세요.")
