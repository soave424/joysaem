import streamlit as st

# 페이지 설정 - 반드시 다른 st 명령어보다 먼저 와야 함
st.set_page_config(page_title="연구회 운영 나눔", layout="wide", initial_sidebar_state="collapsed")

import pandas as pd
import datetime
import uuid
import os
import json

# 데이터 파일 경로 설정
DATA_FILE = "comments.csv"

# 태그 목록 정의 및 태그별 색상 설정
TAG_COLORS = {
    "공개": "#28a745",  # 녹색
    "비공개": "#dc3545",  # 빨간색
    "참여": "#007bff",  # 파란색
    "연구": "#6610f2",  # 보라색
    "소통": "#17a2b8",  # 청록색
    "응원": "#ffc107",  # 노란색
    "운영노하우": "#fd7e14",  # 주황색
    "정정요구": "#e83e8c",  # 분홍색
    "질문": "#20c997",  # 민트색
    "추가의견": "#6c757d"   # 회색
}

# 관리자 여부를 저장할 전역 변수
IS_ADMIN = False

# CSS 스타일 정의
def get_tag_style(tag):
    color = TAG_COLORS.get(tag, "#6c757d")
    return f"""
    <span style="
        background-color: {color}; 
        color: white; 
        padding: 2px 6px; 
        border-radius: 10px; 
        font-size: 0.8em; 
        margin-right: 5px;
    ">
        {tag}
    </span>
    """

# 태그를 HTML로 반환 (가로 정렬 포함)
def tags_to_html(tags_list):
    if not tags_list:
        return "태그 없음"
    html_tags = "".join([get_tag_style(tag) for tag in tags_list])
    return f"""
    <div style='display: flex; flex-wrap: wrap; gap: 5px; margin-bottom: 5px;'>
        {html_tags}
    </div>
    """

# JSON 문자열 -> 리스트
def parse_tags(tags_json):
    try:
        if pd.isna(tags_json) or tags_json == "":
            return []
        return json.loads(tags_json)
    except:
        return []

# 태그 필터 버튼 생성 함수
def create_tag_filters(session_key):
    tag_list = list(TAG_COLORS.keys())
    if not IS_ADMIN:
        tag_list = [tag for tag in tag_list if tag not in ["비공개", "응원"]]

    if session_key not in st.session_state:
        st.session_state[session_key] = ["모든 태그"]

    cols = st.columns(len(tag_list) + 1)

    if cols[0].button("모든 태그", key=f"all_tags_{session_key}", use_container_width=True, type="primary" if "모든 태그" in st.session_state[session_key] else "secondary"):
        st.session_state[session_key] = ["모든 태그"]
        st.rerun()

    for i, tag in enumerate(tag_list):
        if cols[i + 1].button(tag, key=f"{session_key}_{tag}", use_container_width=True, type="primary" if tag in st.session_state[session_key] else "secondary"):
            if "모든 태그" in st.session_state[session_key]:
                st.session_state[session_key] = [tag]
            else:
                if tag in st.session_state[session_key]:
                    st.session_state[session_key].remove(tag)
                else:
                    st.session_state[session_key].append(tag)
                if not st.session_state[session_key]:
                    st.session_state[session_key] = ["모든 태그"]
            st.rerun()

    return st.session_state[session_key]

# 데이터 초기화
def initialize_data():
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=["id", "name", "comment", "tags", "timestamp", "approved"])
        df.to_csv(DATA_FILE, index=False)
        return df
    else:
        df = pd.read_csv(DATA_FILE)
        if "tags" not in df.columns:
            df["tags"] = df.get("tag", "[]").apply(lambda x: json.dumps([x]) if isinstance(x, str) else "[]")
            if "tag" in df.columns:
                df = df.drop(columns=["tag"])
        return df

# 저장 함수
def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# 비밀번호 확인
def check_password():
    global IS_ADMIN
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False

    if st.session_state.password_correct:
        IS_ADMIN = True
        return True

    password = st.sidebar.text_input("관리자 비밀번호를 입력하세요", type="password")
    if password == "admin123":
        st.session_state.password_correct = True
        IS_ADMIN = True
        return True
    elif password:
        st.sidebar.error("비밀번호가 일치하지 않습니다")
        return False
    return False

# 사용자 페이지
def user_view(df):
    st.subheader("의견 공유")
    if st.button("🔄 새로고침"):
        st.rerun()

    with st.form("comment_form"):
        name = st.text_input("이름(선택)")
        comment = st.text_area("내용")
        available_tags = [tag for tag in TAG_COLORS.keys() if IS_ADMIN or tag not in ["비공개", "응원"]]
        selected_tags = st.multiselect("태그 선택 (여러 개 선택 가능)", available_tags)
        submitted = st.form_submit_button("제출")

        if submitted and comment:
            new_comment = {
                "id": str(uuid.uuid4()),
                "name": name if name else "익명",
                "comment": comment,
                "tags": json.dumps(selected_tags),
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "approved": False
            }
            df = pd.concat([df, pd.DataFrame([new_comment])], ignore_index=True)
            save_data(df)
            st.success("글이 제출되었습니다. 관리자 승인 후 게시됩니다.")
            st.rerun()

    st.subheader("승인된 글")
    approved_comments = df[df["approved"] == True].sort_values(by="timestamp", ascending=False)
    if approved_comments.empty:
        st.info("아직 승인된 글이 없습니다.")
    else:
        st.write("태그로 필터링:")
        filter_tags = create_tag_filters("filter_tags")
        if "모든 태그" in filter_tags:
            filtered_comments = approved_comments
        else:
            filtered_comments = approved_comments[approved_comments["tags"].apply(lambda x: any(tag in parse_tags(x) for tag in filter_tags))]

        if filtered_comments.empty:
            st.info("해당 태그의 승인된 글이 없습니다.")
        else:
            for _, row in filtered_comments.iterrows():
                with st.container():
                    st.markdown(f"**{row['name']}** - {row['timestamp']}")
                    tags_list = parse_tags(row['tags'])
                    st.markdown(tags_to_html(tags_list), unsafe_allow_html=True)
                    st.markdown(f"{row['comment']}")
                    st.markdown("---")

# 관리자 페이지
def admin_view(df):
    st.subheader("관리자 페이지 - 글 관리")
    pending_tab, approved_tab = st.tabs(["승인 대기 글", "승인된 글"])

    with pending_tab:
        pending_comments = df[df["approved"] == False]
        st.write("태그로 필터링:")
        filter_tags_pending = create_tag_filters("filter_tags_pending")
        filtered_pending = pending_comments if "모든 태그" in filter_tags_pending else pending_comments[pending_comments["tags"].apply(lambda x: any(tag in parse_tags(x) for tag in filter_tags_pending))]

        if filtered_pending.empty:
            st.info("승인 대기 중인 글이 없습니다.")
        else:
            for idx, row in filtered_pending.iterrows():
                with st.container():
                    st.markdown(f"**{row['name']}** - {row['timestamp']}")
                    tags_list = parse_tags(row['tags'])
                    st.markdown(tags_to_html(tags_list), unsafe_allow_html=True)
                    st.markdown(f"{row['comment']}")
                    btn_col1, btn_col2 = st.columns([1, 1])
                    with btn_col1:
                        if st.button("✅ 승인", key=f"approve_{row['id']}", use_container_width=True):
                            df.at[idx, "approved"] = True
                            save_data(df)
                            st.rerun()
                    with btn_col2:
                        if st.button("🗑️ 삭제", key=f"delete_{row['id']}", use_container_width=True):
                            df = df.drop(idx)
                            save_data(df)
                            st.rerun()
                    st.markdown("---")

    with approved_tab:
        approved_comments = df[df["approved"] == True]
        st.write("태그로 필터링:")
        filter_tags_approved = create_tag_filters("filter_tags_approved")
        filtered_approved = approved_comments if "모든 태그" in filter_tags_approved else approved_comments[approved_comments["tags"].apply(lambda x: any(tag in parse_tags(x) for tag in filter_tags_approved))]

        if filtered_approved.empty:
            st.info("승인된 글이 없습니다.")
        else:
            for idx, row in filtered_approved.iterrows():
                with st.container():
                    st.markdown(f"**{row['name']}** - {row['timestamp']}")
                    tags_list = parse_tags(row['tags'])
                    st.markdown(tags_to_html(tags_list), unsafe_allow_html=True)
                    st.markdown(f"{row['comment']}")
                    if st.button("🗑️ 삭제", key=f"delete_approved_{row['id']}", use_container_width=True):
                        df = df.drop(idx)
                        save_data(df)
                        st.rerun()
                    st.markdown("---")

# 실행
def main():
    df = initialize_data()
    st.sidebar.title("관리자 페이지")
    is_admin = check_password() if st.sidebar.checkbox("관리자 로그인") else False
    st.title("연구회 운영 나눔")
    admin_view(df) if is_admin else user_view(df)

if __name__ == "__main__":
    main()
