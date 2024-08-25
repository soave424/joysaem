import streamlit as st
from google_play_scraper import app, search
from google_play_scraper.exceptions import NotFoundError
import re

st.title('Multiple Google Play Store App Searcher')

app_names_input = st.text_area('Enter the names of the apps to search for, separated by commas or new lines:')

if st.button('Search for Apps'):
    # 파싱 로직을 수정하여 쉼표와 줄바꿈 모두를 구분자로 사용
    app_names = re.split(r'[,\n]+', app_names_input)
    app_names = [name.strip() for name in app_names if name.strip()]
    if not app_names:
        st.error("Please enter at least one app name.")
        st.stop()

    results = []

    for app_name in app_names:
        try:
            # Use the search function to get the most relevant app ID for each app name
            search_results = search(
                app_name,
                lang='ko',  # Language setting
                country='kr'  # Country setting
            )
            if search_results:
                # Assuming the first result is the most relevant one
                most_relevant_app = search_results[0]
                app_id = most_relevant_app['appId']
                # Retrieve app details
                app_details = app(app_id, lang='ko', country='kr')
                download_link = f"https://play.google.com/store/apps/details?id={app_id}"
                # Append both app details and download link to the results
                results.append((app_name, download_link, app_details))
            else:
                results.append((app_name, "No app found.", None))
        except NotFoundError:
            results.append((app_name, "App not found.", None))
        except Exception as e:
            results.append((app_name, f"An error occurred: {str(e)}", None))

    # Display results
    if results:
        st.write("Download Links for Entered Apps:")
        for result in results:
            app_name, link, details = result
            if details:
                st.write(f"**App Name:** {details['title']}")
                st.image(details['icon'], width=100)  # Display app icon
                st.write(f"**Download Link:** [Download]({link})")
            else:
                st.write(f"**{app_name}:** {link}")
