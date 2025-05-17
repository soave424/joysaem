import streamlit as st
from openai import OpenAI
import re

# 페이지 설정
st.set_page_config(layout="wide", page_title="ChatGPT + Custom GPT + Notes")

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=st.secrets['OPENAI_API_KEY'])

# 세션 상태 초기화
if 'messages' not in st.session_state:
    st.session_state.messages = []  # List[{'role': str, 'content': str}]
if 'notes' not in st.session_state:
    st.session_state.notes = {}     # Dict[int, str]
if 'model_id' not in st.session_state:
    st.session_state.model_id = ''  # 선택된 모델 ID 또는 링크 입력값

# 2:1 레이아웃 구성
col1, col2 = st.columns([2, 1])

with col1:
    # 커스텀 GPT ID 또는 링크 입력
    st.subheader("🔧 사용할 모델 입력 또는 링크")
    model_input = st.text_input(
        "모델 ID 또는 공유 링크 (예: g-abcd1234 또는 https://chat.openai.com/g/abcd1234)",
        value=st.session_state.model_id
    )
    if model_input:
        m = re.search(r"/g/([\w-]+)", model_input)
        if m:
            st.session_state.model_id = m.group(1)
        elif model_input.startswith("g-") or model_input in ["gpt-3.5-turbo", "gpt-4"]:
            st.session_state.model_id = model_input
        else:
            st.error("유효한 모델 ID나 링크를 입력해주세요.")
    if st.session_state.model_id:
        st.markdown(f"**선택된 모델 ID:** `{st.session_state.model_id}`")
    else:
        st.info("모델 ID를 입력해야 채팅을 시작할 수 있습니다.")

    # 헤더 및 다운로드 버튼
    hdr_col, dl_col = st.columns([8, 2])
    with hdr_col:
        st.header(f"💬 Chat ({st.session_state.model_id or '모델 미지정'})")
    with dl_col:
        if st.session_state.messages and st.session_state.model_id:
            # 전체 대화 + 메모 텍스트 생성
            lines = []
            for i, m in enumerate(st.session_state.messages):
                prefix = 'User:' if m['role']=='user' else 'AI:'
                lines.append(f"{prefix} {m['content']}")
                if m['role']=='assistant' and i in st.session_state.notes:
                    lines.append(f"메모: {st.session_state.notes[i]}")
                lines.append("")
            full_text = "\n".join(lines).strip()
            st.download_button(
                label="📥 Download All",
                data=full_text,
                file_name="chat_with_notes.txt",
                mime="text/plain"
            )

    # 대화 출력 및 메모 표시
    for idx, msg in enumerate(st.session_state.messages):
        st.chat_message(msg['role']).write(msg['content'])
        if msg['role']=='assistant' and idx in st.session_state.notes:
            note = st.session_state.notes[idx]
            st.markdown(
                f"<div style='margin-left:20px; color:gray;'><strong>메모:</strong> {note}</div>",
                unsafe_allow_html=True
            )

    # 사용자 입력 및 API 호출
    if st.session_state.model_id:
        prompt = st.chat_input("메시지를 입력하세요…")
        if prompt:
            st.session_state.messages.append({'role':'user','content':prompt})
            with st.spinner("응답 생성 중…"):
                resp = client.chat.completions.create(
                    model=st.session_state.model_id,
                    messages=[{'role':'system','content':'You are a helpful assistant.'}] + st.session_state.messages
                )
            st.session_state.messages.append({'role':'assistant','content':resp.choices[0].message.content})

with col2:
    st.header("📝 Notes")
    if not st.session_state.messages:
        st.info("왼쪽에서 대화를 시작하세요.")
    else:
        # AI 메시지(assistant) 인덱스만 선택지로 제공
        assistant_indices = [i for i, m in enumerate(st.session_state.messages) if m['role']=='assistant']
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
            st.experimental_rerun()

        # 저장된 메모 요약
        if st.session_state.notes:
            st.markdown("---")
            st.subheader("💾 저장된 메모들")
            for i in sorted(st.session_state.notes):
                snippet = st.session_state.messages[i]['content']
                st.markdown(f"**{i+1}. {snippet[:40]}…**  \n{st.session_state.notes[i]}")
