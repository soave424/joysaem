import streamlit as st
import pandas as pd
import os
from datetime import datetime
import pytz

# CSV 파일 경로 설정
CSV_FILE = "maintenance_requests.csv"

def load_data():
    if not os.path.exists(CSV_FILE):  # 파일이 없으면 생성
        df = pd.DataFrame(columns=["date", "applicant", "contact", "floor", "classroom", "content", "status", "memo"])
        df.to_csv(CSV_FILE, index=False)
    else:
        df = pd.read_csv(CSV_FILE, dtype={'date': str})
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
    st.header("📝 신청하기")
    
    applicant = st.text_input("신청자 이름", "")
    contact = st.text_input("연락처", "")
    floor = st.selectbox("교실 위치(층)", [1, 2, 3, 4, 5])
    classroom = st.text_input("교실명", "")
    content = st.text_area("유지보수 신청 내용", "")
    
    if st.button("신청"):
        if applicant and contact and classroom and content:
            korea_tz = pytz.timezone('Asia/Seoul')
            date = datetime.now(korea_tz).strftime("%Y-%m-%d %a %H:%M:%S").replace('Mon', '월').replace('Tue', '화').replace('Wed', '수').replace('Thu', '목').replace('Fri', '금').replace('Sat', '토').replace('Sun', '일')
            new_entry = pd.DataFrame([[date, applicant, contact, floor, classroom, content, "신청 완료", ""]], 
                                     columns=["date", "applicant", "contact", "floor", "classroom", "content", "status", "memo"])
            data = pd.concat([data, new_entry], ignore_index=True)
            save_data(data)
            st.success("✅ 신청이 완료되었습니다!")
            st.rerun()
        else:
            st.warning("⚠ 모든 필드를 입력해주세요.")

# 오른쪽: 신청 게시판
with col2:
    st.header("📋 신청 목록")
    pending_data = data[data["status"] == "신청 완료"]
    completed_data = data[data["status"] == "해결 완료"]
    
    st.subheader("🟠 해결 중")
    if pending_data.empty:
        st.info("🚧 현재 신청 목록이 없습니다.")
    else:
        for idx, row in pending_data.iterrows():
            with st.expander(f"[{row['floor']}층_{row['classroom']}] {row['content'][:20]}...   ({row['date']})"):
                st.write(f"**신청자:** {row['applicant']}")
                st.write(f"**연락처:** {row['contact']}")
                st.write(f"**교실 위치:** {row['floor']}층 {row['classroom']}")
                st.write(f"**신청 내용:** {row['content']}")
                st.write(f"**해결 상태:** {row['status']}")
                st.write(f"**메모:** {row['memo']}")
                
                # 해결 완료 버튼 (유니크한 키 사용)
                form_key = f"form_{idx}"
                with st.form(key=form_key):
                    status = st.selectbox("상태 변경", ["해결 완료", "신청 완료"], index=0)
                    memo = st.text_area("메모 입력", placeholder="특이사항이 있는 경우 작성해주세요.")
                    submit = st.form_submit_button("확인")
                    
                    if submit:
                        # `iloc`을 사용하여 안전하게 데이터 수정
                        data.loc[data.index[idx], "status"] = status
                        data.loc[data.index[idx], "memo"] = memo
                        
                        if status == "해결 완료":
                            # 해결 완료된 요청을 기존 위치에서 삭제 후 리스트 아래로 추가
                            completed_entry = data.iloc[idx].copy()
                            data = data.drop(index=data.index[idx]).reset_index(drop=True)
                            data = pd.concat([data, completed_entry.to_frame().T], ignore_index=True)

                        # 변경 사항 저장
                        save_data(data)
                        st.success("✅ 상태가 업데이트되었습니다!")
                        st.rerun()

    st.subheader("✅ 완료 목록")
    if completed_data.empty:
        st.info("🔹 해결된 요청이 없습니다.")
    else:
        for idx, row in completed_data.iterrows():
            with st.expander(f"[{row['floor']}층_{row['classroom']}] {row['content'][:20]}...   ({row['date']})"):
                st.write(f"**신청자:** {row['applicant']}")
                st.write(f"**연락처:** {row['contact']}")
                st.write(f"**교실 위치:** {row['floor']}층 {row['classroom']}")
                st.write(f"**신청 내용:** {row['content']}")
                st.write(f"**해결 상태:** {row['status']}")
                st.write(f"**메모:** {row['memo']}")
