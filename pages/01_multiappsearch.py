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
    html_rows = []  # To hold rows of HTML data including images

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

                # Create HTML row with an image
                html_row = f"""
                <tr>
                    <td><img src="{icon_url}" style="height:50px;"></td>
                    <td>{app_name}</td>
                    <td>{app_details['title']}</td>
                    <td>{app_details['developer']}</td>
                    <td>{app_details['score']}</td>
                    <td><a href="{download_link}">Link</a></td>
                </tr>
                """
                html_rows.append(html_row)
            else:
                results.append([app_name, "No app found", "", "", ""])
                html_rows.append(f"<tr><td></td><td>{app_name}</td><td>No app found</td><td></td><td></td><td></td></tr>")
        except NotFoundError:
            results.append([app_name, "App not found", "", "", ""])
            html_rows.append(f"<tr><td></td><td>{app_name}</td><td>App not found</td><td></td><td></td><td></td></tr>")
        except Exception as e:
            results.append([app_name, f"An error occurred: {str(e)}", "", "", ""])
            html_rows.append(f"<tr><td></td><td>{app_name}</td><td>Error: {str(e)}</td><td></td><td></td><td></td></tr>")

    # Display HTML Table
    html_table = f"""
    <table>
        <thead>
            <tr>
                <th>Icon</th>
                <th>Search Query</th>
                <th>App Name</th>
                <th>Developer</th>
                <th>Rating</th>
                <th>Download Link</th>
            </tr>
        </thead>
        <tbody>
            {''.join(html_rows)}
        </tbody>
    </table>
    """
    st.markdown(html_table, unsafe_allow_html=True)

    # Create DataFrame for CSV download
    df = pd.DataFrame(results, columns=['Search Query', 'App Name', 'Developer', 'Rating', 'Download Link'])
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Results as CSV", csv, "google_play_results.csv", "text/csv", key='download-csv')
