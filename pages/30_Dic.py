import streamlit as st
import requests

# 기본 설정
st.title("📚 표준국어대사전 검색")
API_KEY = st.secrets["Dic_API_Key"]
API_URL = "https://stdict.korean.go.kr/api/search.do"

query = st.text_input("검색어를 입력하세요:", "")

if query:
    params = {
        "key": API_KEY,
        "q": query,
        "req_type": "json",
        "num": 5
    }

    response = requests.get(API_URL, params=params)

    if response.status_code != 200:
        st.error(f"❌ 요청 실패: 상태 코드 {response.status_code}")
        st.code(response.text)
    else:
        try:
            data = response.json()
            if "error" in data:
                st.error(f"⚠️ 에러 코드 {data['error']['error_code']}: {data['error']['message']}")
            elif "channel" in data and "item" in data["channel"]:
                st.success(f"🔍 '{query}' 검색 결과:")
                for item in data["channel"]["item"]:
                    st.markdown(f"### {item['word']} ({item['pos']})")
                    st.markdown(f"뜻: {item['sense']['definition']}")
                    st.markdown(f"[자세히 보기]({item['sense']['link']})")
                    st.markdown("---")
            else:
                st.warning("결과가 없습니다.")
        except requests.exceptions.JSONDecodeError:
            st.error("⚠️ JSON 파싱 실패: 응답이 JSON 형식이 아닙니다.")
            st.code(response.text, language='xml')
