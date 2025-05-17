import streamlit as st
from openai import OpenAI
import numpy as np
import re

# 페이지 설정
st.set_page_config(layout="wide", page_title="ChatGPT + Custom GPT + RAG + Notes")

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=st.secrets['OPENAI_API_KEY'])

# 세션 상태 초기화
if 'messages' not in st.session_state:
    st.session_state.messages = []      # List[{'role': str, 'content': str}]
if 'notes' not in st.session_state:
    st.session_state.notes = {}         # Dict[int, str]
if 'model_id' not in st.session_state:
    st.session_state.model_id = ''      # 선택된 커스텀 GPT ID or base model
if 'docs' not in st.session_state:
    st.session_state.docs = []          # List of document chunks
if 'embeddings' not in st.session_state:
    st.session_state.embeddings = []    # List of embedding vectors

# 유틸: 코사인 유사도
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)) if np.linalg.norm(a) and np.linalg.norm(b) else 0

# 사이드바: 문서 업로드 및 임베딩
st.sidebar.header("📚 Knowledge Upload")
uploaded = st.sidebar.file_uploader("Upload .txt or .md file", type=["txt", "md"])
if uploaded:
    text = uploaded.getvalue().decode('utf-8')
    chunks = [p.strip() for p in text.split("\n\n") if p.strip()]
    st.session_state.docs = chunks
    resp = client.embeddings.create(model="text-embedding-ada-002", input=chunks)
    st.session_state.embeddings = [np.array(d.embedding) for d in resp.data]
    st.sidebar.success(f"Indexed {len(chunks)} chunks.")

# 2:1 레이아웃
col1, col2 = st.columns([2, 1])

with col1:
    # 모델 ID 입력
    st.subheader("🔧 사용할 모델 선택")
    model_input = st.text_input(
        "모델 ID 또는 커스텀 GPT 링크 입력 (예: g-xxxxxx 또는 https://chat.openai.com/g/xxxxxx)",
        value=st.session_state.model_id
    )
    if model_input:
        m = re.search(r"/g/([\w-]+)", model_input)
        if m:
            st.session_state.model_id = m.group(1)
        elif model_input.startswith("g-") or model_input in ["gpt-3.5-turbo", "gpt-4"]:
            st.session_state.model_id = model_input
        else:
            st.error("유효한 모델 ID나 링크를 입력하세요.")
    if st.session_state.model_id:
        st.markdown(f"**선택된 모델 ID:** `{st.session_state.model_id}`")
    else:
        st.info("위에 모델 ID를 입력해야 대화를 시작할 수 있습니다.")

    # 헤더 + 다운로드
    hdr, btn = st.columns([8, 2])
    with hdr:
        st.header(f"💬 Chat ({st.session_state.model_id or '모델 미지정'})")
    with btn:
        if st.session_state.messages and st.session_state.model_id:
            lines = []
            for i, m in enumerate(st.session_state.messages):
                prefix = 'User:' if m['role']=='user' else 'AI:'
                lines.append(f"{prefix} {m['content']}")
                if m['role']=='assistant' and i in st.session_state.notes:
                    lines.append(f"메모: {st.session_state.notes[i]}")
                lines.append("")
            out = "\n".join(lines).strip()
            st.download_button("📥 Download All", data=out, file_name="chat_with_notes.txt")

    # 대화 및 메모 표시
    for idx, msg in enumerate(st.session_state.messages):
        st.chat_message(msg['role']).write(msg['content'])
        if msg['role']=='assistant' and idx in st.session_state.notes:
            note = st.session_state.notes[idx]
            st.markdown(
                f"<div style='margin-left:20px; color:gray;'><strong>메모:</strong> {note}</div>",
                unsafe_allow_html=True
            )

    # 채팅 입력 및 RAG
    if st.session_state.model_id:
        prompt = st.chat_input("메시지를 입력하세요…")
        if prompt:
            st.session_state.messages.append({'role':'user','content':prompt})
            # RAG
            if st.session_state.docs and st.session_state.embeddings:
                q_emb = np.array(client.embeddings.create(model="text-embedding-ada-002", input=[prompt]).data[0].embedding)
                sims = [cosine_similarity(q_emb, e) for e in st.session_state.embeddings]
                topk = np.argsort(sims)[-3:][::-1]
                context = "\n\n".join(st.session_state.docs[i] for i in topk)
                system_msg = {'role':'system','content':f"다음 문서를 참고하세요:\n{context}"}
            else:
                system_msg = {'role':'system','content':'You are a helpful assistant.'}
            with st.spinner("응답 생성 중…"):
                resp = client.chat.completions.create(
                    model=st.session_state.model_id,
                    messages=[system_msg] + st.session_state.messages
                )
            st.session_state.messages.append({'role':'assistant','content':resp.choices[0].message.content})

with col2:
    st.header("📝 Notes")
    if not st.session_state.messages:
        st.info("왼쪽에서 대화를 시작하세요.")
    else:
        ai_idx = [i for i, m in enumerate(st.session_state.messages) if m['role']=='assistant']
        labels = [f"{i+1}. {st.session_state.messages[i]['content'][:30]}..." for i in ai_idx]
        sel = st.selectbox("메모할 메시지 선택", labels)
        sel_idx = ai_idx[labels.index(sel)]
        existing = st.session_state.notes.get(sel_idx, "")
        note = st.text_area("메모 입력", value=existing, height=150)
        if st.button("저장 메모", key=f"save_{sel_idx}"):
            st.session_state.notes[sel_idx] = note
            st.experimental_rerun()