import streamlit as st
from streamlit.components.v1 import html
from openai import OpenAI

# 페이지 넓게 설정
st.set_page_config(layout="wide", page_title="GPT 채팅 + 메모")
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]
if "memo" not in st.session_state:
    st.session_state["memo"] = ""

def query_gpt(text: str):
    st.session_state["messages"].append({"role": "user", "content": text})
    resp = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=st.session_state["messages"]
    )
    st.session_state["messages"].append({
        "role": "assistant",
        "content": resp.choices[0].message.content
    })

col1, col2 = st.columns([2, 1])
with col1:
    st.markdown("## 💬 대화창")

    # ▶ key를 user_input으로 지정
    user_input = st.text_input("메시지를 입력하세요…", key="user_input")
    if user_input:
        query_gpt(user_input)
        # ▶ 딕셔너리 방식으로 값 초기화
        st.session_state["user_input"] = ""

    # (HTML/CSS/JS 채팅창 부분은 이전 예제와 동일합니다)
    chat_html = """
    <style>
      .chat-container { padding:10px; }
      .message { margin: 8px 0; padding: 10px; border-radius: 8px; position: relative; max-width: 60%; word-wrap: break-word; }
      .user .message { background: #DCF8C6; margin-left: 40%; text-align: right; }
      .assistant .message { background: #F1F0F0; margin-right: 40%; text-align: left; }
      .copy-btn { position: absolute; top: 4px; right: 8px; background:none; border:none; cursor:pointer; font-size:0.8em; color:#666; }
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
        msgs.forEach((m) => { all += m.innerText + '\\n\\n'; });
        navigator.clipboard.writeText(all);
      }
    </script>
    <div class="chat-container">
    """

    for i, msg in enumerate(st.session_state["messages"][1:], start=1):
        cls = "user" if msg["role"] == "user" else "assistant"
        safe_id = f"msg_{i}"
        content = msg["content"].replace("\n", "<br>")
        chat_html += f'''
          <div class="{cls}">
            <div id="{safe_id}" class="message">{content}</div>
            <button class="copy-btn" onclick="copyText('{safe_id}')">📋</button>
          </div>
        '''

    chat_html += '''
      <button class="copy-all" onclick="copyAll()">Copy All</button>
    </div>
    '''
    html(chat_html, height=700)

with col2:
    st.markdown("## 📝 메모")
    memo_area = st.text_area(
        "여기에 메모를 자유롭게 작성하세요.", 
        value=st.session_state["memo"], 
        height=600
    )
    if st.button("메모 저장"):
        st.session_state["memo"] = memo_area
        st.success("메모가 저장되었습니다!")
