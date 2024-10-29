# app.py
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()

# 환경 변수로부터 CSV 파일 경로 가져오기
CSV_PATH = os.getenv('CSV_FILE_PATH', 'csv/hidden_data.csv')  # 기본 경로 설정

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
phone_suffix = st.text_input("전화번호 뒷자리를 입력하세요:")

# 조회 버튼이 눌리면 필터링 수행
if st.button("조회"):
    # 전화번호 뒷자리 필터링을 위해 '전번' 열에서 뒷자리 부분만 추출
    data['전화번호_뒷자리'] = data['전번'].astype(str).str[-4:]

    # 이름과 전화번호 뒷자리로 필터링하여 사용자 데이터 가져오기
    user_data = data[(data['이름'] == name) & (data['전화번호_뒷자리'] == phone_suffix)]
    
    if not user_data.empty:
        courses = user_data[['선택 강좌 1', '선택 강좌 2', '선택 강좌 3']].values.flatten()
        st.write(f"{name}님이 신청한 강좌:")
        for course in courses[:3]:  # 최대 3개 강좌 출력
            st.write(f"- {course}")
    else:
        st.write("해당 정보가 없습니다. 이름과 전화번호 뒷자리를 확인해주세요.")
