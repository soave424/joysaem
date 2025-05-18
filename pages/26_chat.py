import streamlit as st
from openai import OpenAI
import re

# 페이지 설정
st.set_page_config(layout="wide", page_title="ChatGPT + Notes")

# OpenAI 클라이언트 초기화 (v1 API)
client = OpenAI(api_key=st.secrets['OPENAI_API_KEY'])

# 세션 상태 초기화
if 'messages' not in st.session_state:
    st.session_state.messages = []   # [{'role':'user'/'assistant','content': str}]
if 'notes' not in st.session_state:
    st.session_state.notes = {}      # {assistant_msg_index: note_text}

# 2:1 레이아웃
col1, col2 = st.columns([2, 1])

# 우측 메모 패널: 메모 저장 처리
with col2:
    st.header("📝 Notes")
    if st.session_state.messages:
        # 어시스턴트 메시지 인덱스만
        assistant_idxs = [i for i, m in enumerate(st.session_state.messages) if m['role']=='assistant']
        options = [f"{idx+1}. {st.session_state.messages[idx]['content'][:30]}…" for idx in assistant_idxs]
        choice = st.selectbox("메모할 메시지 선택", options)
        sel_idx = assistant_idxs[options.index(choice)]
        note = st.text_area("메모 입력", value=st.session_state.notes.get(sel_idx, ""), height=150)
        if st.button("저장 메모", key=f"save_{sel_idx}"):
            st.session_state.notes[sel_idx] = note
            st.experimental_rerun()
    else:
        st.info("왼쪽에서 대화를 시작하세요.")

# 좌측 채팅 패널
with col1:
    st.header("💬 Chat")

    # 입력 및 GPT 호출
    prompt = st.chat_input("메시지를 입력하세요…")
    if prompt:
        # 사용자 메시지 추가
        st.session_state.messages.append({'role':'user','content':prompt})
        with st.spinner("GPT 응답 중…"):
            resp = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{'role':'system','content':'You are a helpful assistant.'}] + st.session_state.messages
            )
        # 어시스턴트 응답 추가
        st.session_state.messages.append({'role':'assistant','content':resp.choices[0].message.content})

    # 전체 대화 + 메모 다운로드 버튼
    if st.session_state.messages:
        export = []
        for idx, m in enumerate(st.session_state.messages):
            prefix = 'User:' if m['role']=='user' else 'AI:'
            export.append(f"{prefix} {m['content']}")
            if m['role']=='assistant' and idx in st.session_state.notes:
                export.append(f"메모: {st.session_state.notes[idx]}")
            export.append("")
        st.download_button(
            label="📥 Download All",
            data="\n".join(export).strip(),
            file_name="conversation_with_notes.txt",
            mime="text/plain"
        )

    # 대화 및 메모 표시
    for idx, m in enumerate(st.session_state.messages):
        st.chat_message(m['role']).write(m['content'])
        if m['role']=='assistant' and idx in st.session_state.notes:
            st.markdown(
                f"<div style='margin-left:20px;color:gray;'><strong>메모:</strong> {st.session_state.notes[idx]}</div>",
                unsafe_allow_html=True
            )
