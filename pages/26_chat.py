import streamlit as st
import openai

# 페이지 설정
st.set_page_config(layout="wide", page_title="ChatGPT + Notes")

# OpenAI API 키 설정
openai.api_key = st.secrets['OPENAI_API_KEY']

# 세션 상태 초기화
if 'messages' not in st.session_state:
    st.session_state.messages = []  # list of {'role', 'content'}
if 'notes' not in st.session_state:
    st.session_state.notes = {}     # dict mapping assistant message index to note

# 2:1 레이아웃
col1, col2 = st.columns([2, 1])

with col1:
    st.header("💬 Chat")

    # 전체 대화 + 메모 다운로드
    if st.session_state.messages:
        export_lines = []
        for idx, msg in enumerate(st.session_state.messages):
            prefix = 'User:' if msg['role'] == 'user' else 'AI:'
            export_lines.append(f"{prefix} {msg['content']}")
            if msg['role'] == 'assistant' and idx in st.session_state.notes:
                export_lines.append(f"메모: {st.session_state.notes[idx]}")
            export_lines.append("")
        export_text = "\n".join(export_lines)
        st.download_button(
            label="📥 Download All",
            data=export_text,
            file_name="conversation_with_notes.txt",
            mime="text/plain"
        )

    # 채팅 출력 및 메모 표시
    for idx, msg in enumerate(st.session_state.messages):
        st.chat_message(msg['role']).write(msg['content'])
        if msg['role'] == 'assistant' and idx in st.session_state.notes:
            st.markdown(
                f"<div style='margin-left:20px;color:gray;'><strong>메모:</strong> {st.session_state.notes[idx]}</div>",
                unsafe_allow_html=True
            )

    # 사용자 입력 및 API 호출
    prompt = st.chat_input("메시지를 입력하세요…")
    if prompt:
        # 사용자 메시지 저장
        st.session_state.messages.append({'role': 'user', 'content': prompt})
        # API 호출을 위한 메시지 리스트 준비
        msgs_for_api = [{'role':'system', 'content':'You are a helpful assistant.'}] + st.session_state.messages
        with st.spinner("GPT 응답 중…"):
            resp = openai.ChatCompletion.create(
                model='gpt-3.5-turbo',
                messages=msgs_for_api
            )
        # 어시스턴트 응답 저장
        st.session_state.messages.append({'role': 'assistant', 'content': resp.choices[0].message.content})

with col2:
    st.header("📝 Notes")
    if not st.session_state.messages:
        st.info("왼쪽에서 대화를 시작해보세요.")
    else:
        # 어시스턴트 메시지 인덱스만 선택지로 제공
        assistant_idxs = [i for i, m in enumerate(st.session_state.messages) if m['role'] == 'assistant']
        options = [f"{i+1}. {st.session_state.messages[i]['content'][:30]}..." for i in assistant_idxs]
        sel = st.selectbox("메모할 메시지를 선택하세요", options)
        selected_idx = assistant_idxs[options.index(sel)]

        # 메모 입력 및 저장
        existing = st.session_state.notes.get(selected_idx, '')
        note_text = st.text_area("메모 입력", value=existing, height=150)
        if st.button("저장 메모", key=f"save_{selected_idx}"):
            st.session_state.notes[selected_idx] = note_text
            # 저장 후 즉시 반영
            st.experimental_rerun()
