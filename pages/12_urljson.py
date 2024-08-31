import streamlit as st
import requests
from bs4 import BeautifulSoup
import json

# URL 입력 받기
st.title("LI 요소 추출기")
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

            # 모든 ul 또는 ol 요소를 찾음
            lists = soup.find_all(['ul', 'ol'])

            # 결과를 저장할 딕셔너리
            result = {}

            for list_tag in lists:
                # 클래스명 또는 id를 가져옴
                title = list_tag.get('class', list_tag.get('id', 'unnamed_list'))

                if isinstance(title, list):
                    title = ' '.join(title)
                elif not title:
                    title = 'unnamed_list'

                # li 요소의 텍스트를 리스트로 저장
                li_elements = list_tag.find_all('li')
                li_texts = [li.get_text(strip=True) for li in li_elements]

                # 결과 딕셔너리에 저장
                result[title] = li_texts

            # JSON 형식으로 변환
            json_output = json.dumps(result, ensure_ascii=False, indent=4)

            # 결과 출력
            st.json(json_output)

        except requests.exceptions.RequestException as e:
            st.error(f"요청 중 오류가 발생했습니다: {e}")
    else:
        st.error("유효한 URL을 입력하세요.")
