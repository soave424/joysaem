import streamlit as st

# 페이지 설정 - 반드시 다른 st 명령어보다 먼저 와야 함
st.set_page_config(page_title="댓글 게시판", layout="wide")

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

TAGS = list(TAG_COLORS.keys())

# CSS 스타일 정의
def get_tag_style(tag):
    """태그에 맞는 CSS 스타일을 반환합니다."""
    color = TAG_COLORS.get(tag, "#6c757d")  # 기본값은 회색
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

# 태그 목록을 HTML로 변환
def tags_to_html(tags_list):
    if not tags_list:
        return "태그 없음"
    html_tags = "".join([get_tag_style(tag) for tag in tags_list])
    return html_tags

# 태그 문자열(JSON)을 리스트로 변환
def parse_tags(tags_json):
    try:
        if pd.isna(tags_json) or tags_json == "":
            return []
        return json.loads(tags_json)
    except:
        return []

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
        # 색상이 있는 태그 필터 버튼들 표시
        st.write("태그로 필터링:")
        cols = st.columns(5)  # 한 줄에 5개씩 태그 버튼 표시
        
        # 세션 상태에 필터 태그 저장
        if "filter_tags" not in st.session_state:
            st.session_state.filter_tags = ["모든 태그"]
            
        # "모든 태그" 버튼
        if cols[0].button("모든 태그", key="all_tags", 
                          use_container_width=True,
                          type="primary" if "모든 태그" in st.session_state.filter_tags else "secondary"):
            st.session_state.filter_tags = ["모든 태그"]
            st.rerun()
            
        # 각 태그별 버튼 생성
        for i, tag in enumerate(TAGS):
            col_idx = (i + 1) % 5  # 한 줄에 5개씩
            if cols[col_idx].button(tag, key=f"tag_{tag}", 
                                  use_container_width=True,
                                  type="primary" if tag in st.session_state.filter_tags else "secondary"):
                if "모든 태그" in st.session_state.filter_tags:
                    st.session_state.filter_tags = [tag]
                else:
                    if tag in st.session_state.filter_tags:
                        st.session_state.filter_tags.remove(tag)
                    else:
                        st.session_state.filter_tags.append(tag)
                    
                    if not st.session_state.filter_tags:  # 선택된 태그가 없으면
                        st.session_state.filter_tags = ["모든 태그"]
                        
                st.rerun()
        
        # 현재 적용된 필터 표시
        if st.session_state.filter_tags != ["모든 태그"]:
            filter_html = "적용된 필터: " + "".join([get_tag_style(tag) for tag in st.session_state.filter_tags])
            st.markdown(filter_html, unsafe_allow_html=True)
            
        # 필터링 적용
        if "모든 태그" in st.session_state.filter_tags:
            filtered_comments = approved_comments
        else:
            # 선택된 태그 중 하나라도 포함된 댓글 필터링
            filtered_comments = approved_comments[approved_comments["tags"].apply(
                lambda x: any(tag in parse_tags(x) for tag in st.session_state.filter_tags)
            )]
        
        if filtered_comments.empty:
            st.info("해당 태그의 승인된 댓글이 없습니다.")
        else:
            for _, row in filtered_comments.iterrows():
                with st.container():
                    st.markdown(f"**{row['name']}** - {row['timestamp']}")
                    
                    # 태그 표시
                    tags_list = parse_tags(row['tags'])
                    st.markdown(tags_to_html(tags_list), unsafe_allow_html=True)
                    
                    # 댓글 내용
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
        
        # 색상이 있는 태그 필터 버튼들 표시
        st.write("태그로 필터링:")
        cols = st.columns(5)  # 한 줄에 5개씩 태그 버튼 표시
        
        # 세션 상태에 필터 태그 저장 (승인 대기용)
        if "filter_tags_pending" not in st.session_state:
            st.session_state.filter_tags_pending = ["모든 태그"]
            
        # "모든 태그" 버튼
        if cols[0].button("모든 태그", key="all_tags_pending", 
                          use_container_width=True,
                          type="primary" if "모든 태그" in st.session_state.filter_tags_pending else "secondary"):
            st.session_state.filter_tags_pending = ["모든 태그"]
            st.rerun()
            
        # 각 태그별 버튼 생성
        for i, tag in enumerate(TAGS):
            col_idx = (i + 1) % 5  # 한 줄에 5개씩
            if cols[col_idx].button(tag, key=f"tag_pending_{tag}", 
                                  use_container_width=True,
                                  type="primary" if tag in st.session_state.filter_tags_pending else "secondary"):
                if "모든 태그" in st.session_state.filter_tags_pending:
                    st.session_state.filter_tags_pending = [tag]
                else:
                    if tag in st.session_state.filter_tags_pending:
                        st.session_state.filter_tags_pending.remove(tag)
                    else:
                        st.session_state.filter_tags_pending.append(tag)
                    
                    if not st.session_state.filter_tags_pending:  # 선택된 태그가 없으면
                        st.session_state.filter_tags_pending = ["모든 태그"]
                        
                st.rerun()
        
        # 현재 적용된 필터 표시
        if st.session_state.filter_tags_pending != ["모든 태그"]:
            filter_html = "적용된 필터: " + "".join([get_tag_style(tag) for tag in st.session_state.filter_tags_pending])
            st.markdown(filter_html, unsafe_allow_html=True)
            
        # 필터링 적용
        if "모든 태그" in st.session_state.filter_tags_pending:
            filtered_pending = pending_comments
        else:
            # 선택된 태그 중 하나라도 포함된 댓글 필터링
            filtered_pending = pending_comments[pending_comments["tags"].apply(
                lambda x: any(tag in parse_tags(x) for tag in st.session_state.filter_tags_pending)
            )]
        
        if filtered_pending.empty:
            st.info("승인 대기 중인 댓글이 없습니다.")
        else:
            for idx, row in filtered_pending.iterrows():
                with st.container():
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        st.markdown(f"**{row['name']}** - {row['timestamp']}")
                        
                        # 태그 표시
                        tags_list = parse_tags(row['tags'])
                        st.markdown(tags_to_html(tags_list), unsafe_allow_html=True)
                        
                        # 댓글 내용
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
        
        # 색상이 있는 태그 필터 버튼들 표시
        st.write("태그로 필터링:")
        cols = st.columns(5)  # 한 줄에 5개씩 태그 버튼 표시
        
        # 세션 상태에 필터 태그 저장 (승인된 댓글용)
        if "filter_tags_approved" not in st.session_state:
            st.session_state.filter_tags_approved = ["모든 태그"]
            
        # "모든 태그" 버튼
        if cols[0].button("모든 태그", key="all_tags_approved", 
                          use_container_width=True,
                          type="primary" if "모든 태그" in st.session_state.filter_tags_approved else "secondary"):
            st.session_state.filter_tags_approved = ["모든 태그"]
            st.rerun()
            
        # 각 태그별 버튼 생성
        for i, tag in enumerate(TAGS):
            col_idx = (i + 1) % 5  # 한 줄에 5개씩
            if cols[col_idx].button(tag, key=f"tag_approved_{tag}", 
                                  use_container_width=True,
                                  type="primary" if tag in st.session_state.filter_tags_approved else "secondary"):
                if "모든 태그" in st.session_state.filter_tags_approved:
                    st.session_state.filter_tags_approved = [tag]
                else:
                    if tag in st.session_state.filter_tags_approved:
                        st.session_state.filter_tags_approved.remove(tag)
                    else:
                        st.session_state.filter_tags_approved.append(tag)
                    
                    if not st.session_state.filter_tags_approved:  # 선택된 태그가 없으면
                        st.session_state.filter_tags_approved = ["모든 태그"]
                        
                st.rerun()
        
        # 현재 적용된 필터 표시
        if st.session_state.filter_tags_approved != ["모든 태그"]:
            filter_html = "적용된 필터: " + "".join([get_tag_style(tag) for tag in st.session_state.filter_tags_approved])
            st.markdown(filter_html, unsafe_allow_html=True)
            
        # 필터링 적용
        if "모든 태그" in st.session_state.filter_tags_approved:
            filtered_approved = approved_comments
        else:
            # 선택된 태그 중 하나라도 포함된 댓글 필터링
            filtered_approved = approved_comments[approved_comments["tags"].apply(
                lambda x: any(tag in parse_tags(x) for tag in st.session_state.filter_tags_approved)
            )]
        
        if filtered_approved.empty:
            st.info("승인된 댓글이 없습니다.")
        else:
            for idx, row in filtered_approved.iterrows():
                with st.container():
                    col1, col2 = st.columns([5, 1])
                    
                    with col1:
                        st.markdown(f"**{row['name']}** - {row['timestamp']}")
                        
                        # 태그 표시
                        tags_list = parse_tags(row['tags'])
                        st.markdown(tags_to_html(tags_list), unsafe_allow_html=True)
                        
                        # 댓글 내용
                        st.markdown(f"{row['comment']}")
                    
                    with col2:
                        if st.button("삭제", key=f"delete_approved_{row['id']}"):
                            df = df.drop(idx)
                            save_data(df)
                            st.rerun()
                    
                    st.markdown("---")

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

if __name__ == "__main__":
    main()