import streamlit as st
from google_play_scraper import app, search
from google_play_scraper.exceptions import NotFoundError
import re
import pandas as pd
import base64
from io import BytesIO

st.title('Multiple Google Play Store App Searcher')

app_names_input = st.text_area('Enter the names of the apps to search for, separated by commas or new lines:')

if st.button('Search for Apps'):
    app_names = re.split(r'[,\n]+', app_names_input)
    app_names = [name.strip() for name in app_names if name.strip()]
    if not app_names:
        st.error("Please enter at least one app name.")
        st.stop()

    results = []
    html_images = []

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

                # Create an HTML image element with the icon
                html_img = f"<img src='{icon_url}' style='height: 100px;'>"
                html_images.append(html_img)

                results.append([app_name, app_details['title'], app_details['developer'], app_details['score'], download_link])
            else:
                results.append([app_name, "No app found", "", "", ""])
                html_images.append("")
        except NotFoundError:
            results.append([app_name, "App not found", "", "", ""])
            html_images.append("")
        except Exception as e:
            results.append([app_name, f"An error occurred: {str(e)}", "", "", ""])
            html_images.append("")

    # Create DataFrame
    df = pd.DataFrame(results, columns=['Search Query', 'App Name', 'Developer', 'Rating', 'Download Link'])
    df['Icon'] = html_images  # Add HTML image tags to DataFrame

    # Convert DataFrame to HTML
    html_data = df.to_html(escape=False)  # 'escape=False' to render HTML tags

    # Encode HTML to base64
    b64_html = base64.b64encode(html_data.encode()).decode()

    # Create download button for HTML file
    st.markdown(
        f'<a href="data:text/html;base64,{b64_html}" download="app_details.html">Download HTML file with images</a>',
        unsafe_allow_html=True
    )
