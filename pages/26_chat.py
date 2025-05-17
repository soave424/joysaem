# app.py
import streamlit as st
from openai import OpenAI
from streamlit.components.v1 import html
import json

st.set_page_config(layout="wide", page_title="대화 및 메모 앱")
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# 세션 초기화
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "notes" not in st.session_state:
    st.session_state["notes"] = {}

def query_gpt(user_text: str):
    msgs = [{"role": "system", "content": "You are a helpful assistant."}]
    for m in st.session_state["messages"]:
        msgs += [
            {"role": "user", "content": m["user"]},
            {"role": "assistant", "content": m["ai"]},
        ]
    msgs.append({"role": "user", "content": user_text})
    resp = client.chat.completions.create(model="gpt-3.5-turbo", messages=msgs)
    st.session_state["messages"].append({
        "user": user_text,
        "ai": resp.choices[0].message.content
    })

# ▶ 고유 placeholder 지정
hidden_input = st.text_input(
    label="", key="in",
    placeholder="__HIDDEN_INPUT__", label_visibility="collapsed"
)
if hidden_input:
    query_gpt(hidden_input)
    st.session_state["in"] = ""

# 대화 + 메모 직렬화
data = {
    "conversations": [
        {
            "id": idx,
            "user": conv["user"],
            "ai": conv["ai"],
            "notes": st.session_state["notes"].get(str(idx), "")
        }
        for idx, conv in enumerate(st.session_state["messages"], start=1)
    ]
}
data_json = json.dumps(data)

# ▶ HTML/JS
html_content = '''
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    .custom-scrollbar::-webkit-scrollbar { width:8px }
    .custom-scrollbar::-webkit-scrollbar-track { background:#f1f1f1;border-radius:10px }
    .custom-scrollbar::-webkit-scrollbar-thumb { background:#888;border-radius:10px }
    .custom-scrollbar::-webkit-scrollbar-thumb:hover { background:#555 }
    .chat-block.selected { background:#e0f2fe;border-left:4px solid #0ea5e9 }
  </style>
</head>
<body class="bg-gray-50">
  <div class="container mx-auto max-w-6xl p-4 h-screen flex flex-col md:flex-row gap-4">
    <div class="chat-pane w-full md:w-2/3 bg-white shadow rounded-lg p-4 flex flex-col h-full relative">
      <h1 class="text-2xl font-bold mb-4 text-center text-blue-600">대화 기록</h1>
      <div id="chatHistory" class="flex-grow overflow-y-auto custom-scrollbar mb-4 p-2 border rounded bg-gray-50"></div>
      <div class="absolute bottom-4 left-4 right-4 flex gap-2">
        <input id="userInput" type="text"
          class="flex-grow border border-gray-300 rounded-lg p-3 focus:ring-2 focus:ring-blue-500 outline-none"
          placeholder="메시지를 입력하세요...">
        <button id="sendButton"
          class="bg-blue-500 hover:bg-blue-600 text-white font-semibold p-3 rounded-lg transition">
          전송
        </button>
      </div>
    </div>
    <div class="notes-pane w-full md:w-1/3 bg-white shadow rounded-lg p-6 flex flex-col">
      <h2 id="notesTitle" class="text-2xl font-bold mb-4 text-center text-green-600">나의 생각</h2>
      <div id="notesPlaceholder"
           class="flex-grow flex items-center justify-center text-gray-500 text-center">
        <p>왼쪽 대화 블록을 클릭하여<br>메모를 작성하세요.</p>
      </div>
      <div id="notesEditor" class="hidden flex-grow flex flex-col">
        <textarea id="notesTextarea"
          class="w-full flex-grow p-3 border border-gray-300 rounded-lg mb-4 focus:ring-2 focus:ring-green-500 outline-none resize-none custom-scrollbar"
          placeholder="대화에 대한 생각을 입력하세요..."></textarea>
        <button id="saveNoteButton"
          class="bg-green-500 hover:bg-green-600 text-white font-semibold p-3 rounded-lg self-end">
          메모 저장
        </button>
        <p id="saveStatus" class="text-sm text-green-700 mt-2 h-5 text-right"></p>
      </div>
    </div>
  </div>

  <script>
    const data = JSON.parse(''' + repr(data_json) + ''');
    let selectedConversationId = null;

    const chatHistory = document.getElementById('chatHistory');
    const userInput = document.getElementById('userInput');
    const sendButton = document.getElementById('sendButton');
    const notesTitle = document.getElementById('notesTitle');
    const notesPlaceholder = document.getElementById('notesPlaceholder');
    const notesEditor = document.getElementById('notesEditor');
    const notesTextarea = document.getElementById('notesTextarea');
    const saveNoteButton = document.getElementById('saveNoteButton');
    const saveStatus = document.getElementById('saveStatus');

    function renderChat() {
      chatHistory.innerHTML = '';
      if (!data.conversations.length) {
        chatHistory.innerHTML = '<p class="text-gray-400 text-center p-4">대화가 없습니다.</p>';
        return;
      }
      data.conversations.forEach(conv => {
        const block = document.createElement('div');
        block.className = 'chat-block p-3 mb-2 border rounded cursor-pointer hover:bg-gray-100 ' +
                          (conv.id === selectedConversationId ? 'selected' : '');
        block.dataset.id = conv.id;
        const u = document.createElement('p');
        u.className = 'font-semibold text-blue-700'; u.textContent = '나: ' + conv.user;
        const a = document.createElement('p');
        a.className = 'text-green-700 mt-1'; a.textContent = 'AI: ' + conv.ai;
        block.append(u, a);
        block.addEventListener('click', () => {
          selectedConversationId = conv.id; renderChat(); showNotes(conv);
        });
        chatHistory.append(block);
      });
      chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    function showNotes(conv) {
      notesPlaceholder.classList.add('hidden');
      notesEditor.classList.remove('hidden');
      notesTitle.textContent = `대화 #${conv.id}에 대한 메모`;
      notesTextarea.value = conv.notes;
      saveStatus.textContent = '';
    }

    function sendToPython() {
      const txt = userInput.value.trim();
      if (!txt) return;
      // ▶ placeholder 로 찾기
      const hidden = document.querySelector('input[placeholder="__HIDDEN_INPUT__"]');
      hidden.value = txt;
      hidden.dispatchEvent(new Event('input', { bubbles: true }));
      hidden.dispatchEvent(new Event('change', { bubbles: true }));
      userInput.value = '';
    }

    function saveNote() {
      if (!selectedConversationId) return;
      const idx = data.conversations.findIndex(c => c.id === selectedConversationId);
      data.conversations[idx].notes = notesTextarea.value;
      saveStatus.textContent = '저장되었습니다!';
      setTimeout(() => saveStatus.textContent = '', 2000);
    }

    sendButton.addEventListener('click', sendToPython);
    userInput.addEventListener('keypress', e => { if (e.key==='Enter') sendToPython(); });
    saveNoteButton.addEventListener('click', saveNote);

    document.addEventListener('DOMContentLoaded', renderChat);
  </script>
</body>
</html>
'''
html(html_content, height=800)
