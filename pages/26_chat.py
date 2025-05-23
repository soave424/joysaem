import streamlit as st
from openai import OpenAI
import json

# ✅ 페이지 설정
st.set_page_config(layout="wide", page_title="ChatGPT + Notes")

# ✅ OpenAI 클라이언트 설정
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ✅ 세션 상태 초기화
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'notes' not in st.session_state:
    st.session_state.notes = {}
if 'book_context' not in st.session_state:
    st.session_state.book_context = ""
if 'selected_note_index' not in st.session_state:
    st.session_state.selected_note_index = 0

# ✅ 시스템 프롬프트 내용
DEFAULT_SYSTEM_PROMPT = "You are a helpful assistant. Answer clearly and kindly."

# ✅ 여백 줄이기 스타일
st.markdown("""
    <style>
    .block-container {padding-top: 1rem !important; padding-bottom: 1rem !important;}
    .stChatMessage {margin-top: 0.3rem !important; margin-bottom: 0.3rem !important;}
    </style>
""", unsafe_allow_html=True)

# ✅ 레이아웃: col1 = Chat / col2 = Notes
col1, col2 = st.columns([3, 1], gap="small")

# 👉 col2: Notes 패널
with col2:
    st.header("📝 Notes")
    uploaded = st.file_uploader("📘 텍스트 파일 업로드", type="txt")
    if uploaded:
        st.session_state.book_context = uploaded.read().decode("utf-8")
        st.success(" 업로드되었습니다!")

    assistant_idxs = [i for i, m in enumerate(st.session_state.messages) if m['role'] == 'assistant']
    if assistant_idxs:
        options = [f"{i+1}. {st.session_state.messages[i]['content'][:30]}…" for i in assistant_idxs]
        selected = st.selectbox("메모할 메시지 선택", options, index=st.session_state.selected_note_index, key="note_select")
        sel_idx = assistant_idxs[options.index(selected)]
        st.session_state.selected_note_index = options.index(selected)

        note_text = st.session_state.notes.get(sel_idx, "")
        updated = st.text_area("메모 입력", value=note_text, height=150, key="note_input")
        if st.button("저장 메모", key="save_note"):
            st.session_state.notes[sel_idx] = updated
            st.success("메모가 저장되었습니다!")
    else:
        st.info("왼쪽에서 대화를 시작하세요.")

# 👉 col1: Chat 패널
with col1:
    st.header("💬 Chat")

    # 기존 메시지 출력
    for idx, msg in enumerate(st.session_state.messages):
        st.chat_message(msg["role"]).write(msg["content"])
        if msg["role"] == "assistant" and idx in st.session_state.notes:
            st.markdown(
                f"<div style='margin-left:20px;color:gray;'><strong>메모:</strong> {st.session_state.notes[idx]}</div>",
                unsafe_allow_html=True
            )

    # 입력창
    user_input = st.chat_input("메시지를 입력하세요…")
    if user_input:
        st.session_state.messages.append({'role': 'user', 'content': user_input})

        # 시스템 메시지 구성
        system_prompt = DEFAULT_SYSTEM_PROMPT
        if st.session_state.book_context:
            system_prompt += "\n\n[책 요약]\n" + st.session_state.book_context

        # ✅ 메시지 유효성 검사
        invalid_msgs = [
            m for m in st.session_state.messages
            if not all(k in m for k in ["role", "content"]) or m["role"] not in ["user", "assistant", "system"] or not m["content"]
        ]
        if invalid_msgs:
            st.error(f"⚠️ 메시지 형식 오류: {invalid_msgs}")
        else:
            with st.spinner("GPT 응답 중…"):
                try:
                    resp = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {'role': 'system', 'content': system_prompt},
                            *st.session_state.messages
                        ]
                    )
                    assistant_reply = resp.choices[0].message.content
                    st.session_state.messages.append({'role': 'assistant', 'content': assistant_reply})
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ 오류 발생: {str(e)}")
