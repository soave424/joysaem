import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# Streamlit 앱 제목
st.title("JavaScript 로드 후 페이지 소스 가져오기")

# URL 입력 받기
url = st.text_input("URL을 입력하세요:")

if st.button("페이지 소스 가져오기"):
    if url:
        try:
            # Chrome WebDriver 설정
            service = Service(ChromeDriverManager().install())
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')  # 브라우저 창을 띄우지 않음
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')

            # WebDriver 실행
            driver = webdriver.Chrome(service=service, options=options)
            driver.get(url)

            # 페이지가 로드될 때까지 대기
            driver.implicitly_wait(10)

            # 페이지 소스 가져오기
            page_source = driver.page_source

            # 페이지 소스를 화면에 출력
            st.text_area("페이지 소스", page_source, height=400)

            # WebDriver 종료
            driver.quit()

        except Exception as e:
            st.error(f"페이지 소스를 가져오는 중 오류가 발생했습니다: {e}")
    else:
        st.error("유효한 URL을 입력하세요.")
