from urllib.parse import quote_plus
import streamlit as st
from google_play_scraper import app, search
from google_play_scraper.exceptions import NotFoundError
import pandas as pd

st.title('Google Play Store App Searcher')

app_name_query = st.text_input('Enter the name of the app to search for:')

if st.button('Search'):
    try:
        # 구글 플레이 스토어에서 앱 이름으로 검색
        search_results = search(
            app_name_query,
            lang='ko',  # 언어 설정
            country='kr'  # 국가 설정
        )
        if not search_results:
            st.error("No apps found. Try a different query.")
            st.stop()

        # 가장 관련성 높은 앱의 세부 정보를 검색
        most_relevant_app = search_results[0]  # 첫 번째 검색 결과 선택
        app_id = most_relevant_app['appId']

        app_details = app(
            app_id,
            lang='ko',
            country='kr'
        )

        # 데이터를 DataFrame으로 만들기
        data = {
            "Category": ["App Name", "Developer", "Rating", "Description", "Download Link"],
            "Details": [
                app_details['title'],
                app_details['developer'],
                app_details['score'],
                app_details['description'],
                f"[Link](https://play.google.com/store/apps/details?id={app_id})"
            ]
        }
        df = pd.DataFrame(data)

        # 앱 아이콘과 함께 표 표시
        st.image(app_details['icon'], width=100)  # 앱 아이콘 표시
        st.table(df)  # 데이터프레임을 표로 표시
    except NotFoundError:
        st.error('App not found. Please check the name and try again.')
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
