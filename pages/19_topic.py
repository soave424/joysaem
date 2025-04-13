import streamlit as st

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")


import pandas as pd
import datetime
import uuid
import os
import json


# 데이터 파일 경로 설정
DATA_FILE = "comments.csv"

# 태그 목록 정의
TAGS = ["공개", "비공개", "참여", "연구", "소통", "응원", "운영노하우", "정정요구", "질문", "추가의견"]

# 페이지 설정
st.set_page_config(page_title="댓글 게시판", layout="wide")

# 데이터 초기화 및 불러오기
def initialize_data():
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=["id", "name", "comment", "tags", "timestamp", "approved"])
        df.to_csv(DATA_FILE, index=False)
        return df
    else:
        df = pd.read_csv(DATA_FILE)
        # 기존 파일에 tags 열이 없으면 추가
        if "tags" not in df.columns:
            df["tags"] = df.get("tag", "[]").apply(lambda x: json.dumps([x]) if isinstance(x, str) else "[]")
            if "tag" in df.columns:
                df = df.drop(columns=["tag"])
        return df

# 데이터 저장 함수
def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# 비밀번호 확인 함수 (관리자 로그인용)
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False
    
    if st.session_state.password_correct:
        return True
    
    # 비밀번호 입력
    password = st.sidebar.text_input("관리자 비밀번호를 입력하세요", type="password")
    
    # 실제 구현 시에는 더 안전한 방법으로 비밀번호 확인
    if password == "admin123":  # 실제 구현 시 이 비밀번호를 변경하세요
        st.session_state.password_correct = True
        return True
    elif password:
        st.sidebar.error("비밀번호가 일치하지 않습니다")
        return False
    return False

# 태그 목록을 문자열로 변환
def tags_to_string(tags_list):
    if not tags_list:
        return "태그 없음"
    return ", ".join(tags_list)

# 태그 문자열(JSON)을 리스트로 변환
def parse_tags(tags_json):
    try:
        if pd.isna(tags_json) or tags_json == "":
            return []
        return json.loads(tags_json)
    except:
        return []

# 메인 애플리케이션
def main():
    # 데이터 불러오기
    df = initialize_data()
    
    # 사이드바에 관리자 로그인 옵션 추가
    st.sidebar.title("관리자 페이지")
    is_admin = check_password() if st.sidebar.checkbox("관리자 로그인") else False
    
    # 메인 페이지 타이틀
    st.title("댓글 게시판")
    
    # 관리자 모드
    if is_admin:
        admin_view(df)
    else:
        user_view(df)

# 사용자 페이지
def user_view(df):
    st.subheader("새 댓글 작성")
    
    with st.form("comment_form"):
        name = st.text_input("이름")
        comment = st.text_area("댓글")
        selected_tags = st.multiselect("태그 선택 (여러 개 선택 가능)", TAGS)
        submitted = st.form_submit_button("댓글 제출")
        
        if submitted and comment:  # 이름은 필수가 아님
            new_comment = {
                "id": str(uuid.uuid4()),
                "name": name if name else "익명",  # 이름이 없으면 "익명"으로 설정
                "comment": comment,
                "tags": json.dumps(selected_tags),  # 태그 리스트를 JSON 문자열로 저장
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "approved": False
            }
            
            df = pd.concat([df, pd.DataFrame([new_comment])], ignore_index=True)
            save_data(df)
            st.success("댓글이 제출되었습니다. 관리자 승인 후 게시됩니다.")
    
    # 승인된 댓글만 표시
    st.subheader("승인된 댓글")
    approved_comments = df[df["approved"] == True].sort_values(by="timestamp", ascending=False)
    
    if approved_comments.empty:
        st.info("아직 승인된 댓글이 없습니다.")
    else:
        # 태그별 필터링 옵션
        filter_tags = st.multiselect("태그로 필터링", ["모든 태그"] + TAGS, default=["모든 태그"])
        
        # "모든 태그"가 선택되었거나 아무것도 선택되지 않았을 때는 모든 댓글 표시
        if "모든 태그" in filter_tags or not filter_tags:
            filtered_comments = approved_comments
        else:
            # 선택된 태그 중 하나라도 포함된 댓글 필터링
            filtered_comments = approved_comments[approved_comments["tags"].apply(
                lambda x: any(tag in parse_tags(x) for tag in filter_tags)
            )]
        
        if filtered_comments.empty:
            st.info("해당 태그의 승인된 댓글이 없습니다.")
        else:
            for _, row in filtered_comments.iterrows():
                with st.container():
                    col1, col2 = st.columns([5, 1])
                    with col1:
                        st.markdown(f"**{row['name']}** - {row['timestamp']}")
                    with col2:
                        tags_list = parse_tags(row['tags'])
                        st.markdown(f"**태그: {tags_to_string(tags_list)}**")
                    st.markdown(f"{row['comment']}")
                    st.markdown("---")

# 관리자 페이지
def admin_view(df):
    st.subheader("관리자 페이지 - 댓글 관리")
    
    # 탭 생성
    pending_tab, approved_tab = st.tabs(["승인 대기 댓글", "승인된 댓글"])
    
    # 승인 대기 댓글 탭
    with pending_tab:
        pending_comments = df[df["approved"] == False]
        
        # 태그별 필터링 옵션
        filter_tags_pending = st.multiselect("태그로 필터링 (승인 대기)", ["모든 태그"] + TAGS, default=["모든 태그"], key="pending_filter")
        
        # "모든 태그"가 선택되었거나 아무것도 선택되지 않았을 때는 모든 댓글 표시
        if "모든 태그" in filter_tags_pending or not filter_tags_pending:
            filtered_pending = pending_comments
        else:
            # 선택된 태그 중 하나라도 포함된 댓글 필터링
            filtered_pending = pending_comments[pending_comments["tags"].apply(
                lambda x: any(tag in parse_tags(x) for tag in filter_tags_pending)
            )]
        
        if filtered_pending.empty:
            st.info("승인 대기 중인 댓글이 없습니다.")
        else:
            for idx, row in filtered_pending.iterrows():
                with st.container():
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        tags_list = parse_tags(row['tags'])
                        st.markdown(f"**{row['name']}** - {row['timestamp']} - **태그: {tags_to_string(tags_list)}**")
                        st.markdown(f"{row['comment']}")
                    
                    with col2:
                        if st.button("승인", key=f"approve_{row['id']}"):
                            df.at[idx, "approved"] = True
                            save_data(df)
                            st.rerun()
                    
                    with col3:
                        if st.button("삭제", key=f"delete_{row['id']}"):
                            df = df.drop(idx)
                            save_data(df)
                            st.rerun()
                    
                    st.markdown("---")
    
    # 승인된 댓글 탭
    with approved_tab:
        approved_comments = df[df["approved"] == True]
        
        # 태그별 필터링 옵션
        filter_tags_approved = st.multiselect("태그로 필터링 (승인됨)", ["모든 태그"] + TAGS, default=["모든 태그"], key="approved_filter")
        
        # "모든 태그"가 선택되었거나 아무것도 선택되지 않았을 때는 모든 댓글 표시
        if "모든 태그" in filter_tags_approved or not filter_tags_approved:
            filtered_approved = approved_comments
        else:
            # 선택된 태그 중 하나라도 포함된 댓글 필터링
            filtered_approved = approved_comments[approved_comments["tags"].apply(
                lambda x: any(tag in parse_tags(x) for tag in filter_tags_approved)
            )]
        
        if filtered_approved.empty:
            st.info("승인된 댓글이 없습니다.")
        else:
            for idx, row in filtered_approved.iterrows():
                with st.container():
                    col1, col2 = st.columns([5, 1])
                    
                    with col1:
                        tags_list = parse_tags(row['tags'])
                        st.markdown(f"**{row['name']}** - {row['timestamp']} - **태그: {tags_to_string(tags_list)}**")
                        st.markdown(f"{row['comment']}")
                    
                    with col2:
                        if st.button("삭제", key=f"delete_approved_{row['id']}"):
                            df = df.drop(idx)
                            save_data(df)
                            st.rerun()
                    
                    st.markdown("---")

if __name__ == "__main__":
    main()