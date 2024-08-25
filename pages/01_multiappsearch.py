import streamlit as st
from google_play_scraper import app, search
from google_play_scraper.exceptions import NotFoundError
import re
import pandas as pd

st.title('Multiple Google Play Store App Searcher')

app_names_input = st.text_area('Enter the names of the apps to search for, separated by commas or new lines:')

if st.button('Search for Apps'):
    app_names = re.split(r'[,\n]+', app_names_input)
    app_names = [name.strip() for name in app_names if name.strip()]
    if not app_names:
        st.error("Please enter at least one app name.")
        st.stop()

    results = []

    for app_name in app_names:
        try:
            search_results = search(
                app_name,
                lang='ko',  # Language setting
                country='kr'  # Country setting
            )
            if search_results:
                most_relevant_app = search_results[0]
                app_id = most_relevant_app['appId']
                app_details = app(app_id, lang='ko', country='kr')
                download_link = f"https://play.google.com/store/apps/details?id={app_id}"
                icon_url = app_details['icon']

                results.append([app_name, app_details['title'], app_details['developer'], app_details['score'], download_link, icon_url])
            else:
                results.append([app_name, "No app found", "", "", "", ""])
        except NotFoundError:
            results.append([app_name, "App not found", "", "", "", ""])
        except Exception as e:
            results.append([app_name, f"An error occurred: {str(e)}", "", "", "", ""])

    # Create DataFrame
    df = pd.DataFrame(results, columns=['Search Query', 'App Name', 'Developer', 'Rating', 'Download Link', 'Icon URL'])

    # Display results in table
    st.table(df)

    # Convert DataFrame to CSV
    csv = df.to_csv(index=False).encode('utf-8')

    # Download button for CSV file
    st.download_button(
        label="Download search results as CSV",
        data=csv,
        file_name='google_play_search_results.csv',
        mime='text/csv',
    )
