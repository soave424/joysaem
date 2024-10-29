# app.py
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
import os
from datetime import datetime
import json

# .env 파일 로드
load_dotenv()

# 환경 변수로부터 CSV 및 JSON 파일 경로 가져오기
CSV_PATH = os.getenv('CSV_FILE_PATH', 'csv/hidden_data.csv')
JSON_PATH = os.getenv('JSON_FILE_PATH', 'data/registration_status.json')

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

# 조회 버튼이 눌리면 필터링 수행
if st.button("조회"):
    # 전화번호 뒷자리 필터링을 위해 '전번' 열에서 뒷자리 부분만 추출
    data['전화번호_뒷자리'] = data['전번'].astype(str).str[-4:]

    # 이름과 전화번호 뒷자리로 필터링하여 사용자 데이터 가져오기
    user_data = data[(data['이름'] == name) & (data['전화번호_뒷자리'] == phone_suffix)]
    
    if not user_data.empty:
        # 신청한 강좌 정보 출력
        courses = user_data[['선택 강좌 1', '선택 강좌 2', '선택 강좌 3']].values.flatten()
        st.write(f"{name}님이 신청한 강좌:")
        for course in courses[:3]:  # 최대 3개 강좌 출력
            st.write(f"- {course}")
        
        # 등록 완료 및 취소 버튼 추가
        if st.button("등록 완료"):
            try:
                # JSON 파일 업데이트 - 등록 상태와 시간 업데이트
                registration_status = {
                    "이름": name,
                    "전화번호 뒷자리": phone_suffix,
                    "등록": "등록",
                    "시간": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                with open(JSON_PATH, 'w') as json_file:
                    json.dump(registration_status, json_file, ensure_ascii=False, indent=4)
                
                # 등록 완료 메시지와 신청한 강좌 안내
                st.success("연수에 참여해주셔서 감사합니다!")
                st.write("신청하신 강좌:")
                for course in courses[:3]:  # 최대 3개 강좌 출력
                    st.write(f"- {course}")
            except Exception as e:
                st.error(f"등록 중 오류가 발생했습니다: {e}")

        elif st.button("등록 취소"):
            try:
                # JSON 파일 업데이트 - 등록 취소 상태 (빈 셀 처리)
                registration_status = {
                    "이름": name,
                    "전화번호 뒷자리": phone_suffix,
                    "등록": "",
                    "시간": ""
                }
                with open(JSON_PATH, 'w') as json_file:
                    json.dump(registration_status, json_file, ensure_ascii=False, indent=4)
                st.write("등록이 취소되었습니다.")
            except Exception as e:
                st.error(f"등록 취소 중 오류가 발생했습니다: {e}")
    else:
        st.write("해당 정보가 없습니다. 이름과 전화번호 뒷자리를 확인해주세요.")
