import streamlit as st
from openai import OpenAI
import re

# 페이지 설정
st.set_page_config(layout="wide", page_title="ChatGPT + Notes")

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=st.secrets['OPENAI_API_KEY'])

# 세션 상태 초기화
if 'messages' not in st.session_state:
    st.session_state.messages = []  # List of {'role': str, 'content': str}
if 'notes' not in st.session_state:
    st.session_state.notes = {}     # Dict[msg_index, note_text]
if 'model_id' not in st.session_state:
    st.session_state.model_id = ''  # 모델 ID or 링크

# 2:1 레이아웃
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("💬 Chat")
    # 다운로드 버튼
    if st.session_state.messages:
        full = []
        for i, m in enumerate(st.session_state.messages):
            prefix = 'User:' if m['role']=='user' else 'AI:'
            full.append(f"{prefix} {m['content']}")
            if m['role']=='assistant' and i in st.session_state.notes:
                full.append(f"메모: {st.session_state.notes[i]}")
            full.append("")
        text = "\n".join(full).strip()
        st.download_button("📥 Download All", data=text, file_name="chat_notes.txt")

    # 채팅 표시 및 메모 반영
    for idx, msg in enumerate(st.session_state.messages):
        st.chat_message(msg['role']).write(msg['content'])
        # 어시스턴트 메시지(짝수번째: index1,3,5..)만 메모 표시
        if msg['role']=='assistant' and idx in st.session_state.notes:
            st.markdown(f"<div style='margin-left:20px;color:gray;'><strong>메모:</strong> {st.session_state.notes[idx]}</div>", unsafe_allow_html=True)

    # 입력창
    prompt = st.chat_input("메시지를 입력하세요…")
    if prompt:
        st.session_state.messages.append({'role':'user','content':prompt})
        with st.spinner("GPT 응답 중…"):
            res = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{'role':'system','content':'You are a helpful assistant.'}] + st.session_state.messages
            )
        st.session_state.messages.append({'role':'assistant','content':res.choices[0].message.content})
        # 자동 rerun
        st.experimental_rerun()

with col2:
    st.subheader("📝 Notes")
    if not st.session_state.messages:
        st.info("왼쪽에서 대화를 시작해 주세요.")
    else:
        # 어시스턴트 메시지 인덱스만
        assistant_idxs = [i for i,m in enumerate(st.session_state.messages) if m['role']=='assistant']
        options = [f"{i+1}. {st.session_state.messages[i]['content'][:30]}..." for i in assistant_idxs]
        sel = st.selectbox("메모할 메시지를 선택하세요", options)
        selected = assistant_idxs[options.index(sel)]

        # 메모 입력 및 저장
        existing = st.session_state.notes.get(selected, "")
        note = st.text_area("메모 입력", value=existing, height=150)
        if st.button("저장 메모", key=f"save_{selected}"):
            st.session_state.notes[selected] = note
            # 저장 후 즉시 반영
            st.experimental_rerun()

        # 저장된 메모 리스트
        if st.session_state.notes:
            st.markdown("---")
            for i in sorted(st.session_state.notes):
                snippet = st.session_state.messages[i]['content']
                st.markdown(f"**{i+1}. {snippet[:40]}…**  \n{st.session_state.notes[i]}")
