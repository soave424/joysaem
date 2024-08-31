import streamlit as st
import requests
from bs4 import BeautifulSoup
import json

# URL 입력 받기
st.title("UL-LI 요소 추출기")
url = st.text_input("URL을 입력하세요:")

# 사용자가 URL을 입력하고 버튼을 누르면 실행
if st.button("추출"):
    if url:
        try:
            # URL의 HTML을 가져옴
            response = requests.get(url)
            response.raise_for_status()  # 요청 실패 시 에러 발생

            # BeautifulSoup을 사용하여 HTML 파싱
            soup = BeautifulSoup(response.text, 'html.parser')

            # ul 요소를 찾고 그 안의 li 요소들을 찾음
            ul_elements = soup.find_all('ul')
            all_li_elements = []

            for ul in ul_elements:
                li_elements = ul.find_all('li')
                for li in li_elements:
                    li_text = li.get_text(strip=True)
                    all_li_elements.append(li_text)

            # JSON 형식으로 변환
            json_output = json.dumps(all_li_elements, ensure_ascii=False, indent=4)

            # 결과 출력
            st.json(json_output)

        except requests.exceptions.RequestException as e:
            st.error(f"요청 중 오류가 발생했습니다: {e}")
    else:
        st.error("유효한 URL을 입력하세요.")
