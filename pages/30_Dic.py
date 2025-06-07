import streamlit as st
import requests
import json

# ✅ 페이지 설정
st.set_page_config(page_title="표준국어대사전 검색", layout="wide")

# ✅ 인증 키 설정
API_KEY = st.secrets["Dic_API_Key"]
API_URL = "https://stdict.korean.go.kr/api/search.do"

# ✅ 사용자 입력 받기
st.title("📚 표준국어대사전 검색")
search_word = st.text_input("검색어를 입력하세요:", "나무")

if search_word:
    # ✅ 요청 파라미터 구성
    params = {
        "key": API_KEY,
        "q": search_word,
        "req_type": "json",
        "num": 5
    }

    # ✅ API 요청
    response = requests.get(API_URL, params=params)

    # ✅ 에러 처리
    if response.status_code != 200:
        st.error("API 요청 실패. 상태 코드: " + str(response.status_code))
    else:
        data = response.json()

        if "error" in data:
            st.error(f"에러 코드: {data['error']['error_code']}\n메시지: {data['error']['message']}")
        elif "channel" in data and "item" in data["channel"]:
            st.subheader(f"🔍 '{search_word}' 검색 결과")
            for item in data["channel"]["item"]:
                st.markdown(f"### {item['word']} ({item['pos']})")
                st.markdown(f"- **뜻풀이:** {item['sense']['definition']}")
                st.markdown(f"- [사전 보기 링크]({item['sense']['link']})")
                st.markdown("---")
        else:
            st.warning("검색 결과가 없습니다.")
