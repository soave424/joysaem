import streamlit as st
import math
import pandas as pd 

# Title of the calculator
st.title("현장체험학습비 계산기")

# Input for participants, absentees, and teachers (shown together)
st.header("1. 인원 입력")
num_participants = st.number_input("1. 참가 학생 수", min_value=0, step=1)
num_absentees = st.number_input("2. 불참 학생 수", min_value=0, step=1)
num_teachers = st.number_input("3. 인솔 교사 수", min_value=0, step=1)

# If any of the first three fields is greater than 0, show bus-related questions
if num_participants > 0 or num_absentees > 0 or num_teachers > 0:
    st.header("2. 버스 관련 입력")
    bus_price = st.number_input("4. 버스 1대 금액", min_value=0, step=1000)
    num_buses = st.number_input("5. 버스 총 대수", min_value=0, step=1)

# If both bus price and number of buses are filled, show activity-related questions
if bus_price > 0 and num_buses > 0:
    st.header("3. 체험비 입력")
    student_activity_cost = st.number_input("6. 학생 체험비", min_value=0, step=1000)
    supported_students = st.number_input("7. 체험비 지원 학생 수", min_value=0, step=1)
    student_lunch_cost = st.number_input("8. 학생 중식비", min_value=0, step=1000)
    student_insurance_cost = st.number_input("9. 학생 보험비", min_value=0, step=500)
    teacher_insurance_cost = st.number_input("10. 교사 보험비", min_value=0, step=500)

# Once all fields are entered, calculate the results
if st.button("Calculate"):

    # Calculations for personnel
    total_students = num_participants + num_absentees

    # Bus-related calculations
    total_bus_cost = bus_price * num_buses
    total_participants = num_participants + num_teachers
    bus_cost_per_person = math.floor((total_bus_cost / total_participants)/10)*10
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

    # Validation: Amount collected from students and teacher expenses vs total costs
    total_collected = student_total_general * (num_participants - supported_students) + (student_total_supported or 0) * supported_students
    total_teacher_expenses = total_teacher_transport_cost + total_teacher_insurance_cost
    total_expenses = total_bus_cost + total_student_activity_cost + total_student_lunch_cost + total_student_insurance_cost + total_teacher_insurance_cost

    st.subheader("Calculation Results")

    # Create a table-like structure with calculations and explanations
    result_data = {
        "항목": [
            "제적", "참가자", "불참자", "인솔",
            "버스비 총액", "1인당 버스비", "버스 절삭액",
            "학생 체험비 총액", "학생 중식비 총액", "학생 보험비 총액",
            "학생 체험비 (일반)", "학생 체험비 (지원)",
            "교사 교통비", "교사 보험비"
        ],
        "결과값": [
            f"{total_students}명", f"{num_participants}명", f"{num_absentees}명", f"{num_teachers}명",
            f"{total_bus_cost:,}원", f"{bus_cost_per_person:,}원", f"{bus_trimming_cost:,}원",
            f"{total_student_activity_cost:,}원", f"{total_student_lunch_cost:,}원", f"{total_student_insurance_cost:,}원",
            f"{student_total_general:,}원", f"{student_total_supported:,}원" if student_total_supported else "N/A",
            f"{total_teacher_transport_cost:,}원", f"{total_teacher_insurance_cost:,}원"
        ],
        "계산 과정": [
            f"참가 학생 수({num_participants})명 + 불참 학생 수({num_absentees})명", f"참가 학생 수({num_participants})명", f"불참 학생 수({num_absentees})명" , 
            f"인솔 교사 수 {num_teachers}명", f"버스 1대 금액({bus_price:,}원) * 버스 대수({num_buses})", 
            f"버스비 총액({total_bus_cost:,}원) / (참가 학생 수({num_participants}) + 인솔 교사 수({num_teachers}))",
            f"버스비 총액({total_bus_cost:,}원) - (1인당 버스비({bus_cost_per_person:,}원) * 전체 탑승 인원({total_participants}))",
            f"학생 체험비({student_activity_cost:,}원) * 지원 제외 참가 학생 수({actual_students}) : ({supported_students})명",
            f"학생 중식비({student_lunch_cost:,}원) * 참가 학생 수({num_participants})",
            f"학생 보험비({student_insurance_cost:,}원) * 참가 학생 수({num_participants})",
            f"1인당 버스비({bus_cost_per_person:,}원) + 체험비({student_activity_cost:,}원) + 중식비({student_lunch_cost:,}원) + 보험비({student_insurance_cost:,}원)", 
            f"1인당 버스비({bus_cost_per_person:,}원) + 중식비({student_lunch_cost:,}원) + 보험비({student_insurance_cost:,}원)", 
            f"1인당 버스비({bus_cost_per_person:,}원) * 인솔 교사 수({num_teachers}) + 절삭액({bus_trimming_cost:,}원)",
            f"교사 보험비({teacher_insurance_cost:,}원) * 인솔 교사 수({num_teachers})"
        ]
    }

    # Display the table with explanations
    result_df = pd.DataFrame(result_data)
    st.table(result_df)

    # Validation check for the total expenses
    st.subheader("Validation")
    st.write(f"총 징수금액 (학생 및 교사): {total_collected + total_teacher_expenses:,}원")
    st.write(f"총 지불금액 (버스비, 체험비, 중식비 등): {total_expenses:,}원")

    if (total_collected + total_teacher_expenses) == total_expenses:
        st.success("금액이 일치합니다.")
    else:
        st.error("징수 금액과 지불 금액이 일치하지 않습니다. 다시 확인해 주세요.")
