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
                lang='ko',
                country='kr'
            )
            if search_results:
                most_relevant_app = search_results[0]
                app_id = most_relevant_app['appId']
                app_details = app(app_id, lang='ko', country='kr')
                download_link = f"https://play.google.com/store/apps/details?id={app_id}"
                icon_url = app_details['icon']

                # Append data for CSV
                results.append([app_name, app_details['title'], app_details['developer'], app_details['score'], download_link])

                # Display results
                st.write(f"**App Name:** {app_details['title']}")
                st.write(icon_url)
                st.image(icon_url, width=100)  # Display app icon
                st.write("---")  # Separator
            else:
                results.append([app_name, "No app found", "", "", ""])
                st.write(f"**{app_name}:** No app found.")
                st.write("---")
        except NotFoundError:
            results.append([app_name, "App not found", "", "", ""])
            st.write(f"**{app_name}:** App not found.")
            st.write("---")
        except Exception as e:
            results.append([app_name, f"An error occurred: {str(e)}", "", "", ""])
            st.write(f"**{app_name}:** An error occurred: {str(e)}")
            st.write("---")

    # Create DataFrame for CSV download
    df = pd.DataFrame(results, columns=['Search Query', 'App Name', 'Developer', 'Rating', 'Download Link'])
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Results as CSV", csv, "google_play_results.csv", "text/csv", key='download-csv')
