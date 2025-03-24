import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from PIL import Image
import io

# 사이드바가 접힌 상태로 시작
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# CSS를 사용하여 사이드바 완전히 숨기기
hide_sidebar_style = """
    <style>
        div[data-testid="stSidebar"] {display: none;}
    </style>
"""
st.markdown(hide_sidebar_style, unsafe_allow_html=True)

# # Set page configuration
# st.set_page_config(page_title="역량검사", layout="wide")

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

yeep_url = "https://yeep.go.kr/intro/coreCmptyIntro.do"

# Define answer options
options = ["전혀 그렇지 않다", "그렇지 않다", "보통", "그렇다", "매우 그렇다"]
option_values = {option: idx for idx, option in enumerate(options, 1)}

# Define competency categories - 대영역과 소영역 모두 정의
main_competencies = {
    "가치창출역량": [1, 2, 3, 4, 5, 6],
    "도전역량": [7, 8, 9, 10, 11, 12],
    "자기주도역량": [13, 14, 15, 16, 17, 18],
    "집단창의역량": [19, 20, 21, 22, 23, 24]
}

# 소영역 정의
sub_competencies = {
    "혁신성": [1, 2],
    "사회적 가치지향": [3, 4],
    "변화민첩성": [5, 6],
    "성취지향성": [7, 8],
    "위험감수역량": [9, 10],
    "회복탄력성": [11, 12],
    "자율성": [13, 14],
    "자기관리역량": [15, 16],
    "끈기": [17, 18],
    "공동의사결정": [19, 20],
    "자원연계": [21, 22],
    "협력성": [23, 24]
}

# 소영역과 대영역의 매핑
sub_to_main_mapping = {
    "혁신성": "가치창출역량",
    "사회적 가치지향": "가치창출역량",
    "변화민첩성": "가치창출역량",
    "성취지향성": "도전역량",
    "위험감수역량": "도전역량",
    "회복탄력성": "도전역량",
    "자율성": "자기주도역량",
    "자기관리역량": "자기주도역량",
    "끈기": "자기주도역량",
    "공동의사결정": "집단창의역량",
    "자원연계": "집단창의역량",
    "협력성": "집단창의역량"
}

# Main app logic
if st.session_state.page == 'assessment':
    # Create a two-column layout
    col1, col2 = st.columns([1, 3])
    
    # Header
    with col2:
        st.markdown("""
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <h1>창업가정신 핵심역량 간이검사</h1>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <p style="font-size: 16px;">아래 문항은 창업가정신과 관련한 생각이나 태도를 알아보기 위한 간이 검사 질문입니다. <br>
                    초등학교 4학년 이상의 학생은 아래 사이트에서 꼭 검사를 제대로 진행해주세요. <br>
                     <a href="yeep_url}" target="_blank">{https://yeep.go.kr/intro/coreCmptyIntro.do}</a>: <br>
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
        st.markdown("<h3 style='text-align: center;'>창업가정신 핵심역량<br>간이검사</h3>", unsafe_allow_html=True)
        
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
        
        # Calendar-like number grid - 문항 수가 24개
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
    
    # Calculate main competency scores
    main_scores = {}
    for competency, question_ids in main_competencies.items():
        competency_score = 0
        valid_questions = 0
        for q_id in question_ids:
            if q_id in st.session_state.answers:
                answer = st.session_state.answers[q_id]
                competency_score += option_values[answer]
                valid_questions += 1
        
        # Calculate average score (1-5 scale) if there are valid answers
        if valid_questions > 0:
            avg_score = competency_score / valid_questions
            main_scores[competency] = avg_score
    
    # Calculate sub competency scores
    sub_scores = {}
    for competency, question_ids in sub_competencies.items():
        competency_score = 0
        valid_questions = 0
        for q_id in question_ids:
            if q_id in st.session_state.answers:
                answer = st.session_state.answers[q_id]
                competency_score += option_values[answer]
                valid_questions += 1
        
        # Calculate average score (1-5 scale) if there are valid answers
        if valid_questions > 0:
            avg_score = competency_score / valid_questions
            sub_scores[competency] = avg_score
    
    # Create tabs for different result views
    tab1, tab2 = st.tabs(["영역별 결과", "응답 상세"])
    
    with tab1:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader(f"{st.session_state.student_info['name']}님의 대영역 역량 프로필")
            
            # Create data for chart
            chart_data = pd.DataFrame({
                '역량': list(main_scores.keys()),
                '점수': list(main_scores.values())
            })
            
            # Create bar chart for main competencies
            chart = alt.Chart(chart_data).mark_bar().encode(
                x=alt.X('점수:Q', scale=alt.Scale(domain=[0, 5])),
                y=alt.Y('역량:N', sort='-x'),
                color=alt.Color('역량:N', legend=None),
                tooltip=['역량', '점수']
            ).properties(
                height=300
            )
            
            st.altair_chart(chart, use_container_width=True)

            st.subheader(f"{st.session_state.student_info['name']}님의 소영역 역량 프로필")
            
            # Create data for chart
            sub_chart_data = pd.DataFrame({
                '역량': list(sub_scores.keys()),
                '점수': list(sub_scores.values()),
                '대영역': [sub_to_main_mapping[sub] for sub in sub_scores.keys()]
            })
            
            # Create bar chart for sub competencies
            sub_chart = alt.Chart(sub_chart_data).mark_bar().encode(
                x=alt.X('점수:Q', scale=alt.Scale(domain=[0, 5])),
                y=alt.Y('역량:N', sort='-x'),
                color=alt.Color('대영역:N'),
                tooltip=['역량', '점수', '대영역']
            ).properties(
                height=400
            )
            
            st.altair_chart(sub_chart, use_container_width=True)
        

    # tab1의 col2 내부에서 소영역별 상세 결과 부분을 수정
    with col2:
        st.subheader("영역별 결과")
        # 점수에 따라 내림차순 정렬 - 이미 있는 코드
        sorted_main_scores = dict(sorted(main_scores.items(), key=lambda item: item[1], reverse=True))

        # 대영역 결과 표시 (이미 있는 코드를 sorted_main_scores로 수정)
        for competency, score in sorted_main_scores.items():
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
                <h3>{emoji} {competency}: {level} <span style="font-size: 0.8em; color: #666;">({score:.1f}/5.0)<span></h3>
            </div>
            """, unsafe_allow_html=True)

        st.subheader("소영역별 상세 결과")
        # 점수에 따라 내림차순 정렬 - 이미 있는 코드
        sorted_sub_scores = dict(sorted(sub_scores.items(), key=lambda item: item[1], reverse=True))

        # 소영역 결과 표시 (수정된 코드는 sorted_sub_scores를 사용)
        for competency, score in sorted_sub_scores.items():
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
            
            # Get the main competency for this sub competency
            main_comp = sub_to_main_mapping[competency]
                
            st.markdown(f"""
            <div style="margin-bottom: 15px; padding: 10px; border-radius: 5px; border: 1px solid #ddd;">
                <h3>{emoji} {competency} <span style="font-size: 0.8em; color: #666;">({main_comp}_{score:.1f}/5.0)</span></h3>
            </div>
            """, unsafe_allow_html=True)

    with tab2:
        st.subheader("문항별 응답 결과")
        
        # 소영역 정보 추가
        response_data = []
        for i, question in enumerate(questions, 1):
            # 어떤 소영역에 속하는지 찾기
            sub_category = None
            for sub, qs in sub_competencies.items():
                if i in qs:
                    sub_category = sub
                    break
            
            # 어떤 대영역에 속하는지 찾기
            main_category = None
            for main, qs in main_competencies.items():
                if i in qs:
                    main_category = main
                    break
            
            response = st.session_state.answers.get(i, "미응답")
            response_data.append({
                "문항번호": i, 
                "질문": question, 
                "응답": response,
                "점수": option_values.get(response, 0) if response != "미응답" else 0,
                "소영역": sub_category,
                "대영역": main_category
            })
        
        response_df = pd.DataFrame(response_data)
        st.dataframe(response_df, use_container_width=True, hide_index=True)
    
    # Return to assessment button
    st.button(
        "검사 다시하기", 
        key="back_to_assessment",
        on_click=reset_assessment
    )