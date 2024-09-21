
import streamlit as st

# 메인 화면 분할
col1, col2 = st.columns(2)

# 데이터 입력 화면
with col1:
    st.subheader("데이터 입력")
    
    # 반 정보 입력
    num_classes = st.number_input("총 반 수", min_value=1, step=1)
    
    # 반별 참석/불참 인원 입력
    class_attend = {}
    class_absent = {}
    for i in range(1, int(num_classes)+1):
        class_attend[i] = st.number_input(f"{i}반 참석 인원", min_value=0, step=1, key=f"attend_{i}")
        class_absent[i] = st.number_input(f"{i}반 불참 인원", min_value=0, step=1, key=f"absent_{i}")
        
    # 버스 및 기타 비용 입력
    bus_cost_per = st.number_input("버스 1대 비용(원)", min_value=0.0, step=1.0)
    num_bus = st.number_input("버스 대수", min_value=0, step=1)
    num_teacher = st.number_input("인솔 인원", min_value=0, step=1)
    activity_cost = st.number_input("체험활동비(원)", min_value=0.0, step=1.0)
    insurance_cost = st.number_input("학생 보험비(원)", min_value=0.0, step=1.0)

    # 계산 버튼
    if st.button("계산"):
        # 계산 로직 구현
        total_attend = sum(class_attend.values())
        total_absent = sum(class_absent.values())
        total_participants = total_attend + total_absent
        total_bus_cost = bus_cost_per * num_bus
        student_bus_cost = (total_bus_cost - (num_teacher * bus_cost_per)) / total_attend
        student_total_cost = student_bus_cost + activity_cost + insurance_cost
        teacher_bus_cost = num_teacher * bus_cost_per

# 계산 결과 화면
with col2:
    st.subheader("계산 결과")
    
    # 반별 참석/불참 인원 표 출력
    st.write("반별 참석/불참 인원")
    table_data = [["반", "참석", "불참", "합계"] ]
    for i in range(1, int(num_classes)+1):
        table_data.append([f"{i}반", class_attend[i], class_absent[i], class_attend[i] + class_absent[i]])
    st.table(table_data)
    
    st.write(f"총 참가 인원: {total_participants}명")
    st.write(f"총 참석 인원: {total_attend}명")
    st.write(f"총 불참 인원: {total_absent}명")
    st.write(f"학생 1인당 버스비: {student_bus_cost:.0f}원")
    st.write(f"학생 1인당 총 비용: {student_total_cost:.0f}원")
    st.write(f"교사 버스비 총액: {teacher_bus_cost:.0f}원")
    st.write(f"총 소요 경비: {total_bus_cost + activity_cost + insurance_cost * total_attend:.0f}원")