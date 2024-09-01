import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.font_manager as fm

# 기본 설정
st.title('Data Analysis and Visualization')

# CSV 파일 업로드
uploaded_file = st.file_uploader("Upload a CSV file", type="csv")

if uploaded_file is not None:
    # 데이터프레임으로 변환
    try:
        df = pd.read_csv(uploaded_file, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(uploaded_file, encoding='cp949')
    
    # 데이터 열 이름 영어로 변경
    df.columns = df.columns.str.replace('기술', 'Skill').str.replace('리더십', 'Leadership').str.replace('역량', 'Competency')
    
    # 데이터 미리보기
    st.write("Uploaded Data:")
    st.dataframe(df)
    
    # 기초 통계량
    st.header('Basic Statistics')
    st.write(df.describe())
    
    # 각 영역별 평균 계산
    st.header('Calculate Average Scores by Category')
    df['Skill_Avg'] = df.filter(like='Skill').mean(axis=1)
    df['Leadership_Avg'] = df.filter(like='Leadership').mean(axis=1)
    df['Competency_Avg'] = df.filter(like='Competency').mean(axis=1)
    
    st.write(df[['Skill_Avg', 'Leadership_Avg', 'Competency_Avg']])
    
    # 시각화
    st.header('Visualization of Scores by Category')
    plt.figure(figsize=(12, 6))
    sns.boxplot(data=df[['Skill_Avg', 'Leadership_Avg', 'Competency_Avg']])
    plt.title('Distribution of Scores by Category')
    st.pyplot(plt)
    
    # 특정 인물의 선택 분석
    st.header('Individual Analysis')
    
    # 인덱스를 선택할 수 있도록 설정 (기본적으로 문자열이 아닌 정수 인덱스를 사용)
    df.index = pd.Index(range(df.shape[0]), name="index")
    selected_person = st.selectbox('Select a person for analysis', df.index)

    if selected_person is not None:
        st.write(f"Analysis for Person {selected_person}:")
        st.write(df.iloc[selected_person])
        
        plt.figure(figsize=(10, 4))
        df.iloc[selected_person].drop(['Skill_Avg', 'Leadership_Avg', 'Competency_Avg']).plot(kind='bar')
        plt.title(f"Score Distribution for Person {selected_person}")
        st.pyplot(plt)

    # 결과 저장
    st.header('Save Analysis Results')
    if st.button('Save as CSV'):
        result_csv = df.to_csv(index=False)
        st.download_button("Download", data=result_csv, file_name="analysis_results.csv", mime="text/csv")

else:
    st.write("Please upload a CSV file.")
