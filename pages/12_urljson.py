import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# Streamlit 앱 제목
st.title("JavaScript 렌더링 웹페이지 스크래핑 도구")

# URL 입력 받기
url = st.text_input("URL을 입력하세요:")

# 사용자가 URL을 입력하고 버튼을 누르면 실행
if st.button("스크래핑 시작"):
    if url:
        try:
            # Selenium WebDriver 설정
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # 브라우저 창을 띄우지 않고 실행
            chrome_options.add_argument("--disable-gpu")  # GPU 비활성화 (리소스 절약)
            chrome_options.add_argument("--no-sandbox")  # 샌드박스 모드 비활성화 (리눅스 호환성)
            chrome_options.add_argument("--disable-dev-shm-usage")  # /dev/shm 사용 비활성화 (리눅스 호환성)

            # WebDriver 설치 및 실행
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
            
            # 입력된 URL로 이동
            driver.get(url)

            # 페이지가 완전히 로드될 때까지 대기
            driver.implicitly_wait(10)

            # 페이지의 HTML을 가져옴
            page_source = driver.page_source

            # BeautifulSoup을 사용하여 HTML 파싱
            soup = BeautifulSoup(page_source, 'html.parser')

            # 페이지의 텍스트 콘텐츠 추출
            page_text = soup.get_text()

            # 페이지의 HTML 콘텐츠 출력
            st.subheader("스크래핑된 HTML 콘텐츠:")
            st.code(soup.prettify(), language='html')

            # 페이지의 텍스트 콘텐츠 출력
            st.subheader("스크래핑된 텍스트 콘텐츠:")
            st.text(page_text)

            # WebDriver 종료
            driver.quit()

        except Exception as e:
            st.error(f"스크래핑 중 오류가 발생했습니다: {e}")
    else:
        st.error("유효한 URL을 입력하세요.")
