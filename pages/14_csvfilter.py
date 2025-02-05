import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# 기본 설정
st.title('Data Analysis and Visualization')

# CSV 파일 업로드
uploaded_file = st.file_uploader("Upload CSV file", type="csv")

# 매칭 사전 (영어로 변경)
matching_dict = {
    'Tech1': ['Program1', 'Program9'],
    'Tech2': ['Program1'],
    'Tech3': ['Program1'],
    'Tech4': ['Program1'],
    'Tech5': ['Program1'],
    'Leadership6': ['Program3'],
    'Leadership7': ['Program3', 'Program9'],
    'Leadership8': ['Program3'],
    'Competence9': ['Program2', 'Program3', 'Program9'],
    'Competence10': ['Program5', 'Program7', 'Program8'],
    'Competence11': ['Program7'],
    'Competence12': ['Program2', 'Program3'],
    'Competence13': ['Program6'],
    'Competence14': ['Program3', 'Program5'],
    'Competence15': ['Program5', 'Program6'],
    'Competence16': ['Program6', 'Program7', 'Program8'],
    'Competence17': ['Program7', 'Program8', 'Program9'],
    'Competence18': ['Program5', 'Program7'],
    'Competence19': ['Program8'],
    'Competence20': ['Program5', 'Program6', 'Program7', 'Program8', 'Program9'],
    'Competence21': ['Program5', 'Program7', 'Program8'],
    'Competence22': ['Program7'],
    'Competence23': ['Program8', 'Program9'],
    'Competence24': ['Program5', 'Program7'],
    'Competence25': ['Program8'],
    'Competence26': ['Program6', 'Program8'],
    'Competence27': ['Program2', 'Program3'],
    'Competence28': ['Program6', 'Program9'],
    'Competence29': ['Program6', 'Program9']
}

# 한글 열 이름을 영어로 변환하는 함수
def translate_columns(df):
    translation_dict = {
        '기술': 'Tech',
        '리더십': 'Leadership',
        '역량': 'Competence'
    }
    new_columns = []
    for col in df.columns:
        for key in translation_dict:
            if key in col:
                col = col.replace(key, translation_dict[key])
        new_columns.append(col)
    df.columns = new_columns
    return df

# 프로그램 평균 계산 함수
def calculate_program_averages(df, matching_dict, key):
    programs = matching_dict.get(key, [])
    valid_programs = [p for p in programs if p in df.columns]
    if valid_programs:
        df_programs = df[valid_programs].mean(axis=1)
    else:
        df_programs = pd.Series([np.nan] * len(df))
    return df_programs

if uploaded_file is not None:
    # 데이터프레임으로 변환
    df = pd.read_csv(uploaded_file)
    
    # 한글 열 이름을 영어로 변환
    df = translate_columns(df)
    
    # 각 항목별로 프로그램 평균 계산
    df['Tech_Avg'] = df.filter(like='Tech').mean(axis=1)
    df['Leadership_Avg'] = df.filter(like='Leadership').mean(axis=1)
    df['Competence_Avg'] = df.filter(like='Competence').mean(axis=1)
    
    # 프로그램별 평균 계산
    program_averages = {}
    for program in ['Program1', 'Program2', 'Program3', 'Program4', 'Program5', 'Program6', 'Program7', 'Program8', 'Program9']:
        program_columns = [key for key, programs in matching_dict.items() if program in programs]
        if program_columns:
            df[program + '_Avg'] = df[program_columns].mean(axis=1)
            program_averages[program] = df[program + '_Avg']
        else:
            df[program + '_Avg'] = np.nan
    
    # 평균값 출력
    st.header('Calculated Averages')
    st.write(df[['Tech_Avg', 'Leadership_Avg', 'Competence_Avg'] + [f"{program}_Avg" for program in ['Program1', 'Program2', 'Program3', 'Program4', 'Program5', 'Program6', 'Program7', 'Program8', 'Program9']]])
    
    # 기초 통계량
    st.header('Descriptive Statistics')
    st.write(df.describe())
    
    # 시각화
    st.header('Score Distribution by Category')
    if not df[['Tech_Avg', 'Leadership_Avg', 'Competence_Avg']].isnull().all().all():
        plt.figure(figsize=(12, 6))
        sns.boxplot(data=df[['Tech_Avg', 'Leadership_Avg', 'Competence_Avg']])
        plt.title('Distribution of Scores by Category')
        st.pyplot(plt)
    else:
        st.warning("All average columns are empty. Skipping plot.")
    
    # 프로그램별 시각화
    st.header('Score Distribution by Program')
    program_data = df[[f"{program}_Avg" for program in program_averages.keys()]].dropna(axis=1, how='all')
    if not program_data.empty:
        plt.figure(figsize=(12, 6))
        sns.boxplot(data=program_data)
        plt.title('Distribution of Scores by Program')
        plt.xticks(rotation=90)
        st.pyplot(plt)
    else:
        st.warning("All program average columns are empty. Skipping plot.")
    
    # 특정 인물의 선택 분석
    st.header('Analysis of Specific Person')
    # 인덱스를 문자열로 변환 (숫자형 인덱스인 경우도 포함하여 처리)
    df.index = df.index.astype(str)
    selected_person = st.selectbox('Select a person to analyze', df.index)
    
    if selected_person:
        st.write(f"Score analysis for {selected_person}:")
        st.write(df.loc[selected_person])
        
        plt.figure(figsize=(10, 4))
        df.loc[selected_person].drop(['Tech_Avg', 'Leadership_Avg', 'Competence_Avg'] + [f"{program}_Avg" for program in program_averages.keys()]).plot(kind='bar')
        plt.title(f"Score distribution for {selected_person}")
        st.pyplot(plt)
    
    # 선택된 인원의 평균값 분석 및 시각화
    st.header('Analysis of Selected People')
    selected_people = st.multiselect('Select people to calculate the average', df.index)
    
    if selected_people:
        selected_df = df.loc[selected_people]
        avg_df = selected_df.mean()

        st.write("Average scores for selected people:")
        st.write(avg_df)
        
        plt.figure(figsize=(10, 6))
        avg_df.drop(['Tech_Avg', 'Leadership_Avg', 'Competence_Avg'] + [f"{program}_Avg" for program in program_averages.keys()]).plot(kind='bar')
        plt.title('Average Score Distribution for Selected People')
        st.pyplot(plt)
    
    # 결과 저장
    st.header('Save Analysis Results')
    if st.button('Save as CSV'):
        result_csv = df.to_csv(index=False)
        st.download_button("Download", data=result_csv, file_name="analysis_results.csv", mime="text/csv")

else:
    st.write("Please upload a CSV file.")
