import streamlit as st
from openai import OpenAI

# ─── 페이지 설정 ───────────────────────────────────────
st.set_page_config(layout="wide", page_title="Chat & Notes")

# ─── OpenAI 클라이언트 초기화 ─────────────────────────
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ─── 세션 상태 초기화 ─────────────────────────────────
if "messages" not in st.session_state:
    # messages: list of dicts {"role": "user"/"assistant", "content": "..."}
    st.session_state.messages = []
if "notes" not in st.session_state:
    # notes: dict mapping message index (int) → str
    st.session_state.notes = {}

# ─── GPT 호출 함수 ─────────────────────────────────────
def query_gpt(user_text: str):
    # system + 기존 대화 + 새로운 user 메시지
    convo = [{"role":"system","content":"You are a helpful assistant."}]
    convo += [{"role":m["role"], "content":m["content"]} for m in st.session_state.messages]
    convo.append({"role":"user","content":user_text})
    res = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=convo
    )
    return res.choices[0].message.content

# ─── 레이아웃: 좌측(2) / 우측(1) ────────────────────────
col1, col2 = st.columns([2,1])

with col1:
    st.header("💬 Chat")
    # 이전 대화 모두 렌더
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    # 입력창
    prompt = st.chat_input("메시지를 입력하세요…")
    if prompt:
        # 사용자 메시지 저장
        st.session_state.messages.append({"role":"user","content":prompt})
        # GPT 응답
        with st.spinner("GPT가 응답 중…"):
            answer = query_gpt(prompt)
        st.session_state.messages.append({"role":"assistant","content":answer})
        # 페이지 새로고침 대신 rerun
        st.experimental_rerun()

with col2:
    st.header("📝 Notes")
    if not st.session_state.messages:
        st.info("왼쪽에서 대화를 시작해보세요.")
    else:
        # 메시지 선택용 드롭다운
        opts = [
            f"{i+1}. [{m['role']}] {m['content'][:30]}{'…' if len(m['content'])>30 else ''}"
            for i,m in enumerate(st.session_state.messages)
        ]
        sel = st.selectbox("메시지 선택", opts, index=0)
        idx = opts.index(sel)
        # 현재 선택된 메시지에 대한 메모 로드
        initial = st.session_state.notes.get(idx, "")
        note = st.text_area("메모 작성", value=initial, height=200)
        if st.button("메모 저장"):
            st.session_state.notes[idx] = note
            st.success("저장되었습니다!")

    st.markdown("---")
    # 모든 메모 보기
    if st.session_state.notes:
        st.subheader("저장된 메모들")
        for i, txt in st.session_state.notes.items():
            msg = st.session_state.messages[i]["content"]
            st.markdown(f"**{i+1}. {msg[:40]}…**  \n{txt}")
