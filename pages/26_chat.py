import streamlit as st
from openai import OpenAI

# 페이지 설정
st.set_page_config(layout="wide", page_title="ChatGPT + Notes")

# OpenAI 클라이언트 초기화 (새 API 사용)
client = OpenAI(api_key=st.secrets['OPENAI_API_KEY'])

# 세션 상태 초기화
if 'messages' not in st.session_state:
    st.session_state.messages = []  # [{'role':'user'/'assistant', 'content': str}]
if 'notes' not in st.session_state:
    st.session_state.notes = {}     # {assistant_msg_index: note_text}

# 2:1 레이아웃
col1, col2 = st.columns([2, 1])

with col1:
    st.header("💬 Chat")

    # 대화 및 메모 함께 다운로드
    if st.session_state.messages:
        export = []
        for idx, msg in enumerate(st.session_state.messages):
            prefix = 'User:' if msg['role']=='user' else 'AI:'
            export.append(f"{prefix} {msg['content']}")
            if msg['role']=='assistant' and idx in st.session_state.notes:
                export.append(f"메모: {st.session_state.notes[idx]}")
            export.append("")
        export_text = "\n".join(export).strip()
        st.download_button(
            label="📥 Download All",
            data=export_text,
            file_name="conversation_with_notes.txt",
            mime="text/plain"
        )

    # 이전 대화 + 메모 표시
    for idx, msg in enumerate(st.session_state.messages):
        st.chat_message(msg['role']).write(msg['content'])
        # 어시스턴트 메시지 아래에 메모가 있으면 표시
        if msg['role']=='assistant' and idx in st.session_state.notes:
            st.markdown(
                f"<div style='margin-left:20px; color:gray;'><strong>메모:</strong> {st.session_state.notes[idx]}</div>",
                unsafe_allow_html=True
            )

    # 사용자 입력 & GPT 호출
    prompt = st.chat_input("메시지를 입력하세요…")
    if prompt:
        st.session_state.messages.append({'role':'user','content':prompt})
        with st.spinner("GPT 응답 중…"):
            # 새 SDK 방식
            resp = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{'role':'system','content':'You are a helpful assistant.'}] + st.session_state.messages
            )
        # 어시스트 응답 추가
        assistant_msg = resp.choices[0].message.content
        st.session_state.messages.append({'role':'assistant','content':assistant_msg})
        # 입력 즉시 반영 (st.chat_input가 자동 rerun)

with col2:
    st.header("📝 Notes")

    if not st.session_state.messages:
        st.info("왼쪽에서 대화를 시작해보세요.")
    else:
        # 어시스턴트 메시지 인덱스만 선택
        assistant_idxs = [i for i,m in enumerate(st.session_state.messages) if m['role']=='assistant']
        options = [f"{i+1}. {st.session_state.messages[i]['content'][:30]}…" for i in assistant_idxs]
        sel = st.selectbox("메모할 메시지를 선택하세요", options)
        sel_idx = assistant_idxs[options.index(sel)]

        # 메모 입력 및 저장
        existing = st.session_state.notes.get(sel_idx, "")
        note = st.text_area("메모 입력", value=existing, height=150)
        if st.button("저장 메모", key=f"save_{sel_idx}"):
            st.session_state.notes[sel_idx] = note
            st.success("메모가 저장되었습니다!")
            # 메모 추가 후 바로 대화 아래에도 표시되도록 메시지 새로고침 없이 반영
            # (다음 rerun 시 자동 표시)

        # 저장된 메모 요약
        if st.session_state.notes:
            st.markdown("---")
            for i in sorted(st.session_state.notes):
                snippet = st.session_state.messages[i]['content']
                st.markdown(f"**{i+1}. {snippet[:40]}…**  \n{st.session_state.notes[i]}")
