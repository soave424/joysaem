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

        try:
            response = requests.get(API_URL, params=params)
            st.text(f"응답 상태 코드: {response.status_code}")
            st.text(f"응답 Content-Length: {len(response.content)} bytes")
            st.text(f"🔑 실제 사용 중인 API Key: {API_KEY[:4]}****{API_KEY[-4:]}")
            st.subheader("🔍 응답 원문 출력")
            st.code(response.text or "<<응답 없음>>")

            try:
                data = response.json()
                st.success("✅ JSON 파싱 성공")
                st.write(data)
            except Exception as json_error:
                st.warning(f"⚠️ JSON 파싱 실패: {json_error}")
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
                except Exception as xml_error:
                    st.error(f"❌ XML 파싱도 실패했습니다: {xml_error}")
        except Exception as req_error:
            st.error(f"❌ 요청 중 오류 발생: {req_error}")
