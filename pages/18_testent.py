import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from PIL import Image
import io

# Set page configuration
st.set_page_config(page_title="역량검사", layout="wide")

# Initialize session state variables
if 'page' not in st.session_state:
    st.session_state.page = 'assessment'
if 'answers' not in st.session_state:
    st.session_state.answers = {}
if 'student_info' not in st.session_state:
    st.session_state.student_info = {'name': '', 'grade': '', 'class': ''}

# Function to handle answer selection
def select_answer(question_num, answer):
    st.session_state.answers[question_num] = answer
    st.experimental_rerun()

# Function to go to results page
def go_to_results():
    st.session_state.page = 'results'
    st.experimental_rerun()

# Function to go back to assessment page
def go_to_assessment():
    st.session_state.page = 'assessment'
    st.experimental_rerun()

# Define questions
questions = [
    "나는 친구들이 생각하지 못하는 새로운 아이디어를 낼 수 있다.",
    "나는 현재 좋은 방법을 알고 있더라도 더 나은 새로운 방법을 찾을 수 있다.",
    "나는 똑같은 일을 하는 것보다 변화가 많은 일을 더 좋아한다.",
    "나는 수업시간에 선생님이 가르쳐 주시지 않은 것도 스스로 공부할 수 있다.",
    "나는 내가 정한 목표를 이루기 위해 꾸준히 노력한다.",
    "나는 어려운 문제를 풀기 위해 포기하지 않고 계속 도전한다.",
    "나는 친구들의 의견을 존중하며 경청한다.",
    "나는 친구들과 협력하여 공동의 목표를 이루는 것을 좋아한다.",
    "나는 다른 사람의 감정을 잘 이해하고 공감할 수 있다.",
    "나는 복잡한 문제를 작은 부분으로 나누어 해결할 수 있다.",
    "나는 문제의 원인을 찾아내고 해결책을 제시할 수 있다.",
    "나는 여러 가지 정보를 분석하여 중요한 것을 찾아낼 수 있다."
]

# Define answer options
options = ["전혀 그렇지 않다", "그렇지 않다", "보통", "그렇다", "매우 그렇다"]
option_values = {option: idx for idx, option in enumerate(options, 1)}

# Define competency categories
competencies = {
    "창의성": [1, 2, 3],
    "자기주도성": [4, 5, 6],
    "협업능력": [7, 8, 9],
    "문제해결력": [10, 11, 12]
}

# Main app logic
if st.session_state.page == 'assessment':
    # Create a two-column layout
    col1, col2 = st.columns([1, 3])
    
    # Header
    with col2:
        st.markdown("""
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <h1>초등학교 진단문항</h1>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <p style="font-size: 16px;">아래 문항은 창의가정신과 관련한 생각이나 태도를 알아보기 위한 질문입니다.<br>
        각 문항을 읽고 자신의 생각과 가장 일치하는 답변을 선택해주세요.</p>
        """, unsafe_allow_html=True)
        
        st.markdown("<hr>", unsafe_allow_html=True)
    
    # Student info input
    with col2:
        name_col, grade_col = st.columns(2)
        with name_col:
            student_name = st.text_input("이름", key="student_name", value=st.session_state.student_info['name'])
            st.session_state.student_info['name'] = student_name
        with grade_col:
            grade = st.text_input("학년/반", key="grade", value=st.session_state.student_info['grade'])
            st.session_state.student_info['grade'] = grade
    
    # Left column - Question numbers with indicators
    with col1:
        st.markdown("<h3 style='text-align: center;'>창의가정신 핵심역량<br>진단도구</h3>", unsafe_allow_html=True)
        
        # Create progress indicator
        total_questions = len(questions)
        answered_questions = len(st.session_state.answers)
        progress_percentage = int((answered_questions / total_questions) * 100)
        
        # Progress bar container
        st.markdown(f"""
        <div style="margin-top: 50px; margin-bottom: 20px;">
            <div style="background-color: #e0e0e0; height: 10px; border-radius: 5px; margin-bottom: 5px;">
                <div style="background-color: #FF8C00; width: {progress_percentage}%; height: 10px; border-radius: 5px;"></div>
            </div>
            <div style="text-align: right; font-size: 16px; color: #FF8C00; font-weight: bold;">{progress_percentage}%</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Calendar-like number grid
        num_rows = 6
        num_cols = 6
        
        for row in range(num_rows):
            cols = st.columns(num_cols)
            for col in range(num_cols):
                q_num = row * num_cols + col + 1
                if q_num <= total_questions:
                    answered = q_num in st.session_state.answers
                    color = "#FF8C00" if answered else "#e0e0e0"
                    cols[col].markdown(f"""
                    <div style="width: 30px; height: 30px; border-radius: 50%; background-color: {color}; 
                    display: flex; align-items: center; justify-content: center; margin: auto; color: white; font-weight: bold;">
                    {q_num}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    cols[col].markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
    
    # Right column - Questions and answer options
    with col2:
        for i, question in enumerate(questions, 1):
            st.markdown(f"<h3>{i}. {question}</h3>", unsafe_allow_html=True)
            
            # Create buttons for answer options
            cols = st.columns(5)
            for j, option in enumerate(options):
                # Check if this option is selected
                is_selected = st.session_state.answers.get(i) == option
                button_style = "primary" if is_selected else "secondary"
                
                if cols[j].button(option, key=f"q{i}_{option}", use_container_width=True, 
                                 type=button_style):
                    select_answer(i, option)
            
            st.markdown("<hr>", unsafe_allow_html=True)
        
        # Show results button if all questions are answered
        if len(st.session_state.answers) == len(questions):
            st.markdown("<div style='text-align: center; margin-top: 20px;'>", unsafe_allow_html=True)
            if st.button("결과 보기", key="show_results", use_container_width=True, type="primary"):
                go_to_results()
            st.markdown("</div>", unsafe_allow_html=True)

# Results page
elif st.session_state.page == 'results':
    st.title("역량검사 결과")
    
    # Calculate competency scores
    scores = {}
    for competency, question_ids in competencies.items():
        competency_score = 0
        for q_id in question_ids:
            if q_id in st.session_state.answers:
                answer = st.session_state.answers[q_id]
                competency_score += option_values[answer]
        
        # Calculate average score (1-5 scale)
        avg_score = competency_score / len(question_ids)
        scores[competency] = avg_score
    
    # Create results visualization
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader(f"{st.session_state.student_info['name']}님의 역량 프로필")
        
        # Create data for chart
        chart_data = pd.DataFrame({
            '역량': list(scores.keys()),
            '점수': list(scores.values())
        })
        
        # Create bar chart
        chart = alt.Chart(chart_data).mark_bar().encode(
            x=alt.X('점수:Q', scale=alt.Scale(domain=[0, 5])),
            y=alt.Y('역량:N', sort='-x'),
            color=alt.Color('역량:N', legend=None),
            tooltip=['역량', '점수']
        ).properties(
            height=300
        )
        
        st.altair_chart(chart, use_container_width=True)
    
    with col2:
        st.subheader("역량별 상세 결과")
        
        # Display detailed results
        for competency, score in scores.items():
            # Determine level based on score
            if score >= 4.5:
                level = "매우 우수"
                emoji = "🌟"
            elif score >= 3.5:
                level = "우수"
                emoji = "😊"
            elif score >= 2.5:
                level = "보통"
                emoji = "🙂"
            else:
                level = "노력 필요"
                emoji = "💪"
                
            st.markdown(f"""
            <div style="margin-bottom: 15px; padding: 10px; border-radius: 5px; border: 1px solid #ddd;">
                <h3>{emoji} {competency}: {level}</h3>
                <p>점수: {score:.1f}/5.0</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Show all responses
    st.subheader("문항별 응답 결과")
    
    response_data = []
    for i, question in enumerate(questions, 1):
        response = st.session_state.answers.get(i, "미응답")
        response_data.append({"문항": i, "질문": question, "응답": response})
    
    response_df = pd.DataFrame(response_data)
    st.dataframe(response_df, use_container_width=True, hide_index=True)
    
    # Return to assessment button
    if st.button("검사 다시하기", key="back_to_assessment"):
        st.session_state.answers = {}
        go_to_assessment()