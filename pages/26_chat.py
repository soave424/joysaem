import streamlit as st
from openai import OpenAI

# 페이지 설정
st.set_page_config(layout="wide", page_title="ChatGPT + Notes")

# OpenAI 클라이언트
client = OpenAI(api_key=st.secrets['OPENAI_API_KEY'])

# 세션 상태 초기화
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'notes' not in st.session_state:
    st.session_state.notes = {}
if 'book_context' not in st.session_state:
    st.session_state.book_context = ""

DEFAULT_SYSTEM_PROMPT = """..."""  # 생략 가능

def build_prompt(user_input):
    if "엄마 사용법" in user_input:
        return (
            "초등학생이 《엄마 사용법》이라는 책을 읽은 뒤 친구와 함께 자연스럽게 주고받을 수 있는 대화를 만들어줘. "
        )
    return user_input

# ✅ 스타일: 여백 제거 및 고정 영역 스타일링
st.markdown("""
    <style>
    /* 입력창 위 불필요한 여백 제거 */
    div.st-emotion-cache-qcqlej {
        margin: 0px !important;
        padding: 0px !important;
        height: 0px !important;
        min-height: 0px !important;
    }

    /* 입력창 전체 주변 여백 제거 */
    section.main > div:has(div[data-testid="stChatInput"]) {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }

    /* 오른쪽 col2 영역 상단 고정 */
    div[data-testid="column"] div:has(.element-container) {
        position: sticky;
        top: 0;
        z-index: 1;
        background-color: white;
        padding-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# ✅ 레이아웃 구성: col1 = 채팅, col2 = 메모
col1, col2 = st.columns([3, 1], gap="small")

# 👉 오른쪽: Notes 패널 (상단 고정됨)
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

# 👉 왼쪽: Chat 영역 (스크롤 가능)
with col1:
    st.header("💬 Chat")
    chat_area = st.container()
    with chat_area:
        for idx, msg in enumerate(st.session_state.messages):
            st.chat_message(msg['role']).write(msg['content'])
            if msg['role'] == 'assistant' and idx in st.session_state.notes:
                st.markdown(
                    f"<div style='margin-left:20px;color:gray;'><strong>메모:</strong> {st.session_state.notes[idx]}</div>",
                    unsafe_allow_html=True
                )

# ✅ 하단 고정 입력창
user_input = st.chat_input("메시지를 입력하세요…")
if user_input:
    st.session_state.messages.append({'role': 'user', 'content': user_input})
    st.chat_message("user").write(user_input)

    # GPT 호출
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
