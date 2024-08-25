import streamlit as st
from google_play_scraper import app
from google_play_scraper.exceptions import NotFoundError
from urllib.parse import quote_plus

st.title('Google Play Store App Searcher')

app_name = st.text_input('Enter the name of the app to search for:')

if st.button('Search'):
    try:
        # URL 인코딩 추가
        safe_app_name = quote_plus(app_name)
        
        # 구글 플레이 스토어에서 앱 검색
        result = app(safe_app_name, lang='ko', country='kr')
        
        # 검색 결과 표시
        st.write(f"**App Name:** {result['title']}")
        st.write(f"**Developer:** {result['developer']}")
        st.write(f"**Rating:** {result['score']}")
        st.write(f"**Download Link:** [Link](https://play.google.com/store/apps/details?id={result['appId']})")
    except NotFoundError:
        st.error('App not found. Please check the name and try again.')
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
