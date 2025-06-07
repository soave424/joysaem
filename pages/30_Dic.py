import streamlit as st
import requests
from urllib.parse import quote_plus
import xml.etree.ElementTree as ET

# ✅ 페이지 설정
st.set_page_config(page_title="표준국어대사전 검색", layout="wide")
st.title("📚 표준국어대사전 검색")

# ✅ 필수 정보: API Key & URL
API_KEY = st.secrets["Dic_API_Key"]
API_URL = "https://stdict.korean.go.kr/api/search.do"

# ✅ 검색어 입력
query = st.text_input("검색어를 입력하세요:", "")

# ✅ 검색 요청
if query:
    with st.spinner("검색 중..."):
        params = {
            "key": API_KEY,
            "q": quote_plus(query),
            "req_type": "json",
            "num": 5
        }

        response = requests.get(API_URL, params=params)

        if response.status_code != 200:
            st.error(f"❌ API 요청 실패: 상태 코드 {response.status_code}")
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
                        st.markdown(f"- **뜻풀이:** {item['sense']['definition']}")
                        st.markdown(f"- [사전 보기]({item['sense']['link']})")
                        st.markdown("---")
                else:
                    st.warning("검색 결과가 없습니다.")
            except requests.exceptions.JSONDecodeError:
                st.warning("⚠️ JSON 파싱 실패: XML 응답일 수 있습니다. 원문을 확인하세요.")
                st.code(response.text, language="xml")

                # ✅ XML 파싱 백업
                try:
                    root = ET.fromstring(response.text)
                    error = root.find("error_code")
                    if error is not None:
                        code = root.find("error_code").text
                        msg = root.find("message").text
                        st.error(f"❌ XML 오류 코드 {code}: {msg}")
                    else:
                        st.info("🔎 XML 파싱 결과:")
                        for item in root.iter("item"):
                            word = item.findtext("word", "없음")
                            pos = item.findtext("pos", "없음")
                            definition = item.find("sense/definition").text if item.find("sense/definition") is not None else "정의 없음"
                            link = item.find("sense/link").text if item.find("sense/link") is not None else "#"
                            st.markdown(f"### {word} ({pos})")
                            st.markdown(f"- **뜻풀이:** {definition}")
                            st.markdown(f"- [사전 보기]({link})")
                            st.markdown("---")
                except Exception as e:
                    st.error("XML 파싱도 실패했습니다. 응답 내용을 직접 확인하세요.")
