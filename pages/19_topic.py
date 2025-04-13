import streamlit as st
import pandas as pd
import datetime
import uuid
import os

# 데이터 파일 경로 설정
DATA_FILE = "comments.csv"

# 페이지 설정
st.set_page_config(page_title="댓글 게시판", layout="wide")

# 데이터 초기화 및 불러오기
def initialize_data():
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=["id", "name", "comment", "timestamp", "approved"])
        df.to_csv(DATA_FILE, index=False)
    return pd.read_csv(DATA_FILE)

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
        submitted = st.form_submit_button("댓글 제출")
        
        if submitted and name and comment:
            new_comment = {
                "id": str(uuid.uuid4()),
                "name": name,
                "comment": comment,
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
        for _, row in approved_comments.iterrows():
            with st.container():
                st.markdown(f"**{row['name']}** - {row['timestamp']}")
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
        
        if pending_comments.empty:
            st.info("승인 대기 중인 댓글이 없습니다.")
        else:
            for idx, row in pending_comments.iterrows():
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"**{row['name']}** - {row['timestamp']}")
                        st.markdown(f"{row['comment']}")
                    
                    with col2:
                        if st.button("승인", key=f"approve_{row['id']}"):
                            df.at[idx, "approved"] = True
                            save_data(df)
                            st.rerun()
                        
                        if st.button("삭제", key=f"delete_{row['id']}"):
                            df = df.drop(idx)
                            save_data(df)
                            st.rerun()
                    
                    st.markdown("---")
    
    # 승인된 댓글 탭
    with approved_tab:
        approved_comments = df[df["approved"] == True]
        
        if approved_comments.empty:
            st.info("승인된 댓글이 없습니다.")
        else:
            for idx, row in approved_comments.iterrows():
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"**{row['name']}** - {row['timestamp']}")
                        st.markdown(f"{row['comment']}")
                    
                    with col2:
                        if st.button("삭제", key=f"delete_approved_{row['id']}"):
                            df = df.drop(idx)
                            save_data(df)
                            st.rerun()
                    
                    st.markdown("---")

if __name__ == "__main__":
    main()