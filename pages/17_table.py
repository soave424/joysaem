import streamlit as st

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
        st.success("✅ 신청이 완료되었습니다! (CSV 연동 예정)")

# 오른쪽: 신청 게시판
with col2:
    st.header("📋 유지보수 신청 목록")
    st.info("🚧 현재 신청 목록 기능은 준비 중입니다. (CSV 연동 예정)")
