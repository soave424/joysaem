import streamlit as st
from streamlit.components.v1 import html
from openai import OpenAI

st.set_page_config(layout="wide", page_title="GPT 채팅 + 메모")
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]
if "memo" not in st.session_state:
    st.session_state.memo = ""

def query_gpt(text: str):
    st.session_state.messages.append({"role": "user", "content": text})
    resp = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=st.session_state.messages
    )
    st.session_state.messages.append({
        "role": "assistant",
        "content": resp.choices[0].message.content
    })

col1, col2 = st.columns([2, 1])
with col1:
    st.markdown("## 💬 대화창")

    # ★ 여기서 key를 "user_input"으로 변경
    user_input = st.text_input("메시지를 입력하세요…", key="user_input")
    if user_input:
        query_gpt(user_input)
        # ★ 세션 상태 초기화할 때도 동일한 key 사용
        st.session_state.user_input = ""

    # (이하 채팅 HTML/CSS/JS 부분은 이전 예제와 동일)
    chat_html = """…"""
    # … chat_html 빌드 생략 …
    html(chat_html, height=700)

with col2:
    st.markdown("## 📝 메모")
    memo_area = st.text_area(
        "여기에 메모를 자유롭게 작성하세요.", 
        value=st.session_state.memo, 
        height=600
    )
    if st.button("메모 저장"):
        st.session_state.memo = memo_area
        st.success("메모가 저장되었습니다!")
