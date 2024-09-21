
import streamlit as st

# 메인 화면 분할
col1, col2 = st.columns(2)

# 데이터 입력 화면
with col1:
    st.subheader("데이터 입력")
    # 참석, 불참, 기타 인원 입력
    num_attend = st.number_input("참석 인원", min_value=0, step=1)
    num_absent = st.number_input("불참 인원", min_value=0, step=1)
    num_etc = st.number_input("기타 인원", min_value=0, step=1)

    # 버스 관련 정보 입력
    bus_cost_per = st.number_input("버스 1대 비용(원)", min_value=0.0, step=1.0)
    num_bus = st.number_input("버스 대수", min_value=0, step=1)
    num_teacher = st.number_input("인솔 인원", min_value=0, step=1)
    activity_cost = st.number_input("체험활동비(원)", min_value=0.0, step=1.0)
    insurance_cost = st.number_input("학생 보험비(원)", min_value=0.0, step=1.0)

    # 계산 버튼
    if st.button("계산"):
        # 계산 로직 구현
        total_participants = num_attend + num_absent + num_etc
        total_bus_cost = bus_cost_per * num_bus
        student_bus_cost = (total_bus_cost - (num_teacher * bus_cost_per)) / num_attend
        student_total_cost = student_bus_cost + activity_cost + insurance_cost
        teacher_bus_cost = num_teacher * bus_cost_per

# 계산 결과 화면
with col2:
    st.subheader("계산 결과")
    st.write(f"총 참가 인원: {total_participants}명")
    st.write(f"학생 1인당 버스비: {student_bus_cost:.0f}원")
    st.write(f"학생 1인당 총 비용: {student_total_cost:.0f}원")
    st.write(f"교사 버스비 총액: {teacher_bus_cost:.0f}원")
    st.write(f"총 소요 경비: {total_bus_cost + activity_cost + insurance_cost * num_attend:.0f}원")
