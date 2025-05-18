import streamlit as st
from openai import OpenAI

# 1) 페이지 설정
st.set_page_config(layout="wide", page_title="ChatGPT + Notes")

# 2) OpenAI 클라이언트 초기화
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# 3) 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []   # [{'role': 'user'/'assistant', 'content': str}]
if "notes" not in st.session_state:
    st.session_state.notes = {}      # {msg_index: note_text}

# ──────────────────────────────────────────────────
# 좌우 2:1 컬럼
col1, col2 = st.columns([2, 1])

with col1:
    st.header("💬 Chat")

    # 4) 대화 전체 다운로드 버튼
    if st.session_state.messages:
        full_text = "\n\n".join(
            f"{'User:' if m['role']=='user' else 'AI:'} {m['content']}"
            for m in st.session_state.messages
        )
        st.download_button(
            label="📥 Download All",
            data=full_text,
            file_name="conversation.txt",
            mime="text/plain"
        )

    # 5) 이전 대화 출력
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    # 6) 사용자 입력
    prompt = st.chat_input("메시지를 입력하세요…")
    if prompt:
        # 사용자 메시지 저장
        st.session_state.messages.append({"role": "user", "content": prompt})
        # GPT 호출
        with st.spinner("GPT 응답 중…"):
            res = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role":"system","content":"You are a helpful assistant."}]
                         + st.session_state.messages
            )
        answer = res.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": answer})

with col2:
    st.header("📝 Notes")

    if not st.session_state.messages:
        st.info("왼쪽에서 대화를 시작해보세요.")
    else:
        # 7) 메시지 선택 드롭다운
        options = [
            f"{i+1}. [{'U' if m['role']=='user' else 'A'}] {m['content'][:30]}{'…' if len(m['content'])>30 else ''}"
            for i, m in enumerate(st.session_state.messages)
        ]
        idx = st.selectbox("메시지 선택", options, index=0)
        msg_i = options.index(idx)  # 실제 인덱스

        # 8) 선택 메시지 메모 입력
        existing_note = st.session_state.notes.get(msg_i, "")
        note = st.text_area("메모 입력", value=existing_note, height=200)

        # 9) 메모 저장
        if st.button("저장", key=f"save_{msg_i}"):
            st.session_state.notes[msg_i] = note
            st.success("메모가 저장되었습니다!")

        # 10) 저장된 메모 요약
        st.markdown("---")
        st.subheader("💾 모든 메모")
        for i, txt in st.session_state.notes.items():
            snippet = st.session_state.messages[i]["content"]
            st.markdown(f"**{i+1}. {snippet[:40]}…**  \n{txt}")