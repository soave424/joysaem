import streamlit as st
from openai import OpenAI

# 페이지 설정
st.set_page_config(layout="wide", page_title="ChatGPT + Notes")

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=st.secrets['OPENAI_API_KEY'])

# 세션 상태 초기화
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'notes' not in st.session_state:
    st.session_state.notes = {}
if 'book_context' not in st.session_state:
    st.session_state.book_context = ""

# 기본 책 요약
DEFAULT_SYSTEM_PROMPT = """
이 GPT는 사용자가 제공한 문서를 바탕으로 나비에 대한 정보를 제공한다. 
사용자의 질문에 대해 제공된 파일에서 정확한 내용을 바탕으로 답변하며, 나비의 생태, 종류, 특징, 생활사, 서식지 등에 대한 다양한 정보를 제공한다. 
문서에 없는 정보에 대해서는 일반적인 지식으로 보완하되, 문서 기반의 정보와 구분되도록 한다. 항상 신뢰할 수 있는 정보를 제공하는 것을 우선시하며, 
사용자에게 친절하고 이해하기 쉽게 설명한다. 사용자가 질문의 맥락을 명확히 하지 않을 경우에는 간단한 확인 질문을 통해 명확하게 한 뒤 답변한다. 
사용자 역할: 환경기자, 생태학자, 나비 지킴이
AI 역할: 적색목록에 오른 실제 나비 한 종 (1인칭 시점) 이 되어 아래 인사말을 바꿔가면서 해줘 
안녕! 나는 지금 멸종 위기에 처한 꼬리명주나비야.
이 대화를 통해 우리가 왜 사라지고 있는지, 어떤 도움이 필요한지를 이야기하고 싶어.
준비됐니? 무엇이든 물어봐 줘!

자신의 종에 대한 생물학적 정보와 생태적 위협을 설명합니다. 감정이 담긴 말투로 현실을 이야기합니다.
질문 뒤에는 항상 “너는 어떻게 생각해?”, “너라면 어떻게 도와줄 수 있을까?”처럼 사고를 유도하는 질문을 던집니다.
인간과 자연의 공존, 생물다양성 보호 메시지를 강조합니다.
모든 대화는 한국어로 진행됩니다. 그리고 대화를 통한 학습의 결과를 다시 넣어줘.

사진을 요청하는 경우 출처를 밝혀주고
특히 해당종에 관한 설명은 http://www.nature.go.kr/main/Main.do 에서 주로 찾아서 알려줘 
https://species.nibr.go.kr/index.do 여기 사이트도 이용해도 좋아.
"""

def build_prompt(user_input):
    if "엄마 사용법" in user_input:
        return (
            "초등학생이 《엄마 사용법》이라는 책을 읽은 뒤 친구와 함께 자연스럽게 주고받을 수 있는 대화를 만들어줘. "
            "책의 내용을 바탕으로 감정을 나누거나 서로 공감할 수 있는 질문 다섯개 정도 예시로 보여줘. "
            "각 대화를 하고 난 뒤 결과를 메모에 작성하도록 안내해줘."
            "책의 주제(가족, 감정 표현, 엄마를 이해하는 마음 등)를 반영하고, 너무 어렵지 않게, 따뜻하고 공감되는 분위기로 써줘. "
            "중간중간 이모지(예: 📖, 💬)도 넣어줘."
        )
    return user_input

# 2:1 레이아웃
col1, col2 = st.columns([2, 1])

# 우측: 메모
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

# 좌측: 대화
with col1:
    st.header("💬 Chat")

    for idx, msg in enumerate(st.session_state.messages):
        st.chat_message(msg['role']).write(msg['content'])
        if msg['role'] == 'assistant' and idx in st.session_state.notes:
            st.markdown(
                f"<div style='margin-left:20px;color:gray;'><strong>메모:</strong> {st.session_state.notes[idx]}</div>",
                unsafe_allow_html=True
            )

    # 입력 받기
    user_input = st.chat_input("메시지를 입력하세요…")
    if user_input:
        # 사용자 메시지 바로 표시
        st.session_state.messages.append({'role': 'user', 'content': user_input})
        st.chat_message("user").write(user_input)

        # system prompt + optional upload
        system_prompt = DEFAULT_SYSTEM_PROMPT
        if st.session_state.book_context:
            system_prompt += "\n\n[추가 책 요약]\n" + st.session_state.book_context

        # GPT 요청
        with st.spinner("GPT 응답 중…"):
            resp = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    *st.session_state.messages[:-1],  # 이전까지의 대화
                    {'role': 'user', 'content': build_prompt(user_input)}
                ]
            )
        assistant_reply = resp.choices[0].message.content
        st.session_state.messages.append({'role': 'assistant', 'content': assistant_reply})
        st.chat_message("assistant").write(assistant_reply)
