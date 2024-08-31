import streamlit as st
import requests
from bs4 import BeautifulSoup
import json

def url_to_json(url):
    try:
        response = requests.get(url)
        response.raise_for_status()

        # 인코딩을 'utf-8'로 설정
        response.encoding = response.apparent_encoding

        soup = BeautifulSoup(response.text, 'html.parser')

        # 웹 페이지의 title, meta description, 그리고 모든 h1 태그의 내용을 추출하여 JSON으로 변환
        page_data = {
            "title": soup.title.string if soup.title else "No title found",
            "meta_description": soup.find("meta", {"name": "description"})["content"] if soup.find("meta", {"name": "description"}) else "No description found",
            "h1_tags": [h1.get_text().strip() for h1 in soup.find_all("h1")]
        }

        return json.dumps(page_data, indent=4, ensure_ascii=False)
    
    except requests.exceptions.RequestException as e:
        return json.dumps({"error": str(e)}, indent=4, ensure_ascii=False)

st.title("URL을 입력하여 웹사이트 정보를 JSON 형식으로 확인하기")

# URL 입력
url = st.text_input("웹사이트 URL을 입력하세요:")

if st.button("정보 가져오기"):
    if url:
        json_data = url_to_json(url)
        st.text_area("웹사이트 정보 (JSON):", json_data, height=300)
    else:
        st.error("URL을 입력하세요.")
