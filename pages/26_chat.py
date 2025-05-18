import streamlit as st
from openai import OpenAI

# 페이지 설정
st.set_page_config(layout="wide", page_title="ChatGPT + Notes")

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=st.secrets['OPENAI_API_KEY'])

# 세션 상태 초기화
if 'messages' not in st.session_state:
    st.session_state.messages = []  # List[{'role': str, 'content': str}]
if 'notes' not in st.session_state:
    st.session_state.notes = {}     # Dict[int, str]

# 2:1 레이아웃 구성
col1, col2 = st.columns([2, 1])

with col1:
    # 헤더 및 다운로드 버튼 배치
    hdr_col, dl_col = st.columns([8, 2])
    with hdr_col:
        st.header("💬 Chat")
    with dl_col:
        if st.session_state.messages:
            # 대화 + 메모 합쳐서 텍스트 생성
            lines = []
            for idx, m in enumerate(st.session_state.messages):
                prefix = 'User:' if m['role'] == 'user' else 'AI:'
                lines.append(f"{prefix} {m['content']}")
                if m['role'] == 'assistant' and idx in st.session_state.notes:
                    lines.append(f"메모: {st.session_state.notes[idx]}")
                lines.append("")
            output = "\n".join(lines).strip()
            st.download_button(
                label="📥 Download All",
                data=output,
                file_name="conversation_with_notes.txt",
                mime="text/plain"
            )

    # 사용자 입력 처리 (먼저 처리해야 즉시 반영)
    prompt = st.chat_input("메시지를 입력하세요…")
    if prompt:
        # 사용자 메시지 저장 및 GPT 호출
        st.session_state.messages.append({'role': 'user', 'content': prompt})
        with st.spinner("GPT 응답 중…"):
            resp = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{'role': 'system', 'content': 'You are a helpful assistant.'}] + st.session_state.messages
            )
        st.session_state.messages.append({'role': 'assistant', 'content': resp.choices[0].message.content})
        # Streamlit이 자동으로 다시 렌더링합니다

    # 대화 및 메모 표시
    for idx, msg in enumerate(st.session_state.messages):
        st.chat_message(msg['role']).write(msg['content'])
        # 어시스턴트 메시지에 메모가 있으면 바로 아래에 표시
        if msg['role'] == 'assistant' and idx in st.session_state.notes:
            note = st.session_state.notes[idx]
            st.markdown(
                f"<div style='margin-left:20px; color:gray;'><strong>메모:</strong> {note}</div>",
                unsafe_allow_html=True
            )

with col2:
    st.header("📝 Notes")

    if not st.session_state.messages:
        st.info("왼쪽에서 대화를 시작해보세요.")
    else:
        # AI 메시지(assistant) 인덱스만 선택지로 제공
        assistant_indices = [i for i, m in enumerate(st.session_state.messages) if m['role'] == 'assistant']
        options = [
            f"{i+1}. {st.session_state.messages[i]['content'][:30]}{'…' if len(st.session_state.messages[i]['content'])>30 else ''}"
            for i in assistant_indices
        ]
        choice = st.selectbox("메모할 메시지를 선택하세요", options)
        selected_idx = assistant_indices[options.index(choice)]

        # 메모 입력 및 저장
        existing = st.session_state.notes.get(selected_idx, "")
        note_text = st.text_area("메모 입력", value=existing, height=150)
        if st.button("저장 메모", key=f"save_{selected_idx}"):
            st.session_state.notes[selected_idx] = note_text
            st.success("메모가 저장되었습니다!")
        
        # 저장된 메모 요약
        if st.session_state.notes:
            st.markdown("---")
            st.subheader("💾 저장된 메모들")
            for i in sorted(st.session_state.notes):
                snippet = st.session_state.messages[i]['content']
                st.markdown(f"**{i+1}. {snippet[:40]}…**  \n{st.session_state.notes[i]}")
