import streamlit as st
from openai import OpenAI
from streamlit.components.v1 import html
import json

st.set_page_config(layout="wide", page_title="Chat & Notes")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ─── 세션 스테이트 초기화 & 마이그레이션 ─────────────────
if "messages" not in st.session_state:
    st.session_state["messages"] = []
else:
    # ✂️ migrate old-format messages (user/ai) → new-format (role/content)
    migrated = []
    for msg in st.session_state["messages"]:
        if "role" in msg and "content" in msg:
            # 이미 올바른 구조
            migrated.append(msg)
        elif "user" in msg and "ai" in msg:
            # 이전 구조라면 두 개의 메시지로 분리
            migrated.append({"role": "user",      "content": msg["user"]})
            migrated.append({"role": "assistant", "content": msg["ai"]})
        # else: 알 수 없는 포맷은 무시
    st.session_state["messages"] = migrated

if "notes" not in st.session_state:
    st.session_state["notes"] = {}

# ─── GPT 호출 함수 ─────────────────────────────────────
def query_gpt(user_text: str):
    convo = [{"role":"system","content":"You are a helpful assistant."}]
    convo += [{"role":m["role"], "content":m["content"]} 
              for m in st.session_state["messages"]]
    convo.append({"role":"user","content":user_text})
    res = client.chat.completions.create(model="gpt-3.5-turbo", messages=convo)
    st.session_state["messages"].append({"role":"user",      "content":user_text})
    st.session_state["messages"].append({"role":"assistant", "content":res.choices[0].message.content})

# ─── 숨은 입력 필드 & 처리 ───────────────────────────────
hidden = st.text_input("", key="in", placeholder="__HIDDEN__", label_visibility="collapsed")
if hidden:
    query_gpt(hidden)
    st.session_state["in"] = ""

# ─── JSON 직렬화 ───────────────────────────────────────
data = {"conversations": [
    {"id": idx, "user": m["content"]}  # 메모 기능만 남겨두고...
    for idx, m in enumerate(st.session_state["messages"], start=1)
]}
data_json = json.dumps(data)

# ─── (이하 HTML/Tailwind 로 채팅+메모 UI 삽입) ─────────
html_content = '''
<!-- ... (생략: 이전에 사용하셨던 HTML/JS 템플릿) ... -->
'''
html(html_content, height=800)
