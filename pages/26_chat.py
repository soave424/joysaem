import streamlit as st
from openai import OpenAI
import numpy as np

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
    st.session_state.model_id = None    # 선택된 커스텀 GPT ID
if 'docs' not in st.session_state:
    st.session_state.docs = []          # List of document chunks
if 'embeddings' not in st.session_state:
    st.session_state.embeddings = []    # List of embedding vectors

# 유틸: 코사인 유사도
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)) if np.linalg.norm(a) and np.linalg.norm(b) else 0

# 문서 업로드 및 임베딩
st.sidebar.header("📚 Knowledge Upload")
uploaded = st.sidebar.file_uploader("Upload .txt or .md file for knowledge", type=["txt", "md"])
if uploaded:
    text = uploaded.getvalue().decode('utf-8')
    # 간단히 문단 단위로 분할
    chunks = [p for p in text.split("\n\n") if p.strip()]
    st.session_state.docs = chunks
    # 임베딩 생성
    resp = client.embeddings.create(
        model="text-embedding-ada-002",
        input=chunks
    )
    st.session_state.embeddings = [np.array(d.embedding) for d in resp.data]
    st.sidebar.success(f"Indexed {len(chunks)} chunks for retrieval.")

# 2:1 레이아웃
col1, col2 = st.columns([2, 1])

with col1:
    # 커스텀 GPT 선택
    st.subheader("🔧 내 커스텀 GPT 목록")
    try:
        gpt_list = client.gpts.list().data
        options = {g.name: g.id for g in gpt_list}
        choice = st.selectbox("사용할 커스텀 GPT 선택", list(options.keys()))
        st.session_state.model_id = options[choice]
        st.markdown(f"**선택된 모델 ID:** `{st.session_state.model_id}`")
    except Exception as e:
        st.error(f"커스텀 GPT 목록 로드 오류: {e}")
        st.stop()

    # 헤더 및 다운로드
    hdr, btn = st.columns([8,2])
    with hdr:
        st.header(f"💬 Chat ({choice})")
    with btn:
        if st.session_state.messages:
            # 합쳐서 다운로드
            lines = []
            for i,m in enumerate(st.session_state.messages):
                pref = 'User:' if m['role']=='user' else 'AI:'
                lines.append(f"{pref} {m['content']}")
                if m['role']=='assistant' and i in st.session_state.notes:
                    lines.append(f"메모: {st.session_state.notes[i]}")
                lines.append("")
            text_out = "\n".join(lines).strip()
            st.download_button("📥 Download All", data=text_out, file_name="chat_with_notes.txt")

    # 대화 및 메모 표시
    for idx,msg in enumerate(st.session_state.messages):
        st.chat_message(msg['role']).write(msg['content'])
        if msg['role']=='assistant' and idx in st.session_state.notes:
            note = st.session_state.notes[idx]
            st.markdown(f"<div style='margin-left:20px; color:gray;'><strong>메모:</strong> {note}</div>", unsafe_allow_html=True)

    # 사용자 입력 + RAG
    prompt = st.chat_input("메시지를 입력하세요…")
    if prompt:
        st.session_state.messages.append({'role':'user','content':prompt})
        # RAG context retrieval
        if st.session_state.docs and st.session_state.embeddings:
            q_emb = np.array(client.embeddings.create(model="text-embedding-ada-002", input=[prompt]).data[0].embedding)
            sims = [cosine_similarity(q_emb, e) for e in st.session_state.embeddings]
            topk = np.argsort(sims)[-3:][::-1]
            context = "\n\n".join([st.session_state.docs[i] for i in topk])
            system_msg = {'role':'system','content': f"다음 문서를 참고하여 답변하세요:\n{context}"}
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
        # AI 메시지 인덱스만
        ai_idx = [i for i,m in enumerate(st.session_state.messages) if m['role']=='assistant']
        labels = [f"{i+1}. {st.session_state.messages[i]['content'][:30]}..." for i in ai_idx]
        sel = st.selectbox("메모할 메시지 선택", labels)
        sel_idx = ai_idx[labels.index(sel)]
        existing = st.session_state.notes.get(sel_idx,"")
        note = st.text_area("메모 입력", value=existing, height=150)
        if st.button("저장 메모", key=f"save_{sel_idx}"):
            st.session_state.notes[sel_idx] = note
            st.experimental_rerun()
