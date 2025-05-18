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

DEFAULT_SYSTEM_PROMPT = """..."""  # 생략 가능

def build_prompt(user_input):
    return user_input

# 💄 최소 여백 스타일링
st.markdown("""
    <style>
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
    }
    .stChatMessage {
        margin-top: 0.3rem !important;
        margin-bottom: 0.3rem !important;
    }
    </style>
""", unsafe_allow_html=True)

# 💬 2-Column 구성
col1, col2 = st.columns([3, 1], gap="small")

# 👉 col2: Notes
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

# 👉 col1: Chat
with col1:
    st.header("💬 Chat")
    
    # ✅ 메시지 출력
    for idx, msg in enumerate(st.session_state.messages):
        st.chat_message(msg["role"]).write(msg["content"])
        if msg["role"] == "assistant" and idx in st.session_state.notes:
            st.markdown(
                f"<div style='margin-left:20px; color: gray;'><strong>메모:</strong> {st.session_state.notes[idx]}</div>",
                unsafe_allow_html=True
            )

# ✅ Chat 메시지 출력이 끝난 후, 반드시 맨 아래에 input 창
user_input = st.chat_input("메시지를 입력하세요…")

if user_input:
    st.session_state.messages.append({'role': 'user', 'content': user_input})

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
