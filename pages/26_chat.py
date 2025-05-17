# app.py
import streamlit as st
from openai import OpenAI
from streamlit.components.v1 import html
import json

# ─── 페이지 설정 ───────────────────────────────────────
st.set_page_config(layout="wide", page_title="Chat & Notes")

# ─── OpenAI 클라이언트 초기화 ─────────────────────────
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ─── 세션 상태 초기화 ─────────────────────────────────
if "messages" not in st.session_state:
    st.session_state["messages"] = []       # List[{"role": str, "content": str}]
if "notes" not in st.session_state:
    st.session_state["notes"] = {}          # Dict[int, str]
if "selected" not in st.session_state:
    st.session_state["selected"] = None     # int or None

# ─── GPT 질의 함수 ─────────────────────────────────────
def query_gpt(text: str):
    # system + 기존 대화 + 새로운 질문
    convo = [{"role":"system","content":"You are a helpful assistant."}] + st.session_state["messages"]
    convo.append({"role":"user","content":text})
    resp = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=convo
    )
    # 사용자 메시지와 GPT 응답을 차례로 저장
    st.session_state["messages"].append({"role":"user",      "content": text})
    st.session_state["messages"].append({"role":"assistant", "content": resp.choices[0].message.content})

# ─── 숨은 입력 필드 (new 메시지, selected id) ─────────
inp = st.text_input("", key="in",  placeholder="__IN__",  label_visibility="collapsed")
sel = st.text_input("", key="sel", placeholder="__SEL__", label_visibility="collapsed")

if inp:
    query_gpt(inp)
    st.session_state["in"] = ""

if sel:
    try:
        st.session_state["selected"] = int(sel)
    except:
        st.session_state["selected"] = None
    st.session_state["sel"] = ""

# ─── 대화 내역 JSON 직렬화 ─────────────────────────────
data = {
    "conversations": [
        {"id": i+1, "role": m["role"], "content": m["content"]}
        for i, m in enumerate(st.session_state["messages"])
    ]
}
data_json = json.dumps(data)

# ─── 레이아웃: 좌측(2) 채팅, 우측(1) 메모 ─────────────────
col1, col2 = st.columns([2,1])

with col1:
    html_code = '''
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
      /* 전체 높이, 스크롤바, 입력창 고정 */
      .chat-pane { height:100vh; position:relative; }
      .custom-scrollbar::-webkit-scrollbar { width:8px }
      .custom-scrollbar::-webkit-scrollbar-thumb { background:#888;border-radius:10px }
      .chat-input { position:absolute; bottom:1rem; left:1rem; right:1rem; display:flex; gap:0.5rem; }
      /* 블럭 스타일 */
      .chat-block { padding:0.75rem; margin-bottom:0.5rem; border-radius:0.5rem; position:relative; cursor:pointer; }
      .chat-block.user      { background:#DCF8C6; margin-left:30%; text-align:right; }
      .chat-block.assistant { background:#F1F0F0; margin-right:30%; text-align:left; }
      /* 복사 버튼 */
      .copy-btn { position:absolute; top:0.25rem; right:0.5rem; background:none; border:none; cursor:pointer; font-size:0.9em; }
      /* 전체 복사 버튼 */
      .copy-all { position:fixed; bottom:1rem; right:1rem; padding:0.5rem 1rem;
                  background:#4CAF50; color:white; border:none; border-radius:0.25rem; cursor:pointer; }
      .copy-all:hover { background:#43A047; }
    </style>

    <div class="chat-pane bg-white p-4 overflow-hidden">
      <div id="history" class="custom-scrollbar overflow-y-auto" style="height:calc(100vh - 4rem);"></div>
      <div class="chat-input">
        <input id="uinput" type="text" class="flex-grow border rounded p-2 focus:ring-2 focus:ring-blue-500" placeholder="메시지를 입력하세요…" />
        <button id="sendBtn" class="bg-blue-500 text-white px-4 rounded">전송</button>
      </div>
      <button id="copyAll" class="copy-all">Copy All</button>
    </div>

    <script>
      const data = JSON.parse(''' + repr(data_json) + ''');
      const hist = document.getElementById("history");
      const uin = document.getElementById("uinput");
      const sendBtn = document.getElementById("sendBtn");
      const copyAll = document.getElementById("copyAll");

      // 대화 렌더링
      function render(){
        hist.innerHTML="";
        data.conversations.forEach(c=>{
          const div = document.createElement("div");
          div.className = "chat-block " + c.role;
          div.id = "msg"+c.id;
          div.innerText = c.content;
          // 개별 복사 버튼
          const btn = document.createElement("button");
          btn.className="copy-btn"; btn.innerText="📋";
          btn.onclick = e => { e.stopPropagation(); navigator.clipboard.writeText(c.content); };
          div.append(btn);
          // 클릭 시 선택 id 전달
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

      // 전송 처리
      sendBtn.onclick = ()=>{
        const v = uin.value.trim();
        if(!v) return;
        const inp = document.querySelector('input[placeholder="__IN__"]');
        inp.value = v;
        inp.dispatchEvent(new Event("input",{bubbles:true}));
        uin.value="";
      };
      uin.addEventListener("keypress", e=>{ if(e.key==="Enter") sendBtn.onclick(); });

      // 전체 복사 처리
      copyAll.onclick = ()=>{
        const all = data.conversations.map(c=>c.content).join("\\n\\n");
        navigator.clipboard.writeText(all);
      };
    </script>
    '''
    html(html_code, height=700)

with col2:
    st.header("📝 메모")
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

