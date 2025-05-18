import streamlit as st
from openai import OpenAI
import re

# 페이지 설정
st.set_page_config(layout="wide", page_title="ChatGPT + Notes")

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=st.secrets['OPENAI_API_KEY'])

# 세션 상태 초기화
if 'messages' not in st.session_state:
    st.session_state.messages = []   # [{'role':'user'/'assistant','content': str}]
if 'notes' not in st.session_state:
    st.session_state.notes = {}      # {assistant_msg_index: note_text}
if 'input' not in st.session_state:
    st.session_state.input = ''

# 컬럼 레이아웃: 좌측-우측 2:1
col1, col2 = st.columns([2, 1])

# 우측: 메모 패널
with col2:
    st.header("📝 Notes")
    if st.session_state.messages:
        assistant_idxs = [i for i, m in enumerate(st.session_state.messages) if m['role']=='assistant']
        options = [f"{idx+1}. {st.session_state.messages[idx]['content'][:30]}…" for idx in assistant_idxs]
        sel = st.selectbox("메모할 메시지 선택", options)
        sel_idx = assistant_idxs[options.index(sel)]
        note_text = st.session_state.notes.get(sel_idx, "")
        updated = st.text_area("메모 입력", value=note_text, height=150)
        if st.button("저장 메모", key=f"save_{sel_idx}"):
            st.session_state.notes[sel_idx] = updated
            st.success("메모가 저장되었습니다!")
    else:
        st.info("왼쪽에서 대화를 시작하세요.")

# 좌측: 채팅 패널
with col1:
    st.header("💬 Chat")
    # 전체 대화 + 메모 다운로드 버튼
    if st.session_state.messages:
        lines = []
        for idx, msg in enumerate(st.session_state.messages):
            prefix = 'User:' if msg['role']=='user' else 'AI:'
            lines.append(f"{prefix} {msg['content']}")
            if msg['role']=='assistant' and idx in st.session_state.notes:
                lines.append(f"메모: {st.session_state.notes[idx]}")
            lines.append("")
        full_text = "\n".join(lines).strip()
        st.download_button(
            label="📥 Download All",
            data=full_text,
            file_name="conversation_with_notes.txt",
            mime="text/plain"
        )

    # 스크롤 가능한 메시지 컨테이너
    st.markdown(
        '<div style="height:60vh; overflow-y:auto; padding-right:10px;">',
        unsafe_allow_html=True
    )
    for idx, msg in enumerate(st.session_state.messages):
        st.chat_message(msg['role']).write(msg['content'])
        if msg['role']=='assistant' and idx in st.session_state.notes:
            st.markdown(
                f"<div style='margin-left:20px;color:gray;'><strong>메모:</strong> {st.session_state.notes[idx]}</div>",
                unsafe_allow_html=True
            )
    st.markdown('</div>', unsafe_allow_html=True)

    # 입력 폼: st.form 사용으로 즉시 반영
    with st.form(key='chat_form', clear_on_submit=True):
        user_input = st.text_input("메시지를 입력하세요…", key='input')
        submitted = st.form_submit_button("전송")
        if submitted and user_input:
            st.session_state.messages.append({'role':'user','content':user_input})
            with st.spinner("GPT 응답 중…"):
                resp = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{'role':'system','content':'You are a helpful assistant.'}] + st.session_state.messages
                )
            st.session_state.messages.append({'role':'assistant','content':resp.choices[0].message.content})
