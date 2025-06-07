import streamlit as st
import requests
from urllib.parse import quote_plus
import xml.etree.ElementTree as ET

st.set_page_config(page_title="표준국어대사전 검색", layout="wide")
st.title("📚 표준국어대사전 검색")

API_KEY = st.secrets["Dic_API_Key"]
API_URL = "https://stdict.korean.go.kr/api/search.do"

query = st.text_input("검색어를 입력하세요:", "")

if query:
    with st.spinner("검색 중..."):
        params = {
            "key": API_KEY,
            "q": quote_plus(query),
            "req_type": "json",
            "num": 5
        }

        response = requests.get(API_URL, params=params)

        # 응답 원문 먼저 확인
        st.subheader("🔍 응답 원문 출력")
        st.code(response.text[:1000])  # 너무 길 경우 대비 1000자 제한

        if response.status_code != 200:
            st.error(f"❌ API 요청 실패: 상태 코드 {response.status_code}")
        else:
            try:
                data = response.json()
                st.success("✅ JSON 파싱 성공")
                st.write(data)
            except Exception as e:
                st.warning(f"⚠️ JSON 파싱 실패: {e}")
                try:
                    root = ET.fromstring(response.text)
                    st.success("✅ XML 파싱 성공")
                    for item in root.iter("item"):
                        word = item.findtext("word", "없음")
                        pos = item.findtext("pos", "없음")
                        definition = item.find("sense/definition").text if item.find("sense/definition") is not None else "정의 없음"
                        link = item.find("sense/link").text if item.find("sense/link") is not None else "#"
                        st.markdown(f"### {word} ({pos})")
                        st.markdown(f"- **뜻풀이:** {definition}")
                        st.markdown(f"- [사전 보기]({link})")
                        st.markdown("---")
                except Exception as ex:
                    st.error("❌ XML 파싱도 실패했습니다.")
                    st.code(response.text, language='html')
