import streamlit as st
import openai
import re

# 페이지 설정
st.set_page_config(layout="wide", page_title="ChatGPT + Notes")

# OpenAI API 키 설정
openai.api_key = st.secrets['OPENAI_API_KEY']

# 세션 상태 초기화
if 'messages' not in st.session_state:
    st.session_state.messages = []   # [{'role':'user'/'assistant', 'content': str}]
if 'notes' not in st.session_state:
    st.session_state.notes = {}      # {assistant_msg_index: note_text}

# 2:1 레이아웃
col1, col2 = st.columns([2, 1])

# 오른쪽 노트 저장 처리 먼저 실행하여 state 업데이트
with col2:
    st.header("📝 Notes")
    if st.session_state.messages:
        # 어시스트 메시지 인덱스 필터
        assistant_idxs = [i for i, m in enumerate(st.session_state.messages) if m['role']=='assistant']
        options = [f"{i+1}. {st.session_state.messages[i]['content'][:30]}…" for i in assistant_idxs]
        sel = st.selectbox("메모할 메시지 선택", options)
        sel_idx = assistant_idxs[options.index(sel)]
        existing = st.session_state.notes.get(sel_idx, "")
        note_text = st.text_area("메모 입력", value=existing, height=150)
        if st.button("저장 메모", key=f"save_{sel_idx}"):
            st.session_state.notes[sel_idx] = note_text
            st.success("메모가 저장되었습니다!")
            st.experimental_rerun()
    else:
        st.info("왼쪽에서 대화를 시작하세요.")

with col1:
    st.header("💬 Chat")

    # Chat input 및 메시지 처리
    prompt = st.chat_input("메시지를 입력하세요…")
    if prompt:
        st.session_state.messages.append({'role':'user','content':prompt})
        with st.spinner("GPT 응답 중…"):
            resp = openai.ChatCompletion.create(
                model='gpt-3.5-turbo',
                messages=[{'role':'system','content':'You are a helpful assistant.'}] + st.session_state.messages
            )
        st.session_state.messages.append({'role':'assistant','content':resp.choices[0].message.content})
        st.experimental_rerun()

    # 전체 대화 + 메모 다운로드 버튼
    if st.session_state.messages:
        export_lines = []
        for idx, msg in enumerate(st.session_state.messages):
            prefix = 'User:' if msg['role']=='user' else 'AI:'
            export_lines.append(f"{prefix} {msg['content']}")
            if msg['role']=='assistant' and idx in st.session_state.notes:
                export_lines.append(f"메모: {st.session_state.notes[idx]}")
            export_lines.append("")
        export_text = "\n".join(export_lines)
        st.download_button(
            label="📥 Download All",
            data=export_text,
            file_name="conversation_with_notes.txt",
            mime="text/plain"
        )

    # 대화 및 메모 표시
    for idx, msg in enumerate(st.session_state.messages):
        st.chat_message(msg['role']).write(msg['content'])
        if msg['role']=='assistant' and idx in st.session_state.notes:
            st.markdown(
                f"<div style='margin-left:20px;color:gray;'><strong>메모:</strong> {st.session_state.notes[idx]}</div>",
                unsafe_allow_html=True
            )
