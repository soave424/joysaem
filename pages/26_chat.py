import streamlit as st
import openai

st.set_page_config(page_title="Chat with GPT")
st.title("💬 GPT-like Chat")

# 세션 상태에 대화 내역 저장
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]

# OpenAI API 키 설정
openai.api_key = st.secrets["openai_api_key"]

def query_gpt(messages):
    resp = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    return resp.choices[0].message.content

# 사용자 입력
user_input = st.chat_input("메시지를 입력하세요…")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.spinner("GPT가 생각 중…"):
        assistant_reply = query_gpt(st.session_state.messages)
    st.session_state.messages.append({"role": "assistant", "content": assistant_reply})

# 메시지 렌더링
for msg in st.session_state.messages[1:]:
    st.chat_message(msg["role"]).write(msg["content"])
