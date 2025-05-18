import streamlit as st
from openai import OpenAI

# 페이지 설정
st.set_page_config(layout="wide", page_title="ChatGPT + Notes")

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=st.secrets['OPENAI_API_KEY'])

# 세션 상태 초기화
if 'messages' not in st.session_state:
    st.session_state.messages = []   # [{'role':'user'/'assistant','content': str}]
if 'notes' not in st.session_state:
    st.session_state.notes = {}      # {assistant_msg_index: note_text}
if 'book_context' not in st.session_state:
    st.session_state.book_context = ""  # 책 내용 업로드용

# 기본 책 요약 (엄마 사용법)
DEFAULT_SYSTEM_PROMPT = """
너는 초등학생의 독서활동을 돕는 따뜻하고 공감가는 어시스턴트입니다.
지금부터 너에게 책 《엄마 사용법》과 관련된 질문을 할 거예요.

《엄마 사용법》은 엄마와의 일상을 '사용 설명서'로 풀어내며 가족 간의 소통과 이해를 그린 따뜻한 이야기입니다.
주인공은 엄마가 자신을 잘 이해해주지 못한다고 느끼고, 엄마에게 자신의 사용법을 알려주려는 마음으로 설명서를 씁니다.

책의 주제는 가족 간의 이해, 감정 표현, 사랑의 방식입니다.
"""

# 자동 프롬프트 구성 함수
def build_prompt(user_input):
    if "엄마 사용법" in user_input:
        return (
            "초등학생이 《엄마 사용법》이라는 책을 읽은 뒤 친구와 함께 자연스럽게 주고받을 수 있는 대화를 만들어줘. "
            "책의 내용을 바탕으로 감정을 나누거나 서로 공감할 수 있는 질문과 대답을 다섯 쌍 정도 예시로 보여줘. "
            "각 대화는 A와 B로 나눠서 실제 친구처럼 이야기하듯 구성해줘. "
            "책의 주제(가족, 감정 표현, 엄마를 이해하는 마음 등)를 반영하고, 너무 어렵지 않게, 따뜻하고 공감되는 분위기로 써줘. "
            "중간중간 이모지(예: 📖, 💬)도 넣어줘."
        )
    return user_input

# 2:1 레이아웃
col1, col2 = st.columns([2, 1])

# 우측: 메모 패널
with col2:
    st.header("📝 Notes")

    uploaded = st.file_uploader("📘 책 요약 텍스트 파일 업로드", type="txt")
    if uploaded:
        st.session_state.book_context = uploaded.read().decode("utf-8")
        st.success("책 요약이 업로드되었습니다!")

    if st.session_state.messages:
        assistant_idxs = [i for i, m in enumerate(st.session_state.messages) if m['role']=='assistant']
        options = [f"{idx+1}. {st.session_state.messages[idx]['content'][:30]}…" for idx in assistant_idxs]
        choice = st.selectbox("메모할 메시지 선택", options)
        sel_idx = assistant_idxs[options.index(choice)]
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
        full = "\n".join(lines).strip()
        st.download_button(
            label="📥 Download All",
            data=full,
            file_name="conversation_with_notes.txt",
            mime="text/plain"
        )

    # 대화 및 메모 표시
    for idx, msg in enumerate(st.session_state.messages):
        st.chat_message(msg['role']).write(msg['content'])
        if msg['role']=='assistant' and idx in st.session_state.notes:
            st.markdown(
                f"<div style='margin-left:20px;color:gray;'><strong>메모:</strong> {st.session_state.notes[idx]}</div>",
                unsafe_allow_html=True
            )

    # 입력창을 채팅 내용 아래에 배치
    user_input = st.chat_input("메시지를 입력하세요…")
    if user_input:
        st.session_state.messages.append({'role':'user','content':user_input})

        # 최종 system prompt 구성
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
        st.session_state.messages.append({'role':'assistant','content':resp.choices[0].message.content})
