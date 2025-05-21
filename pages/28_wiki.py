import streamlit as st
import pandas as pd
import datetime
import io
import openai
import os

st.set_page_config(page_title="공동 문서 빌더 MVP", layout="wide")
st.title("📝 공동 위키 빌더 MVP")

client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# 기준 문서 로드
navi_path = os.path.join("txt", "navi.txt")
if os.path.exists(navi_path):
    with open(navi_path, "r", encoding="utf-8") as f:
        reference_doc = f.read()
else:
    reference_doc = ""

st.subheader("1. 블록 입력")

col1, col2 = st.columns([1, 2])

with col1:
    title = st.text_input("제목", placeholder="예: 세종대왕의 업적")
    author = st.text_input("작성자", placeholder="예: 홍길동")
    source = st.text_input("출처", placeholder="예: 한국역사문화대백과사전")
    uploaded_file = st.file_uploader("내용을 담은 텍스트 파일 업로드", type="txt")

with col2:
    if uploaded_file is not None:
        content = uploaded_file.read().decode("utf-8")
    else:
        content = st.text_area("내용", height=300, placeholder="조사한 내용을 여기에 입력하거나 텍스트 파일을 업로드하세요.")

def evaluate_accuracy(content):
    if not reference_doc:
        return None, "기준 문서 없음"
    prompt = f"""
다음은 기준 문서입니다.

[기준 문서]
{reference_doc}

아래는 사용자 작성 블록입니다.

[사용자 블록]
{content}

사용자 블록이 기준 문서와 비교했을 때 정확한지 평가해 주세요.
- 1점 (매우 부정확)부터 5점 (매우 정확)까지 점수를 주세요.
- 이유도 1~2문장으로 설명해 주세요.

결과는 JSON 형식으로 주세요:
{{"accuracy_score": 정수, "reasoning": "설명"}}
"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        text = response.choices[0].message.content
        result = eval(text)
        return result.get("accuracy_score"), result.get("reasoning")
    except Exception as e:
        return None, str(e)

if st.button("블록 추가"):
    if not (title and author and content):
        st.warning("제목, 작성자, 내용은 필수 항목입니다.")
    else:
        score, reason = evaluate_accuracy(content)
        new_block = {
            "제목": title,
            "작성자": author,
            "날짜": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "내용": content,
            "출처": source,
            "정확도(5점)": score,
            "평가 사유": reason
        }
        if "blocks" not in st.session_state:
            st.session_state.blocks = []
        st.session_state.blocks.append(new_block)
        st.success("블록이 추가되었습니다.")

st.divider()

st.subheader("2. 작성된 블록")

if "blocks" in st.session_state and st.session_state.blocks:
    df = pd.DataFrame(st.session_state.blocks)
    st.dataframe(df, use_container_width=True)

    selected_indices = st.multiselect("다운로드할 블록 선택", options=list(range(len(df))), format_func=lambda i: df.loc[i, "제목"])

    def build_txt(dataframe):
        lines = []
        for _, row in dataframe.iterrows():
            lines.append("##### BLOCK START #####")
            lines.append(f"제목: {row['제목']}")
            lines.append(f"작성자: {row['작성자']}")
            lines.append(f"날짜: {row['날짜']}")
            lines.append(f"출처: {row['출처']}")
            lines.append(f"정확도(5점): {row['정확도(5점)']}")
            lines.append(f"평가 사유: {row['평가 사유']}")
            lines.append("내용:")
            lines.append(row['내용'])
            lines.append("##### BLOCK END #####\n")
        return "\n".join(lines)

    if selected_indices:
        selected_df = df.loc[selected_indices]
        selected_txt = build_txt(selected_df)
        st.download_button(
            label="📥 선택된 블록 다운로드 (TXT)",
            data=selected_txt,
            file_name="selected_wiki_blocks.txt",
            mime="text/plain"
        )

    full_txt = build_txt(df)
    st.download_button(
        label="📥 전체 블록 다운로드 (TXT)",
        data=full_txt,
        file_name="wiki_blocks.txt",
        mime="text/plain"
    )

    # 삭제 기능
    delete_index = st.number_input("삭제할 블록 번호 입력 (0부터 시작)", min_value=0, max_value=len(df)-1, step=1)
    admin_code = st.text_input("관리코드 입력", type="password")
    if st.button("블록 삭제"):
        if admin_code == "z733":
            removed_block = st.session_state.blocks.pop(delete_index)
            st.success(f"'{removed_block['제목']}' 블록이 삭제되었습니다.")
        else:
            st.error("관리코드가 올바르지 않습니다.")
else:
    st.info("아직 추가된 블록이 없습니다.")
