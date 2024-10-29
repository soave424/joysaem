# app.py
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()

# 환경 변수로부터 CSV 파일 경로 가져오기
CSV_PATH = os.getenv('CSV_FILE_PATH', 'csv/hidden_data.csv')

# 강좌 정보 사전
course_info = {
    "초등형 MBTI 클래시파이 : 웹개발스토리와 감정소진없이 학급경영하기": ("김태림쌤", "A1실"),
    "창업과 투자 그리고 기업가정신까지!? 일석삼조 효과의 '어쩌다 초등 사장' 프로젝트": ("쭈니쌤", "A2실"),
    "경제교육보드게임, 캐쉬플로우": ("박민수쌤", "A3실"),
    "왕초보도 따라하는 학급화폐 1년 로드맵": ("좋아유쌤", "A4실"),
    "내 아이의 금융 문해력 기르기": ("댈님", "A5실"),
    "도구없이 누구나 할 수 있는 교육마술": ("이화수쌤", "A6실"),
    "이렇게만 따라하세요! 20대 내 집 마련 루트": ("가드닝쌤", "A1실"),
    "코로나 실전 투자 경험을 통해 배운 행복한 부자로 가는 길": ("노현진쌤", "A2실"),
    "은또링샘의 친절한 재무제표 분석 (feat. 미리 캔버스)": ("은또링쌤", "A3실"),
    "내집마련 도전기: 꿈을 현실로 만드는 첫걸음": ("먹태쌤", "A4실"),
    "학교에서 시작하는 부수입 노하우": ("퇴근맨", "A5실"),
    "부린이도 할 수 있다! 같은 돈으로 더 오르는 내집 마련 A to Z": ("홍당무쌤", "A1실"),
    "교사를 위한 퍼스널 브랜딩 & 꼬꼬무 부수입 by 진격의홍쌤": ("진격의홍쌤", "A2실"),
    "미친 자에게 건배를: 부동산 투자에 미친 자의 이야기": ("다니쌤", "A3실"),
    "소비형 인간에서 저축형 인간 마인드셋하기": ("따롱쌤", "A4실"),
    "선생님의 돈공부: 재무관리와 내 삶 기획하기": ("달구쌤", "A5실")
}

# CSV 파일 로드 함수 (캐싱 적용)
@st.cache_data
def load_data():
    df = pd.read_csv(CSV_PATH)
    return df

# 데이터 로드
data = load_data()

# Streamlit UI 구성
st.title("강좌 신청 조회 및 등록 관리")

# 사용자 입력
name = st.text_input("이름을 입력하세요:")
phone_suffix = st.text_input("전화번호 뒷자리를 입력하세요:")

# CSS 스타일 추가
st.markdown("""
    <style>
        /* 배경 및 텍스트 색상 */
        body {
            background-color: #f0f2f6;
            color: #333333;
        }

        /* 제목 스타일 */
        .stApp h1 {
            color: #4c6ef5;
            font-weight: 700;
            font-size: 2rem;
            margin-bottom: 1rem;
        }

        /* 텍스트 입력 및 버튼 스타일 */
        .stTextInput, .stButton button {
            border-radius: 8px;
            padding: 8px;
            font-size: 1rem;
        }

        /* 표 스타일 */
        .stTable {
            background-color: #ffffff;
            border: 1px solid #d0e2f2;
            border-radius: 10px;
            overflow: hidden;
        }

        .stTable tr:nth-child(even) {background-color: #e8f4fa;} /* 연한 하늘색 */
        .stTable th {
            background-color: #b3d9ff;  /* 하늘색 */
            color: black;
            padding: 10px;
            text-align: left;
        }
        .stTable td {
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #d0e2f2;
        }
    </style>
""", unsafe_allow_html=True)

# 조회 버튼이 눌리면 필터링 수행
if st.button("조회"):
    # 전화번호 뒷자리 필터링을 위해 '전번' 열에서 뒷자리 부분만 추출
    data['전화번호_뒷자리'] = data['전번'].astype(str).str[-4:]

    # 이름과 전화번호 뒷자리로 필터링하여 사용자 데이터 가져오기
    user_data = data[(data['이름'] == name) & (data['전화번호_뒷자리'] == phone_suffix)]
    
    if not user_data.empty:
        # 신청한 강좌 정보를 테이블 형식으로 출력
        courses = user_data[['선택 강좌 1', '선택 강좌 2', '선택 강좌 3']].values.flatten()
        course_data = []

        for course in courses[:3]:  # 최대 3개 강좌만 처리
            if pd.notna(course):  # 비어있지 않은 경우에만 처리
                # "강좌명 / 강사명" 형태에서 강좌명과 강사명을 분리
                parts = course.split('/')
                course_name = parts[0].strip()
                
                # 강사명과 강의실 자동 채우기
                instructor, classroom = course_info.get(course_name, ("", ""))
                
                # 강사명이나 강의실 정보가 비어 있는 경우 채움
                instructor = instructor if len(parts) > 1 else instructor
                course_data.append({"강좌명": course_name, "강사명": instructor, "강의실": classroom})

        # DataFrame에 인덱스를 1부터 시작하도록 설정
        course_df = pd.DataFrame(course_data).reset_index(drop=True)
        course_df.index = course_df.index + 1  # 인덱스를 1부터 시작하도록 조정

        # 테이블 출력
        st.write(f"{name}님이 신청한 강좌:")
        st.table(course_df.style.set_properties(**{'border-color': '#d0e2f2'}))  # 테두리 색상 추가
    else:
        st.write("해당 정보가 없습니다. 이름과 전화번호 뒷자리를 확인해주세요.")
