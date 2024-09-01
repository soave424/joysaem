import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Matching dictionary (from your earlier example)
matching_dict = {
    'Tech1': ['Program1', 'Program5'],
    'Tech2': ['Program1'],
    'Tech3': ['Program1'],
    'Tech4': ['Program1'],
    'Tech5': ['Program1'],
    'Leadership6': ['Program2'],
    'Leadership7': ['Program2', 'Program5'],
    'Leadership8': ['Program2'],
    'Competence9': ['Program2', 'Program3', 'Program5'],
    'Competence10': ['Program3', 'Program4', 'Program5'],
    'Competence11': ['Program6'],
    'Competence12': ['Program2', 'Program3'],
    'Competence13': ['Program4'],
    'Competence14': ['Program3', 'Program5'],
    'Competence15': ['Program4', 'Program5'],
    'Competence16': ['Program4', 'Program6', 'Program7'],
    'Competence17': ['Program4', 'Program6', 'Program7'],
    'Competence18': ['Program4', 'Program5'],
    'Competence19': ['Program7'],
    'Competence20': ['Program4', 'Program5', 'Program6', 'Program7'],
    'Competence21': ['Program4', 'Program5', 'Program7'],
    'Competence22': ['Program7'],
    'Competence23': ['Program6', 'Program7'],
    'Competence24': ['Program4', 'Program5'],
    'Competence25': ['Program7'],
    'Competence26': ['Program6', 'Program7'],
    'Competence27': ['Program2', 'Program3'],
    'Competence28': ['Program4', 'Program7'],
    'Competence29': ['Program4', 'Program7'],
}

# 기본 설정
st.title('데이터 분석 및 시각화')

# CSV 파일 업로드
uploaded_file = st.file_uploader("CSV 파일을 업로드하세요", type="csv")

if uploaded_file is not None:
    # 데이터프레임으로 변환
    df = pd.read_csv(uploaded_file)
    
    # 데이터 미리보기
    st.write("업로드된 데이터:")
    st.dataframe(df)
    
    # 기초 통계량
    st.header('기초 통계량')
    st.write(df.describe())
    
    # 각 영역별 평균 계산
    st.header('영역별 평균 계산')
    df['Tech_Avg'] = df.filter(like='Tech').mean(axis=1)
    df['Leadership_Avg'] = df.filter(like='Leadership').mean(axis=1)
    df['Competence_Avg'] = df.filter(like='Competence').mean(axis=1)
    
    st.write(df[['Tech_Avg', 'Leadership_Avg', 'Competence_Avg']])
    
    # 프로그램별 평균 계산 함수
    def calculate_program_averages(df, matching_dict, category):
        programs = matching_dict.get(category, [])
        df_programs = df[programs].mean(axis=1) if programs else pd.Series([np.nan] * len(df))
        return df_programs
    
    # 모든 프로그램의 평균을 계산하여 추가
    for category in matching_dict.keys():
        df[category + '_Avg'] = calculate_program_averages(df, matching_dict, category)
    
    st.write("프로그램별 평균:")
    st.dataframe(df)
    
    # 시각화
    st.header('영역별 점수 시각화')
    plt.figure(figsize=(12, 6))
    sns.boxplot(data=df[['Tech_Avg', 'Leadership_Avg', 'Competence_Avg']])
    plt.title('Score Distribution by Category')
    st.pyplot(plt)
    
    # 프로그램별 점수 분포 시각화
    st.header('Score Distribution by Program')
    plt.figure(figsize=(14, 7))
    program_columns = [col + '_Avg' for col in matching_dict.keys()]
    sns.boxplot(data=df[program_columns])
    plt.title('Score Distribution by Program')
    plt.xticks(rotation=90)
    st.pyplot(plt)

    # 특정 인물의 선택 분석
    st.header('특정 인물 분석')
    selected_person = st.selectbox('분석할 사람을 선택하세요', df.index)
    
    if selected_person:
        st.write(f"{selected_person}의 점수 분석:")
        st.write(df.loc[selected_person])
        
        plt.figure(figsize=(10, 4))
        df.loc[selected_person].drop(['Tech_Avg', 'Leadership_Avg', 'Competence_Avg']).plot(kind='bar')
        plt.title(f"{selected_person}의 점수 분포")
        st.pyplot(plt)

    # 결과 저장
    st.header('분석 결과 저장')
    if st.button('CSV로 결과 저장'):
        result_csv = df.to_csv(index=False)
        st.download_button("다운로드", data=result_csv, file_name="analysis_results.csv", mime="text/csv")

else:
    st.write("CSV 파일을 업로드해주세요.")
