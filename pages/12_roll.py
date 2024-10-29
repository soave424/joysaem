# app.py
import streamlit as st
from dotenv import load_dotenv  
import pandas as pd
import os

# 환경 변수로부터 CSV 파일 경로 가져오기
CSV_PATH = os.getenv('CSV_FILE_PATH', 'hidden_data.csv')

# CSV 파일 로드 함수 (캐싱 적용)
@st.cache_data
def load_data():
    # CSV 파일 읽기
    df = pd.read_csv(CSV_PATH)
    return df

# 데이터 로드
data = load_data()

# Streamlit UI 구성
st.title("강좌 신청 조회")

# 사용자 입력
name = st.text_input("이름을 입력하세요:")
phone_number = st.text_input("전화번호를 입력하세요:")

# 조회 버튼이 눌리면 필터링 수행
if st.button("조회"):
    # 이름과 전화번호로 필터링하여 사용자 데이터 가져오기
    user_data = data[(data['이름'] == name) & (data['전화번호'] == phone_number)]
    
    if not user_data.empty:
        courses = user_data['강좌명'].tolist()
        st.write(f"{name}님이 신청한 강좌:")
        for course in courses[:3]:  # 최대 3개 강좌 출력
            st.write(f"- {course}")
    else:
        st.write("해당 정보가 없습니다. 이름과 전화번호를 확인해주세요.")
