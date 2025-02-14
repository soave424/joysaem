import streamlit as st
import pandas as pd
import os
from datetime import datetime

# CSV 파일 경로 설정
CSV_FILE = os.path.join("csv", "maintenance_requests.csv")

def load_data():
    if not os.path.exists(CSV_FILE):
        df = pd.DataFrame(columns=["date", "applicant", "contact", "floor", "classroom", "content", "status", "memo"])
        df.to_csv(CSV_FILE, index=False)
    else:
        df = pd.read_csv(CSV_FILE)
    return df

def save_data(df):
    df.to_csv(CSV_FILE, index=False)

# 데이터 불러오기
data = load_data()

st.title("🏫 유지보수 서비스 신청 게시판")

# 레이아웃 설정
col1, col2 = st.columns([1, 2])

# 왼쪽: 신청 폼
with col1:
    st.header("📝 유지보수 신청하기")
    
    applicant = st.text_input("신청자 이름", "")
    contact = st.text_input("연락처", "")
    floor = st.selectbox("교실 위치(층)", [1, 2, 3, 4, 5])
    classroom = st.text_input("교실명", "")
    content = st.text_area("유지보수 신청 내용", "")
    
    if st.button("신청하기"):
        if applicant and contact and classroom and content:
            date = datetime.now().strftime("%Y-%m-%d-%a")
            new_entry = pd.DataFrame([[date, applicant, contact, floor, classroom, content, "신청 완료", ""]], 
                                     columns=["date", "applicant", "contact", "floor", "classroom", "content", "status", "memo"])
            data = pd.concat([data, new_entry], ignore_index=True)
            save_data(data)
            st.success("✅ 신청이 완료되었습니다!")
            st.experimental_rerun()
        else:
            st.warning("⚠ 모든 필드를 입력해주세요.")

# 오른쪽: 신청 게시판
with col2:
    st.header("📋 유지보수 신청 목록")
    if data.empty:
        st.info("아직 신청된 유지보수 요청이 없습니다.")
    else:
        for idx, row in data.iterrows():
            with st.expander(f"[{row['floor']}층_{row['classroom']}] {row['content'][:20]}...   ({row['date']})"):
                st.write(f"**신청자:** {row['applicant']}")
                st.write(f"**연락처:** {row['contact']}")
                st.write(f"**교실 위치:** {row['floor']}층 {row['classroom']}")
                st.write(f"**신청 내용:** {row['content']}")
                st.write(f"**해결 상태:** {row['status']}")
                st.write(f"**메모:** {row['memo']}")
                
                if st.button(f"해결 완료 - {row['classroom']}", key=f"done_{idx}"):
                    with st.form(key=f"form_{idx}"):
                        st.write("🛠 문제가 해결되었나요?")
                        status = st.selectbox("상태 변경", ["해결 완료", "신청 완료"], index=1)
                        memo = st.text_area("메모 입력")
                        submit = st.form_submit_button("확인")
                        
                        if submit:
                            data.at[idx, "status"] = status
                            data.at[idx, "memo"] = memo
                            save_data(data)
                            st.success("✅ 상태가 업데이트되었습니다!")
                            st.experimental_rerun()
