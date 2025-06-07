import streamlit as st
import requests
from urllib.parse import quote_plus
from gtts import gTTS
import base64
import io

st.set_page_config(page_title="📚 표준국어대사전 검색 + TTS", layout="wide")
st.title("📚 표준국어대사전 검색")

API_KEY = st.secrets["Dic_API_Key"]
API_URL = "https://stdict.korean.go.kr/api/search.do"

query = st.text_input("검색어를 입력하세요:", "")

def play_tts(text):
    tts = gTTS(text=text, lang='ko')
    mp3_fp = io.BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    st.audio(mp3_fp.read(), format="audio/mp3")

if query:
    with st.spinner("🔍 검색 중..."):
        params = {
            "key": API_KEY,
            "q": quote_plus(query),
            "req_type": "json",
            "num": 10
        }

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

                    with st.expander(f"{idx}. {word} ({pos})"):
                        st.markdown(f"- **뜻풀이:** {definition}")
                        st.markdown(f"- [사전 링크 보기]({link})")
                        if st.button(f"🔊 {word} 뜻 듣기", key=f"tts_{idx}"):
                            play_tts(definition)
            else:
                st.warning("검색 결과가 없습니다.")
        except Exception as e:
            st.error(f"⚠️ 오류 발생: {e}")
            st.code(response.text)
