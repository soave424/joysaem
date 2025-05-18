import streamlit as st
import openai

# 1) 페이지 설정
st.set_page_config(layout="wide", page_title="ChatGPT + Notes")

# 2) OpenAI API 키 설정
openai.api_key = st.secrets["OPENAI_API_KEY"]

# 3) 세션 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []   # [{"role":"user"/"assistant", "content":...}]
if "notes" not in st.session_state:
    st.session_state.notes = {}      # {msg_index: note_text}

# 2:1 레이아웃
col1, col2 = st.columns([2, 1])

with col1:
    st.header("💬 Chat")

    # 전체 대화 + 메모 다운로드
    if st.session_state.messages:
        lines = []
        for i, m in enumerate(st.session_state.messages):
            prefix = "User:" if m["role"] == "user" else "AI:"
            lines.append(f"{prefix} {m['content']}")
            if m["role"] == "assistant" and i in st.session_state.notes:
                lines.append(f"메모: {st.session_state.notes[i]}")
            lines.append("")
        full_text = "\n".join(lines).strip()
        st.download_button("📥 Download All", data=full_text,
                           file_name="conversation_with_notes.txt",
                           mime="text/plain")

    # 대화 표시 + 메모 반영
    for idx, msg in enumerate(st.session_state.messages):
        st.chat_message(msg["role"]).write(msg["content"])
        if msg["role"] == "assistant" and idx in st.session_state.notes:
            st.markdown(
                f"<div style='margin-left:20px; color:gray;'><strong>메모:</strong> "
                f"{st.session_state.notes[idx]}</div>",
                unsafe_allow_html=True
            )

    # 사용자 입력 & API 호출
    prompt = st.chat_input("메시지를 입력하세요…")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.spinner("GPT 응답 중…"):
            resp = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role":"system","content":"You are a helpful assistant."}]
                         + st.session_state.messages
            )
        st.session_state.messages.append({
            "role": "assistant",
            "content": resp.choices[0].message.content
        })
        # st.chat_input이 자동 rer런을 트리거해 줍니다

with col2:
    st.header("📝 Notes")
    if not st.session_state.messages:
        st.info("왼쪽에서 대화를 시작해보세요.")
    else:
        # 어시스턴트 메시지 인덱스만 선택
        assistant_idxs = [i for i, m in enumerate(st.session_state.messages)
                          if m["role"] == "assistant"]
        options = [
            f"{i+1}. {st.session_state.messages[i]['content'][:30]}…"
            for i in assistant_idxs
        ]
        sel = st.selectbox("메모할 메시지를 선택하세요", options)
        idx = assistant_idxs[options.index(sel)]

        # 메모 입력·저장
        existing = st.session_state.notes.get(idx, "")
        note = st.text_area("메모 입력", value=existing, height=150)
        if st.button("저장 메모", key=f"save_{idx}"):
            st.session_state.notes[idx] = note
            st.success("메모가 저장되었습니다!")

        # 저장된 메모 요약
        if st.session_state.notes:
            st.markdown("---")
            for i in sorted(st.session_state.notes):
                snippet = st.session_state.messages[i]["content"]
                st.markdown(f"**{i+1}. {snippet[:40]}…**  \n{st.session_state.notes[i]}")
