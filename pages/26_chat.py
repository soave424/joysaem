# app.py
import streamlit as st
from openai import OpenAI

# 페이지 설정
st.set_page_config(layout="wide", page_title="ChatGPT + Notes")

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []   # List[{"role": str, "content": str}]
if "notes" not in st.session_state:
    st.session_state.notes = {}      # Dict[int, str]

# 2:1 레이아웃
col1, col2 = st.columns([2, 1])

with col1:
    st.header("💬 Chat")

    # 대화 렌더링 + 메모 표시
    for idx, msg in enumerate(st.session_state.messages):
        st.chat_message(msg["role"]).write(msg["content"])
        if msg["role"] == "assistant" and idx in st.session_state.notes:
            note_text = st.session_state.notes[idx]
            # 메모는 약간 indent 해서 표시
            st.markdown(
                f"<div style='margin-left:20px; color:gray;'><strong>메모:</strong> {note_text}</div>",
                unsafe_allow_html=True
            )

    # 입력창
    prompt = st.chat_input("메시지를 입력하세요…")
    if prompt:
        # 사용자 질문 저장
        st.session_state.messages.append({"role": "user", "content": prompt})
        # GPT 호출
        with st.spinner("GPT 응답 중…"):
            resp = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role":"system","content":"You are a helpful assistant."}]
                         + st.session_state.messages
            )
        answer = resp.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": answer})

    # 대화 + 메모 전체 다운로드
    if st.session_state.messages:
        # 메시지별로 메모 포함해 텍스트 조합
        lines = []
        for idx, m in enumerate(st.session_state.messages):
            prefix = "User:" if m["role"] == "user" else "AI:"
            lines.append(f"{prefix} {m['content']}")
            if m["role"] == "assistant" and idx in st.session_state.notes:
                lines.append(f"메모: {st.session_state.notes[idx]}")
            lines.append("")  # 빈 줄
        all_text = "\n".join(lines).strip()

        st.download_button(
            label="📥 Download Conversation with Notes",
            data=all_text,
            file_name="conversation_with_notes.txt",
            mime="text/plain"
        )

with col2:
    st.header("📝 Notes")

    if not st.session_state.messages:
        st.info("왼쪽에서 대화를 시작해보세요.")
    else:
        # 메시지 선택 드롭다운
        options = [
            f"{i+1}. [{'U' if m['role']=='user' else 'A'}] {m['content'][:30]}{'…' if len(m['content'])>30 else ''}"
            for i, m in enumerate(st.session_state.messages)
        ]
        sel = st.selectbox("메모할 메시지를 선택하세요", options)
        idx = options.index(sel)

        # 선택된 메시지 메모 입력/저장
        existing = st.session_state.notes.get(idx, "")
        note = st.text_area("메모 입력", value=existing, height=150)
        if st.button("저장 메모", key=f"save_{idx}"):
            st.session_state.notes[idx] = note
            st.success("메모가 저장되었습니다!")

        # 메모만 따로 다운로드
        if st.session_state.notes:
            notes_lines = []
            for i in sorted(st.session_state.notes):
                notes_lines.append(f"{i+1}. {st.session_state.notes[i]}")
            notes_text = "\n\n".join(notes_lines)
            st.download_button(
                label="📥 Download Notes",
                data=notes_text,
                file_name="notes.txt",
                mime="text/plain"
            )
