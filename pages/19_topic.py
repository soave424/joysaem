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

# 태그 필터 UI 생성 함수
def create_tag_filters(session_key):
    # 세션 상태에 필터 태그 저장
    if session_key not in st.session_state:
        st.session_state[session_key] = ["모든 태그"]
    
    # 태그 개수에 맞게 컬럼 생성 (모든 태그 + 실제 태그들)
    cols = st.columns(len(TAGS) + 1)
    
    # "모든 태그" 버튼
    if cols[0].button("모든 태그", key=f"all_tags_{session_key}", 
                      use_container_width=True,
                      type="primary" if "모든 태그" in st.session_state[session_key] else "secondary"):
        st.session_state[session_key] = ["모든 태그"]
        st.rerun()
    
    # 각 태그별 버튼 생성
    for i, tag in enumerate(TAGS):
        if cols[i + 1].button(tag, key=f"{session_key}_{tag}", 
                          use_container_width=True,
                          type="primary" if tag in st.session_state[session_key] else "secondary"):
            if "모든 태그" in st.session_state[session_key]:
                st.session_state[session_key] = [tag]
            else:
                if tag in st.session_state[session_key]:
                    st.session_state[session_key].remove(tag)
                else:
                    st.session_state[session_key].append(tag)
                
                if not st.session_state[session_key]:  # 선택된 태그가 없으면
                    st.session_state[session_key] = ["모든 태그"]
            
            st.rerun()
    
    # 선택된 필터 표시는 제거 (버튼 자체가 이미 선택 상태로 표시됨)
    return st.session_state[session_key]

# 사용자 페이지
def user_view(df):
    st.subheader("의견 공유")
    
    with st.form("comment_form"):
        name = st.text_input("이름(선택)")
        comment = st.text_area("내용")
        selected_tags = st.multiselect("태그 선택 (여러 개 선택 가능)", TAGS)
        submitted = st.form_submit_button("제출")
        
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
            st.success("글이 제출되었습니다. 관리자 승인 후 게시됩니다.")
    
    # 승인된 댓글만 표시
    st.subheader("승인된 글")
    approved_comments = df[df["approved"] == True].sort_values(by="timestamp", ascending=False)
    
    if approved_comments.empty:
        st.info("아직 승인된 글이 없습니다.")
    else:
        # 태그 필터링 UI 생성
        st.write("태그로 필터링:")
        filter_tags = create_tag_filters("filter_tags")
            
        # 필터링 적용
        if "모든 태그" in filter_tags:
            filtered_comments = approved_comments
        else:
            # 선택된 태그 중 하나라도 포함된 댓글 필터링
            filtered_comments = approved_comments[approved_comments["tags"].apply(
                lambda x: any(tag in parse_tags(x) for tag in filter_tags)
            )]
        
        if filtered_comments.empty:
            st.info("해당 태그의 승인된 글이 없습니다.")
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
    st.subheader("관리자 페이지 - 글 관리")
    
    # 탭 생성
    pending_tab, approved_tab = st.tabs(["승인 대기 글", "승인된 글"])
    
    # 승인 대기 댓글 탭
    with pending_tab:
        pending_comments = df[df["approved"] == False]
        
        # 태그 필터링 UI 생성
        st.write("태그로 필터링:")
        filter_tags_pending = create_tag_filters("filter_tags_pending")
        
        # 필터링 적용
        if "모든 태그" in filter_tags_pending:
            filtered_pending = pending_comments
        else:
            # 선택된 태그 중 하나라도 포함된 댓글 필터링
            filtered_pending = pending_comments[pending_comments["tags"].apply(
                lambda x: any(tag in parse_tags(x) for tag in filter_tags_pending)
            )]
        
        if filtered_pending.empty:
            st.info("승인 대기 중인 글이 없습니다.")
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
        
        # 태그 필터링 UI 생성
        st.write("태그로 필터링:")
        filter_tags_approved = create_tag_filters("filter_tags_approved")
        
        # 필터링 적용
        if "모든 태그" in filter_tags_approved:
            filtered_approved = approved_comments
        else:
            # 선택된 태그 중 하나라도 포함된 댓글 필터링
            filtered_approved = approved_comments[approved_comments["tags"].apply(
                lambda x: any(tag in parse_tags(x) for tag in filter_tags_approved)
            )]
        
        if filtered_approved.empty:
            st.info("승인된 글이 없습니다.")
        else:
            for idx, row in filtered_approved.iterrows():
                with st.container():
                    col1, col2 = st.columns([5, 1])
                    
                    # 관리자 페이지 - 댓글 표시 부분 수정
                    # 승인 대기 댓글 표시 부분
                    with col1:
                        st.markdown(f"**{row['name']}** - {row['timestamp']}")
                        
                        # 태그 표시 - 가로로 한 줄에 표시되도록 수정
                        tags_list = parse_tags(row['tags'])
                        tag_html = "<div style='display: flex; flex-wrap: nowrap; gap: 5px;'>"
                        tag_html += "".join([get_tag_style(tag) for tag in tags_list])
                        tag_html += "</div>"
                        st.markdown(tag_html, unsafe_allow_html=True)
                        
                        #  내용
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
    st.title("연구회 운영 나눔")
    
    # 관리자 모드
    if is_admin:
        admin_view(df)
    else:
        user_view(df)

if __name__ == "__main__":
    main()