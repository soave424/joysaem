import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# 구글 시트에 접근하기 위한 설정
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

# JSON 파일의 경로 (서비스 계정 키)
creds = ServiceAccountCredentials.from_json_keyfile_name("path_to_your_credentials.json", scope)
client = gspread.authorize(creds)

# 구글 시트 열기
sheet = client.open("your_google_sheet_name").worksheet("Sheet1")

# 시트에서 모든 데이터 가져오기
data = sheet.get_all_records()

# 데이터를 pandas 데이터프레임으로 변환
df = pd.DataFrame(data)

st.title("Google Sheets Data")

# 데이터프레임 표시
st.dataframe(df)
