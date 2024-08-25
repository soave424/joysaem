import streamlit as st
from google_play_scraper import app, search
from google_play_scraper.exceptions import NotFoundError
from urllib.parse import quote_plus


st.title('Multiple Google Play Store App Searcher')

app_names_input = st.text_area('Enter the names of the apps to search for, separated by commas:')

if st.button('Search for Apps'):
    app_names = [name.strip() for name in app_names_input.split(',') if name.strip()]
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
                download_link = f"https://play.google.com/store/apps/details?id={app_id}"
                results.append((app_name, download_link))
            else:
                results.append((app_name, "No app found."))
        except NotFoundError:
            results.append((app_name, "App not found."))
        except Exception as e:
            results.append((app_name, f"An error occurred: {str(e)}"))

    # Display results
    if results:
        st.write("Download Links for Entered Apps:")
        for result in results:
            st.write(f"**{result[0]}:** [Download Link]({result[1]})" if "http" in result[1] else f"**{result[0]}:** {result[1]}")

