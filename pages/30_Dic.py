import streamlit as st
import requests
from urllib.parse import quote_plus

# ✅ 페이지 설정
st.set_page_config(page_title="📚 표준국어대사전 검색", layout="wide")
st.title("📚 표준국어대사전 검색")

# ✅ API 설정
API_KEY = st.secrets["Dic_API_Key"]
API_URL = "https://stdict.korean.go.kr/api/search.do"

# ✅ 검색어 입력
query = st.text_input("검색어를 입력하세요:", "")

if query:
    with st.spinner("🔍 검색 중..."):
        params = {
            "key": API_KEY,
            "q": quote_plus(query),
            "req_type": "json",
            "num": 10
        }

        try:
            response = requests.get(API_URL, params=params)

            try:
                data = response.json()
                if "channel" in data and "item" in data["channel"]:
                    st.success(f"'{query}'에 대한 검색 결과 {data['channel']['total']}건")
                    for idx, item in enumerate(data["channel"]["item"], 1):
                        word = item.get("word", "알 수 없음")
                        pos = item.get("pos", "품사 없음")
                        definition = item["sense"].get("definition", "뜻 없음")
                        link = item["sense"].get("link", "#")

                        st.markdown(f"""
                        <h4>{idx}. <a href='{link}' target='_blank'>{word} ({pos})</a></h4>
                        <p>- {definition}</p>
                        <hr>
                        """, unsafe_allow_html=True)
                else:
                    st.warning("검색 결과가 없습니다.")
            except Exception as json_error:
                st.warning(f"⚠️ JSON 파싱 실패: {json_error}")
                st.code(response.text)
        except Exception as err:
            st.error(f"❌ 요청 중 오류 발생: {err}")
