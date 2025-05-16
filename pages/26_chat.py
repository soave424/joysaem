import streamlit as st
import xml.etree.ElementTree as ET
from openai import OpenAI

import streamlit as st
from streamlit.components.v1 import html



st.set_page_config(layout="wide")
st.title("💬 Custom GPT-like Chat")

# --- 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]

OpenAI.api_key =st.secrets["OPENAI_API_KEY"]

def query_gpt(user_input):
    st.session_state.messages.append({"role": "user", "content": user_input})
    resp = OpenAI.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=st.session_state.messages
    )
    assistant_reply = resp.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": assistant_reply})

# --- 사용자 입력
user_input = st.text_input("메시지를 입력하세요…", key="input")
if user_input:
    query_gpt(user_input)
    st.session_state.input = ""  # 입력창 초기화

# --- CSS + JS 삽입
chat_html = """
<style>
  .chat-container { padding:10px; }
  .message { display: block; margin: 8px 0; padding: 10px; border-radius: 8px; position: relative; max-width: 60%; word-wrap: break-word; }
  .user { text-align: right; }
  .user .message { background: #DCF8C6; margin-left: 40%; }
  .assistant { text-align: left; }
  .assistant .message { background: #F1F0F0; margin-right: 40%; }
  .copy-btn { position: absolute; top: 4px; right: 8px; border:none; background:none; cursor:pointer; font-size:0.8em; color:#666; }
  .copy-all { position: fixed; bottom: 20px; right: 20px; padding:8px 12px; border-radius:4px; background:#4CAF50; color:white; border:none; cursor:pointer; }
</style>

<script>
  function copyText(id){
    const txt = document.getElementById(id).innerText;
    navigator.clipboard.writeText(txt);
  }
  function copyAll(){
    const msgs = document.querySelectorAll('.message');
    let all = '';
    msgs.forEach((m,i) => {
      all += m.innerText + '\\n\\n';
    });
    navigator.clipboard.writeText(all);
  }
</script>

<div class="chat-container">
"""

# 각 메시지 블럭 생성
for i, msg in enumerate(st.session_state.messages[1:], start=1):
    cls = "user" if msg["role"]=="user" else "assistant"
    safe_id = f"msg_{i}"
    text = msg["content"].replace("\n", "<br>")  # 줄바꿈 유지
    chat_html += f'''
      <div class="{cls}">
        <div id="{safe_id}" class="message">{text}</div>
        <button class="copy-btn" onclick="copyText('{safe_id}')">📋</button>
      </div>
    '''

# 전체 복사 버튼
chat_html += '''
  <button class="copy-all" onclick="copyAll()">Copy All</button>
</div>
'''

html(chat_html, height=600)

