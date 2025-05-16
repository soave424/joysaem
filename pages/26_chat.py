import streamlit as st
import xml.etree.ElementTree as ET
from openai import OpenAI

# 1) 시크릿에 저장한 키 불러오기
api_key = st.secrets["OPENAI_API_KEY"]

# 2) 최신 OpenAI 클라이언트 인스턴스 생성
client = OpenAI(api_key=api_key)

# 3) 메시지 이력 초기화
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "당신은 친절한 도우미입니다."}
    ]

st.title("💬 GPT와 대화")

# 사용자 입력
user_input = st.text_input("메시지를 입력하세요", "")
if st.button("전송") and user_input:
    # 4) 대화 이력에 추가
    st.session_state.messages.append({"role": "user", "content": user_input})

    # 5) ChatCompletion 호출 (구버전 메서드가 아니라 이렇게!)
    resp = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=st.session_state.messages
    )

    # 6) 어시스턴트 응답
    assistant_reply = resp.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": assistant_reply})

# 7) 화면에 대화 이력 표시
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"**You:** {msg['content']}")
    elif msg["role"] == "assistant":
        st.markdown(f"**GPT:** {msg['content']}")
