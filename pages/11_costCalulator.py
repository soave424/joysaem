import streamlit as st
import math

# Title of the calculator
st.title("Experiential Learning Cost Calculator")

# Input fields for each required data
num_participants = st.number_input("1. 참가 학생 수", min_value=0, step=1)
num_absentees = st.number_input("2. 불참 학생 수", min_value=0, step=1)
num_teachers = st.number_input("3. 인솔 교사 수", min_value=0, step=1)

bus_price = st.number_input("4. 버스 1대 금액", min_value=0, step=1000)
num_buses = st.number_input("5. 버스 총 대수", min_value=0, step=1)

student_activity_cost = st.number_input("6. 학생 체험비", min_value=0, step=1000)
supported_students = st.number_input("7. 체험비 지원 학생 수", min_value=0, step=1)

student_lunch_cost = st.number_input("8. 학생 중식비", min_value=0, step=1000)
student_insurance_cost = st.number_input("9. 학생 보험비", min_value=0, step=500)
teacher_insurance_cost = st.number_input("10. 교사 보험비", min_value=0, step=500)

if st.button("Calculate"):

    # Calculations for personnel
    total_students = num_participants + num_absentees

    # Bus-related calculations
    total_bus_cost = bus_price * num_buses
    total_participants = num_participants + num_teachers
    bus_cost_per_person = math.floor(total_bus_cost / total_participants)
    bus_trimming_cost = total_bus_cost - (bus_cost_per_person * total_participants)

    # Activity cost calculations
    actual_students = num_participants - supported_students  # Adjusting for supported students
    total_student_activity_cost = student_activity_cost * actual_students
    total_student_lunch_cost = student_lunch_cost * num_participants
    total_student_insurance_cost = student_insurance_cost * num_participants

    # Total charges
    student_total_general = bus_cost_per_person + student_activity_cost + student_lunch_cost + student_insurance_cost
    student_total_supported = bus_cost_per_person + student_lunch_cost + student_insurance_cost if supported_students > 0 else None

    # Teacher-related calculations
    total_teacher_transport_cost = bus_cost_per_person * num_teachers + bus_trimming_cost
    total_teacher_insurance_cost = teacher_insurance_cost * num_teachers

    # Display the results
    st.subheader("Results")
    
    st.write(f"1. 참가 학생 수: {num_participants}명")
    st.write(f"2. 불참 학생 수: {num_absentees}명")
    st.write(f"3. 전체 학생 수: {total_students}명")
    st.write(f"4. 인솔 교사 수: {num_teachers}명")

    st.write(f"5. 버스비 총액: {total_bus_cost:,} 원")
    st.write(f"6. 1인당 버스비 (절사): {bus_cost_per_person:,} 원")
    st.write(f"7. 버스 절삭액: {bus_trimming_cost:,} 원")

    st.write(f"8. 학생 체험비 총액: {total_student_activity_cost:,} 원")
    st.write(f"9. 학생 중식비 총액: {total_student_lunch_cost:,} 원")
    st.write(f"10. 학생 보험비 총액: {total_student_insurance_cost:,} 원")

    st.subheader("징수 금액")
    st.write(f"11. 학생 체험비 (일반): {student_total_general:,} 원")
    if student_total_supported is not None:
        st.write(f"12. 학생 체험비 (지원): {student_total_supported:,} 원")

    st.subheader("교사 출장 비용")
    st.write(f"13. 교사 교통비: {total_teacher_transport_cost:,} 원")
    st.write(f"14. 교사 보험비: {total_teacher_insurance_cost:,} 원")
