import streamlit as st
from google_play_scraper import app

# 스트림릿 앱의 타이틀 설정
st.title('Google Play Store App Searcher')

# 사용자 입력 받기
app_name = st.text_input('Enter the name of the app to search for:')

# 검색 버튼
if st.button('Search'):
    # 구글 플레이 스토어에서 앱 검색
    result = app(app_name, lang='ko', country='kr')  # 앱 이름, 언어 및 국가 설정
    if result:
        # 검색 결과 표시
        st.write(f"**App Name:** {result['title']}")
        st.write(f"**Developer:** {result['developer']}")
        st.write(f"**Rating:** {result['score']}")
        st.write(f"**Download Link:** [Link](https://play.google.com/store/apps/details?id={result['appId']})")
    else:
        st.write('No results found.')
