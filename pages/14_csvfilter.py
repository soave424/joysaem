import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# 기본 설정
st.title('데이터 분석 및 시각화')

# CSV 파일 업로드
uploaded_file = st.file_uploader("CSV 파일을 업로드하세요", type="csv")

if uploaded_file is not None:
    # 데이터프레임으로 변환
    try:
        df = pd.read_csv(uploaded_file, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(uploaded_file, encoding='cp949')
    
    # 데이터 미리보기
    st.write("업로드된 데이터:")
    st.dataframe(df)
    
    # 기초 통계량
    st.header('기초 통계량')
    st.write(df.describe())
    
    # 각 영역별 평균 계산
    st.header('영역별 평균 계산')
    # 예를 들어, '기술'과 '리더십', '역량'으로 분리한다고 가정
    # 영역 이름에 따라 열을 그룹화하여 평균 계산
    df['기술_평균'] = df.filter(like='기술').mean(axis=1)
    df['리더십_평균'] = df.filter(like='리더십').mean(axis=1)
    df['역량_평균'] = df.filter(like='역량').mean(axis=1)
    
    st.write(df[['기술_평균', '리더십_평균', '역량_평균']])
    
    # 시각화
    st.header('영역별 점수 시각화')
    plt.figure(figsize=(12, 6))
    sns.boxplot(data=df[['기술_평균', '리더십_평균', '역량_평균']])
    plt.title('영역별 점수 분포')
    st.pyplot(plt)
    
    # 특정 인물의 선택 분석
    st.header('특정 인물 분석')
    selected_person = st.selectbox('분석할 사람을 선택하세요', df.index)
    
    if selected_person:
        st.write(f"{selected_person}의 점수 분석:")
        st.write(df.loc[selected_person])
        
        plt.figure(figsize=(10, 4))
        df.loc[selected_person].drop(['기술_평균', '리더십_평균', '역량_평균']).plot(kind='bar')
        plt.title(f"{selected_person}의 점수 분포")
        st.pyplot(plt)

    # 결과 저장
    st.header('분석 결과 저장')
    if st.button('CSV로 결과 저장'):
        result_csv = df.to_csv(index=False)
        st.download_button("다운로드", data=result_csv, file_name="analysis_results.csv", mime="text/csv")

else:
    st.write("CSV 파일을 업로드해주세요.")
