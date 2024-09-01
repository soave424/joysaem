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
    'Leadership6': ['Program2'],
    'Leadership7': ['Program2', 'Program9'],
    'Leadership8': ['Program2'],
    'Competence9': ['Program3', 'Program4', 'Program7', 'Program9'],
    'Competence10': ['Program5', 'Program7', 'Program8'],
    'Competence11': ['Program8'],
    'Competence12': ['Program3', 'Program7'],
    'Competence13': ['Program6'],
    'Competence14': ['Program2', 'Program4'],
    'Competence15': ['Program5', 'Program7'],
    'Competence16': ['Program5', 'Program7', 'Program8'],
    'Competence17': ['Program7', 'Program8', 'Program9'],
    'Competence18': ['Program5', 'Program8'],
    'Competence19': ['Program9'],
    'Competence20': ['Program5', 'Program7', 'Program8', 'Program9'],
    'Competence21': ['Program5', 'Program8', 'Program9'],
    'Competence22': ['Program7'],
    'Competence23': ['Program8', 'Program9'],
    'Competence24': ['Program5', 'Program8'],
    'Competence25': ['Program9'],
    'Competence26': ['Program7', 'Program8'],
    'Competence27': ['Program3', 'Program7'],
    'Competence28': ['Program6', 'Program8'],
    'Competence29': ['Program6', 'Program8']
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
    if programs:  # 프로그램 목록이 있으면
        df_programs = df[programs].mean(axis=1)
    else:
        df_programs = pd.Series([np.nan] * len(df))  # NaN으로 채운 시리즈 반환
    return df_programs

if uploaded_file is not None:
    # 데이터프레임으로 변환
    df = pd.read_csv(uploaded_file)
    
    # 한글 열 이름을 영어로 변환
    df = translate_columns(df)
    
    # 데이터 미리보기
    st.write("Uploaded Data:")
    st.dataframe(df)
    
    # 각 항목별로 프로그램 평균 계산
    df['Tech_Avg'] = calculate_program_averages(df, matching_dict, 'Tech1')
    df['Leadership_Avg'] = calculate_program_averages(df, matching_dict, 'Leadership6')
    df['Competence_Avg'] = calculate_program_averages(df, matching_dict, 'Competence9')
    
    # 평균값 출력
    st.header('Calculated Averages')
    st.write(df[['Tech_Avg', 'Leadership_Avg', 'Competence_Avg']])
    
    # 기초 통계량
    st.header('Descriptive Statistics')
    st.write(df.describe())
    
    # 시각화
    st.header('Score Distribution by Category')
    plt.figure(figsize=(12, 6))
    sns.boxplot(data=df[['Tech_Avg', 'Leadership_Avg', 'Competence_Avg']])
    plt.title('Distribution of Scores by Category')
    st.pyplot(plt)
    
    # 특정 인물의 선택 분석
    st.header('Analysis of Specific Person')
    selected_person = st.selectbox('Select a person to analyze', df.index)
    
    if selected_person:
        st.write(f"Score analysis for {selected_person}:")
        st.write(df.loc[selected_person])
        
        plt.figure(figsize=(10, 4))
        df.loc[selected_person].drop(['Tech_Avg', 'Leadership_Avg', 'Competence_Avg']).plot(kind='bar')
        plt.title(f"Score distribution for {selected_person}")
        st.pyplot(plt)
    
    # 결과 저장
    st.header('Save Analysis Results')
    if st.button('Save as CSV'):
        result_csv = df.to_csv(index=False)
        st.download_button("Download", data=result_csv, file_name="analysis_results.csv", mime="text/csv")

else:
    st.write("Please upload a CSV file.")
