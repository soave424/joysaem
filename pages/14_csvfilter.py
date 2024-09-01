import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# 기본 설정
st.title('Data Analysis and Visualization')

# 매칭 데이터 딕셔너리로 포함 (영어로 변환)
matching_dict = {
    'Tech1': ['Program1', 'Program9'],
    'Tech2': ['Program1'],
    'Tech3': ['Program1'],
    'Tech4': ['Program1'],
    'Tech5': ['Program1'],
    'Leadership6': ['Program2'],
    'Leadership7': ['Program2', 'Program7'],
    'Leadership8': ['Program2'],
    'Competence9': ['Program3', 'Program4', 'Program7'],
    'Competence10': ['Program4', 'Program5', 'Program7'],
    'Competence11': ['Program6'],
    'Competence12': ['Program3', 'Program4'],
    'Competence13': ['Program5'],
    'Competence14': ['Program2', 'Program4'],
    'Competence15': ['Program4', 'Program5'],
    'Competence16': ['Program5', 'Program6', 'Program7'],
    'Competence17': ['Program6', 'Program7'],
    'Competence18': ['Program4', 'Program5'],
    'Competence19': ['Program8'],
    'Competence20': ['Program4', 'Program5', 'Program6', 'Program7', 'Program8'],
    'Competence21': ['Program4', 'Program5', 'Program7'],
    'Competence22': ['Program6'],
    'Competence23': ['Program7', 'Program8'],
    'Competence24': ['Program4', 'Program5'],
    'Competence25': ['Program8'],
    'Competence26': ['Program5', 'Program6'],
    'Competence27': ['Program3', 'Program4'],
    'Competence28': ['Program6', 'Program9'],
    'Competence29': ['Program6', 'Program9'],
}

# CSV 파일 업로드
uploaded_file = st.file_uploader("Upload your CSV file", type="csv")

if uploaded_file is not None:
    # 데이터프레임으로 변환
    df = pd.read_csv(uploaded_file)

    # 데이터 미리보기
    st.write("Uploaded Data:")
    st.dataframe(df)

    # 매칭된 프로그램별 분석 추가
    def calculate_program_averages(df, matching_dict, category):
        programs = matching_dict.get(category, [])
        valid_programs = [prog for prog in programs if prog in df.columns]  # 실제로 존재하는 프로그램만 선택
        df_programs = df[valid_programs].mean(axis=1) if valid_programs else pd.Series([np.nan] * len(df))
        return df_programs

    df['Tech_Avg'] = calculate_program_averages(df, matching_dict, 'Tech1')
    df['Leadership_Avg'] = calculate_program_averages(df, matching_dict, 'Leadership6')
    df['Competence_Avg'] = calculate_program_averages(df, matching_dict, 'Competence9')

    st.header('Category Averages')
    st.write(df[['Tech_Avg', 'Leadership_Avg', 'Competence_Avg']])

    # 시각화
    st.header('Category Score Visualization')
    plt.figure(figsize=(12, 6))
    sns.boxplot(data=df[['Tech_Avg', 'Leadership_Avg', 'Competence_Avg']])
    plt.title('Score Distribution by Category')
    st.pyplot(plt)

    # 특정 인물의 선택 분석
    st.header('Individual Analysis')
    selected_person = st.selectbox('Select a person for analysis', df.index)

    if selected_person:
        st.write(f"Score analysis for {selected_person}:")
        st.write(df.loc[selected_person])

        plt.figure(figsize=(10, 4))
        df.loc[selected_person].drop(['Tech_Avg', 'Leadership_Avg', 'Competence_Avg']).plot(kind='bar')
        plt.title(f"{selected_person}'s Score Distribution")
        st.pyplot(plt)

    # 결과 저장
    st.header('Save Analysis Results')
    if st.button('Save as CSV'):
        result_csv = df.to_csv(index=False)
        st.download_button("Download", data=result_csv, file_name="analysis_results.csv", mime="text/csv")

else:
    st.write("Please upload a CSV file.")
