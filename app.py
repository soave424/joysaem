import streamlit as st
from google_play_scraper import app, search
from google_play_scraper.exceptions import NotFoundError

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

        # 검색 결과를 표시하고 사용자가 선택할 수 있게 함
        app_options = {f"{app['title']} ({app['appId']})": app['appId'] for app in search_results}
        app_id = st.selectbox("Select an app from the list:", options=list(app_options.values()), format_func=lambda x: app_options[x])

        # 선택된 앱 ID로 앱 세부 정보 검색
        app_details = app(
            app_id,
            lang='ko',
            country='kr'
        )

        # 앱 세부 정보 표시
        st.write(f"**App Name:** {app_details['title']}")
        st.write(f"**Developer:** {app_details['developer']}")
        st.write(f"**Rating:** {app_details['score']}")
        st.write(f"**Description:** {app_details['description']}")
        st.image(app_details['icon'], width=100)  # 앱 아이콘 표시
        st.write(f"**Download Link:** [Link](https://play.google.com/store/apps/details?id={app_id})")
    except NotFoundError:
        st.error('App not found. Please check the name and try again.')
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
