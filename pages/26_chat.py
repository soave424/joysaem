import streamlit as st
from openai import OpenAI

st.set_page_config(layout="wide", page_title="ChatGPT + Notes")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'notes' not in st.session_state:
    st.session_state.notes = {}
if 'book_context' not in st.session_state:
    st.session_state.book_context = ""

DEFAULT_SYSTEM_PROMPT = """..."""

def build_prompt(user_input):
    if "엄마 사용법" in user_input:
        return (
            "초등학생이 《엄마 사용법》이라는 책을 읽은 뒤 친구와 함께 자연스럽게 주고받을 수 있는 대화를 만들어줘. "
            "..."
        )
    return user_input

# ✅ CSS로 여백 및 Notes 고정 처리
st.markdown("""
    <style>
    /* Chat 영역 header와 메시지 간격 제거 */
    h1, h2, h3, h4, h5, h6 {
        margin-bottom: 0.2rem !important;
    }

    /* Chat 메시지 container 여백 줄이기 */
    .stChatMessage {
        margin-top: 0.3rem !important;
        margin-bottom: 0.3rem !important;
        padding-top: 0.2rem !important;
        padding-bottom: 0.2rem !important;
    }

    /* 입력창 위 여백 제거 */
    div[data-testid="chat-input"] > div:first-child {
        display: none !important;
    }

    /* 전체 섹션 패딩 조정 */
    section.main > div {
        padding-top: 0.5rem !important;
    }
    </style>
""", unsafe_allow_html=True)

# ✅ 레이아웃 설정
col1, col2 = st.columns([3, 1], gap="small")

# 👉 Notes 영역 (col2)
with col2:
    st.header("📝 Notes")
    uploaded = st.file_uploader("📘 텍스트 파일 업로드", type="txt")
    if uploaded:
        st.session_state.book_context = uploaded.read().decode("utf-8")
        st.success(" 업로드되었습니다!")

    if st.session_state.messages:
        assistant_idxs = [i for i, m in enumerate(st.session_state.messages) if m['role'] == 'assistant']
        options = [f"{idx + 1}. {st.session_state.messages[idx]['content'][:30]}…" for idx in assistant_idxs]
        choice = st.selectbox("메모할 메시지 선택", options)
        sel_idx = assistant_idxs[options.index(choice)]
        note_text = st.session_state.notes.get(sel_idx, "")
        updated = st.text_area("메모 입력", value=note_text, height=150)
        if st.button("저장 메모", key=f"save_{sel_idx}"):
            st.session_state.notes[sel_idx] = updated
            st.success("메모가 저장되었습니다!")
    else:
        st.info("왼쪽에서 대화를 시작하세요.")

# 👉 Chat 영역 (col1)
with col1:
    st.header("💬 Chat")
    for idx, msg in enumerate(st.session_state.messages):
        st.chat_message(msg['role']).write(msg['content'])
        if msg['role'] == 'assistant' and idx in st.session_state.notes:
            st.markdown(
                f"<div style='margin-left:20px;color:gray;'><strong>메모:</strong> {st.session_state.notes[idx]}</div>",
                unsafe_allow_html=True
            )

# ✅ 입력창 (항상 하단)
user_input = st.chat_input("메시지를 입력하세요…")
if user_input:
    st.session_state.messages.append({'role': 'user', 'content': user_input})
    st.chat_message("user").write(user_input)

    system_prompt = DEFAULT_SYSTEM_PROMPT
    if st.session_state.book_context:
        system_prompt += "\n\n[추가 책 요약]\n" + st.session_state.book_context

    with st.spinner("GPT 응답 중…"):
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {'role': 'system', 'content': system_prompt},
                *st.session_state.messages[:-1],
                {'role': 'user', 'content': build_prompt(user_input)}
            ]
        )
    assistant_reply = resp.choices[0].message.content
    st.session_state.messages.append({'role': 'assistant', 'content': assistant_reply})
    st.chat_message("assistant").write(assistant_reply)
