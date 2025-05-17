import streamlit as st
from openai import OpenAI
from streamlit.components.v1 import html
import json

st.set_page_config(layout="wide", page_title="대화 및 메모 앱")
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# 세션 스테이트 초기화
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "notes" not in st.session_state:
    st.session_state["notes"] = {}

# GPT 호출 함수
def query_gpt(user_text):
    msgs = [{"role": "system", "content": "You are a helpful assistant."}]
    for m in st.session_state["messages"]:
        msgs.append({"role": "user", "content": m["user"]})
        msgs.append({"role": "assistant", "content": m["ai"]})
    msgs.append({"role": "user", "content": user_text})
    resp = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=msgs
    )
    st.session_state["messages"].append({
        "user": user_text,
        "ai": resp.choices[0].message.content
    })

# 입력 처리
user_input = st.text_input("메시지를 입력하세요…", key="in")
if user_input:
    query_gpt(user_input)
    # 입력 초기화
    st.session_state["in"] = ""

# JSON 직렬화
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

# HTML 콘텐츠를 일반 문자열 + JSON 문자열 결합으로 생성
html_content = '''
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>대화 및 메모 앱</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    .custom-scrollbar::-webkit-scrollbar { width: 8px; }
    .custom-scrollbar::-webkit-scrollbar-track { background: #f1f1f1; border-radius:10px; }
    .custom-scrollbar::-webkit-scrollbar-thumb { background: #888; border-radius:10px; }
    .custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #555; }
    .chat-block.selected {
      background-color: #e0f2fe;
      border-left-width: 4px;
      border-left-color: #0ea5e9;
    }
  </style>
</head>
<body class="bg-gray-50">
  <div class="container mx-auto max-w-6xl p-4 h-screen flex flex-col md:flex-row gap-4">
    <div class="chat-pane w-full md:w-2/3 bg-white shadow-lg rounded-lg p-4 flex flex-col">
      <h1 class="text-2xl font-bold mb-4 text-center text-blue-600">대화 기록</h1>
      <div id="chatHistory" class="chat-history flex-grow overflow-y-auto custom-scrollbar mb-4 p-2 border rounded-md bg-gray-50"></div>
      <div class="chat-input flex gap-2">
        <input type="text" id="userInput" class="flex-grow border border-gray-300 rounded-lg p-3 focus:ring-2 focus:ring-blue-500 outline-none" placeholder="메시지를 입력하세요...">
        <button id="sendButton" class="bg-blue-500 hover:bg-blue-600 text-white font-semibold p-3 rounded-lg transition-colors">전송</button>
      </div>
    </div>

    <div class="notes-pane w-full md:w-1/3 bg-white shadow-lg rounded-lg p-6 flex flex-col">
      <h2 id="notesTitle" class="text-2xl font-bold mb-4 text-center text-green-600">나의 생각</h2>
      <div id="notesPlaceholder" class="text-gray-500 text-center flex-grow flex items-center justify-center">
        <p>왼쪽 대화 블록을 클릭하여<br>이곳에 생각을 작성해보세요.</p>
      </div>
      <div id="notesEditor" class="hidden flex-grow flex flex-col">
        <textarea id="notesTextarea" class="w-full flex-grow p-3 border border-gray-300 rounded-lg mb-4 focus:ring-2 focus:ring-green-500 outline-none resize-none custom-scrollbar" placeholder="여기에 대화에 대한 생각, 비판, 분석 등을 자유롭게 작성하세요..."></textarea>
        <button id="saveNoteButton" class="bg-green-500 hover:bg-green-600 text-white font-semibold p-3 rounded-lg transition-colors self-end">메모 저장</button>
        <p id="saveStatus" class="text-sm text-green-700 mt-2 h-5 text-right"></p>
      </div>
    </div>
  </div>

  <script>
    // 파이썬에서 직렬화된 데이터를 JS 객체로 변환
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

    function renderChatHistory() {
      chatHistory.innerHTML = '';
      if (data.conversations.length === 0) {
        chatHistory.innerHTML = '<p class="text-gray-400 text-center p-4">아직 대화 내용이 없습니다.</p>';
        return;
      }
      data.conversations.forEach(conv => {
        const block = document.createElement('div');
        block.className = 'chat-block p-3 mb-3 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-100 transition ' +
                          (conv.id === selectedConversationId ? 'selected' : '');
        block.dataset.id = conv.id;

        const p1 = document.createElement('p');
        p1.className = 'font-semibold text-blue-700';
        p1.textContent = '나: ' + conv.user;
        const p2 = document.createElement('p');
        p2.className = 'text-green-700 mt-1';
        p2.textContent = 'AI: ' + conv.ai;

        block.append(p1, p2);
        block.addEventListener('click', () => {
          selectedConversationId = conv.id;
          renderChatHistory();
          showNotes(conv);
        });
        chatHistory.append(block);
      });
      chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    function showNotes(conv) {
      notesPlaceholder.classList.add('hidden');
      notesEditor.classList.remove('hidden');
      notesTitle.textContent = `대화 #${conv.id} (${conv.user.substring(0,15)}…)에 대한 생각`;
      notesTextarea.value = conv.notes;
      saveStatus.textContent = '';
    }

    function handleSend() {
      const text = userInput.value.trim();
      if (!text) return;
      // Streamlit의 text_input 과 연결
      // 여기에 아무 동작 없이 아래 코드로 대체합니다
      // 페이지 전체가 reload 되어 Python 코드가 실행됩니다
      document.querySelector('input[data-key="in"]').value = text;
      document.querySelector('input[data-key="in"]').dispatchEvent(new Event('change'));
    }

    function handleSaveNote() {
      if (!selectedConversationId) return;
      const idx = data.conversations.findIndex(c => c.id === selectedConversationId);
      if (idx < 0) return;
      data.conversations[idx].notes = notesTextarea.value;
      saveStatus.textContent = '메모가 저장되었습니다!';
      setTimeout(() => saveStatus.textContent = '', 2000);

      // 실제 저장은 Python 쪽에 요청을 보내거나
      // localStorage 등에 직접 저장하는 로직을 추가하세요.
    }

    sendButton.addEventListener('click', handleSend);
    userInput.addEventListener('keypress', e => { if(e.key==='Enter') handleSend(); });
    saveNoteButton.addEventListener('click', handleSaveNote);

    document.addEventListener('DOMContentLoaded', renderChatHistory);
  </script>
</body>
</html>
'''

# 스트림릿에 렌더링
html(html_content, height=800)
