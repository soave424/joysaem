# app.py
import streamlit as st
from openai import OpenAI
from streamlit.components.v1 import html
import json

# 페이지 설정
st.set_page_config(layout="wide", page_title="Chat & Notes")

# OpenAI 클라이언트
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state["messages"] = []       # List[{"role":str,"content":str}]
if "notes" not in st.session_state:
    st.session_state["notes"] = {}          # Dict[int,str]
if "selected" not in st.session_state:
    st.session_state["selected"] = None     # int

# GPT 호출
def query_gpt(text: str):
    convo = [{"role":"system","content":"You are a helpful assistant."}] + st.session_state["messages"]
    convo.append({"role":"user","content":text})
    resp = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=convo
    )
    st.session_state["messages"].append({"role":"user",      "content":text})
    st.session_state["messages"].append({"role":"assistant", "content":resp.choices[0].message.content})

# 숨은 입력 필드: __IN__ → 새 메시지, __SEL__ → 블럭 클릭 ID
inp = st.text_input("", key="in",  placeholder="__IN__",  label_visibility="collapsed")
sel = st.text_input("", key="sel", placeholder="__SEL__", label_visibility="collapsed")

if inp:
    query_gpt(inp)
    # 이전 방식(st.session_state["in"] = "") 대신 pop으로 제거
    st.session_state.pop("in", None)

if sel:
    try:
        st.session_state["selected"] = int(sel)
    except:
        st.session_state["selected"] = None
    # 이전 방식(st.session_state["sel"] = "") 대신 pop으로 제거
    st.session_state.pop("sel", None)

# 대화+노트를 JSON에 담기
data = {
    "conversations": [
        {
            "id": i+1,
            "role": m["role"],
            "content": m["content"],
            "notes": st.session_state["notes"].get(i+1, "")
        }
        for i, m in enumerate(st.session_state["messages"])
    ]
}
data_json = json.dumps(data)

# 좌측(2) / 우측(1) 레이아웃
col1, col2 = st.columns([2,1])

with col1:
    # 채팅 UI 전용 HTML/JS
    chat_html = '''
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
      .chat-pane { height:100vh; position:relative; }
      .custom-scrollbar::-webkit-scrollbar { width:8px }
      .custom-scrollbar::-webkit-scrollbar-thumb { background:#888;border-radius:10px }
      .chat-input { position:absolute; bottom:1rem; left:1rem; right:1rem; display:flex; gap:0.5rem; }
      .chat-block { padding:0.75rem; margin-bottom:0.5rem; border-radius:0.5rem; position:relative; cursor:pointer; }
      .chat-block.user      { background:#DCF8C6; margin-left:30%; text-align:right; }
      .chat-block.assistant { background:#F1F0F0; margin-right:30%; text-align:left; }
      .copy-btn { position:absolute; top:0.25rem; right:0.5rem; background:none; border:none; cursor:pointer; font-size:0.9em; }
    </style>
    <div class="chat-pane bg-white p-4 overflow-hidden">
      <div id="history" class="custom-scrollbar overflow-y-auto" style="height:calc(100vh - 4rem);"></div>
      <div class="chat-input">
        <input id="uinput" type="text" class="flex-grow border rounded p-2 focus:ring-2 focus:ring-blue-500" placeholder="메시지를 입력하세요…" />
        <button id="sendBtn" class="bg-blue-500 text-white px-4 rounded">전송</button>
      </div>
    </div>
    <script>
      const data = JSON.parse(''' + repr(data_json) + ''');
      const hist = document.getElementById("history");
      const uin = document.getElementById("uinput");
      const sendBtn = document.getElementById("sendBtn");

      function render(){
        hist.innerHTML="";
        data.conversations.forEach(c=>{
          const div = document.createElement("div");
          div.className = "chat-block " + c.role;
          div.id = "msg"+c.id;
          div.innerText = c.content;
          const btn = document.createElement("button");
          btn.className="copy-btn"; btn.innerText="📋";
          btn.onclick = e => { e.stopPropagation(); navigator.clipboard.writeText(c.content); };
          div.append(btn);
          div.onclick = ()=>{
            const sel = document.querySelector('input[placeholder="__SEL__"]');
            sel.value = c.id;
            sel.dispatchEvent(new Event("input",{bubbles:true}));
          };
          hist.append(div);
        });
        hist.scrollTop = hist.scrollHeight;
      }
      render();

      sendBtn.onclick = ()=>{
        const v = uin.value.trim();
        if(!v) return;
        const inp = document.querySelector('input[placeholder="__IN__"]');
        inp.value = v;
        inp.dispatchEvent(new Event("input",{bubbles:true}));
        uin.value="";
      };
      uin.addEventListener("keypress", e=>{ if(e.key==="Enter") sendBtn.onclick(); });
    </script>
    '''
    html(chat_html, height=700)

with col2:
    st.header("📝 Notes")
    # Copy All with Notes 버튼
    copy_notes_html = '''
    <style>
      .copy-all-notes { margin-bottom:0.5rem; padding:0.5rem 1rem; background:#4CAF50; color:white; border:none; border-radius:0.25rem; cursor:pointer; }
      .copy-all-notes:hover { background:#43A047; }
    </style>
    <button id="copyAllNotes" class="copy-all-notes">Copy All with Notes</button>
    <script>
      const data = JSON.parse(''' + repr(data_json) + ''');
      document.getElementById("copyAllNotes").onclick = () => {
        const all = data.conversations.map(c => {
          let line = (c.role==="user"?"User: ":"AI: ") + c.content;
          if (c.notes) line += "\\nNote: " + c.notes;
          return line;
        }).join("\\n\\n");
        navigator.clipboard.writeText(all);
      };
    </script>
    '''
    html(copy_notes_html)

    sid = st.session_state["selected"]
    if sid and 1 <= sid <= len(st.session_state["messages"]):
        st.subheader(f"대화 #{sid}")
        existing = st.session_state["notes"].get(sid, "")
        note = st.text_area("메모 입력", value=existing, height=200)
        if st.button("저장", key="save"):
            st.session_state["notes"][sid] = note
            st.success("저장되었습니다!")
    else:
        st.info("왼쪽 대화 블럭을 클릭하세요.")
