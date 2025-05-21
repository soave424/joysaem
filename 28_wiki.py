import streamlit as st
import pandas as pd
import datetime
import io

st.set_page_config(page_title="공동 문서 빌더 MVP", layout="wide")
st.title("📝 공동 위키 빌더 MVP")

# 구글 시트 저장을 위한 준비는 추후에 연결

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

if st.button("블록 추가"):
    if not (title and author and content):
        st.warning("제목, 작성자, 내용은 필수 항목입니다.")
    else:
        new_block = {
            "제목": title,
            "작성자": author,
            "날짜": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "내용": content,
            "출처": source,
            "정확도(5점)": None,
            "평가 사유": None
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

    # TXT 포맷으로 변환
    txt_lines = []
    for i, row in df.iterrows():
        txt_lines.append(f"제목: {row['제목']}")
        txt_lines.append(f"작성자: {row['작성자']} | 날짜: {row['날짜']}")
        txt_lines.append(f"출처: {row['출처']}")
        txt_lines.append("내용:")
        txt_lines.append(row['내용'])
        txt_lines.append("정확도(5점): " + str(row['정확도(5점)']))
        txt_lines.append("평가 사유: " + str(row['평가 사유']))
        txt_lines.append("\n---\n")

    full_txt = "\n".join(txt_lines)

    st.download_button(
        label="📥 전체 블록 다운로드 (TXT)",
        data=full_txt,
        file_name="wiki_blocks.txt",
        mime="text/plain"
    )
else:
    st.info("아직 추가된 블록이 없습니다.")
