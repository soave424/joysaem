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
if 'button_clicked' not in st.session_state:
    st.session_state.button_clicked = False

# Callback functions for button clicks
def answer_click(question_num, answer):
    st.session_state.answers[question_num] = answer
    st.session_state.button_clicked = True

def results_click():
    st.session_state.page = 'results'
    st.session_state.button_clicked = True

def reset_assessment():
    st.session_state.page = 'assessment'
    st.session_state.answers = {}
    st.session_state.button_clicked = True

# Define questions - 이전 문항들을 새 문항들로 교체
questions = [
    "나는 더 좋은 방법을 생각해내고, 새로운 생각을 떠올리는 걸 좋아한다.",
    "나는 새로운 것과 특별한 것이 더 좋고, 재미있게 느껴진다.",
    "나는 환경을 지키기 위해 좋은 방법을 생각해낸다.",
    "나는 도움이 필요한 사람들을 돕는 사람을 멋지다고 생각하고, 그런 방법을 배우고 싶다.",
    "나는 변화나 불편한 점을 빠르게 알아차린다.",
    "나는 불편한 문제를 해결하는 방법을 찾고, 생각이 떠오르면 바로 해본다.",
    "나는 스스로 정한 높은 목표를 이루기 위해 열심히 노력한다.",
    "나는 목표를 세우고 계획하며, 어려운 일도 잘 해낼 수 있다고 믿는다.",
    "나는 좋은 방법을 찾고, 어려워도 해낼 수 있다고 생각하며 도전한다.",
    "나는 일이 잘못될 때도 대비하고, 문제를 해결하려고 노력한다.",
    "나는 여러 번 실패해도 다시 해보고, 잘 안 되면 왜 그런지 생각해본다.",
    "나는 실패해도 남을 탓하지 않고, 고칠 방법을 찾으며 포기하지 않는다.",
    "나는 목표를 세우고 스스로 문제를 해결하기 위해 끝까지 노력한다.",
    "나는 친구들과 생각이 다를 때도 내 생각을 똑똑하게 말할 수 있다.",
    "나는 약속을 잘 지키고, 하고 싶은 일이 있어도 미루지 않고 한다.",
    "나는 맡은 일을 꼼꼼하게 하고, 화가 나도 생각하고 말한다.",
    "나는 목표를 이루기 위해 집중해서 열심히 노력한다.",
    "나는 어려운 일도 쉽게 포기하지 않고, 끝까지 해내려고 한다.",
    "나는 친구들 사이의 문제를 잘 해결하고, 친구들의 이야기를 잘 들어준다.",
    "나는 친구들과 의견을 모아 좋은 방법을 찾고, 여러 의견을 잘 비교한다.",
    "나는 필요한 정보를 잘 찾고, 도움을 요청할 줄 안다.",
    "나는 도움이 필요하면 요청할 줄 알고, 나를 도와줄 친구들이 있다고 생각한다.",
    "나는 친구들이 잘 할 수 있게 역할을 나누어주고, 힘들어하는 친구를 잘 도와준다.",
    "나는 친구들과 목표를 이야기하며, 함께 일하는 게 더 좋다고 생각한다."
]

# Define answer options
options = ["전혀 그렇지 않다", "그렇지 않다", "보통", "그렇다", "매우 그렇다"]
option_values = {option: idx for idx, option in enumerate(options, 1)}

# Define competency categories - 역량 영역도 수정
competencies = {
    "가치창출역량": [1, 2, 3, 4, 5, 6],
    "도전역량": [7, 8, 9, 10, 11, 12],
    "자기주도역량": [13, 14, 15, 16, 17, 18],
    "집단창의역량": [19, 20, 21, 22, 23, 24]
}

# Main app logic
if st.session_state.page == 'assessment':
    # Create a two-column layout
    col1, col2 = st.columns([1, 3])
    
    # Header
    with col2:
        st.markdown("""
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <h1>창의가정신 역량검사</h1>
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
        
        # Calendar-like number grid - 문항 수가 24개로 늘어나 그리드 조정
        num_rows = 6
        num_cols = 4
        
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
                
                # Use on_click callback for immediate response
                cols[j].button(
                    option, 
                    key=f"q{i}_{option}", 
                    use_container_width=True, 
                    type=button_style,
                    on_click=answer_click,
                    args=(i, option)
                )
            
            st.markdown("<hr>", unsafe_allow_html=True)
        
        # Show results button if all questions are answered
        if len(st.session_state.answers) == len(questions):
            st.markdown("<div style='text-align: center; margin-top: 20px;'>", unsafe_allow_html=True)
            st.button(
                "결과 보기", 
                key="show_results", 
                use_container_width=True, 
                type="primary",
                on_click=results_click
            )
            st.markdown("</div>", unsafe_allow_html=True)

# Results page
elif st.session_state.page == 'results':
    st.title("창의가정신 역량검사 결과")
    
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
    st.button(
        "검사 다시하기", 
        key="back_to_assessment",
        on_click=reset_assessment
    )