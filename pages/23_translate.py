import streamlit as st
import deepl

# Streamlit에 설정된 API 키
auth_key = st.secrets["DeepL_API_Key"]
translator = deepl.Translator(auth_key)

st.title("📘 단어/문장 번역기")
st.markdown("입력한 단어 또는 문장을 DeepL API를 이용해 번역해드립니다.")

# 사용자 입력
text = st.text_area("번역할 내용을 입력하세요:", height=150, placeholder="예: Artificial Intelligence is changing the world.")

# 번역 언어 선택 (정확한 지역 코드 사용)
lang_map = {
    "한국어 (Korean)": "KO",
    "영어 (미국식, EN-US)": "EN-US",
    "영어 (영국식, EN-GB)": "EN-GB",
    "일본어 (Japanese)": "JA",
    "중국어 (Chinese)": "ZH",
    "프랑스어 (French)": "FR",
    "독일어 (German)": "DE"
}
target_lang_label = st.selectbox("번역할 언어를 선택하세요:", list(lang_map.keys()))
target_lang = lang_map[target_lang_label]

# 번역 실행
if st.button("번역하기") and text:
    try:
        result = translator.translate_text(text, target_lang=target_lang)
        st.subheader("✅ 번역 결과")
        st.success(result.text)
    except Exception as e:
        st.error(f"오류가 발생했습니다: {e}")
