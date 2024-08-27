import streamlit as st
import requests
import json

# Set up the API key and base URL for National Library of Korea
API_KEY = '57cfd60d09be8111d421f49807146ec3f2806d19aa3741fbab5c95df3e61c00c'  
BASE_URL = 'https://www.nl.go.kr/NL/search/openApi/search.do'

# Naver API credentials

NAVER_CLIENT_ID = '4VEUTHOdiibOqzJdOu7P' 
NAVER_CLIENT_SECRET = 'p2GQWrdWmD'  

st.title("Book Search and Details Display")

# Input for book title
book_title = st.text_input("Enter the book title to search:")

# Search button
if st.button("Search"):
    if book_title:
        # National Library API request parameters
        params = {
            'key': API_KEY,
            'kwd': book_title,
            'pageNum': 1,
            'pageSize': 1,  # Limiting to the first result for simplicity
            'apiType': 'json'
        }

        # Make the API request to National Library
        response = requests.get(BASE_URL, params=params)

        # Check if the request was successful
        if response.status_code == 200:
            try:
                # Load the response as JSON
                json_data = response.json()
                if 'result' in json_data and json_data['result']:
                    book_data = json_data['result'][0]  # First item in the result

                    # Extracting the required fields
                    title = book_data.get('titleInfo', 'N/A')
                    author = book_data.get('authorInfo', 'N/A')
                    publisher = book_data.get('pubInfo', 'N/A')
                    pub_year = book_data.get('pubYearInfo', 'N/A')
                    isbn = book_data.get('isbn', 'N/A')
                    call_no = book_data.get('callNo', 'N/A')
                    kdc_code = book_data.get('kdcCode1s', 'N/A')
                    kdc_name = book_data.get('kdcName1s', 'N/A')
                    class_no = book_data.get('classNo', 'N/A')

                    # Fetch book image from Naver API using the title
                    naver_headers = {
                        'X-Naver-Client-Id': NAVER_CLIENT_ID,
                        'X-Naver-Client-Secret': NAVER_CLIENT_SECRET
                    }
                    naver_params = {'query': title}
                    naver_response = requests.get('https://openapi.naver.com/v1/search/book.json', headers=naver_headers, params=naver_params)
                    naver_data = naver_response.json()

                    if naver_data.get('items'):
                        image_url = naver_data['items'][0].get('image', None)
                    else:
                        image_url = None

                    # Displaying the book image and details
                    col1, col2 = st.columns([1, 2])

                    with col1:
                        if image_url:
                            st.image(image_url, use_column_width=True)
                        else:
                            st.write("No image available")

                    with col2:
                        st.write(f"**Title:** {title}")
                        st.write(f"**Author:** {author}")
                        st.write(f"**Publisher:** {publisher}")
                        st.write(f"**Publication Year:** {pub_year}")
                        st.write(f"**ISBN:** {isbn}")
                        st.write(f"**Call Number:** {call_no}")
                        st.write(f"**KDC Code:** {kdc_code} ({kdc_name})")
                        st.write(f"**Class Number:** {class_no}")

                else:
                    st.error("No book information found.")

            except json.JSONDecodeError:
                st.error("Error: The response is not a valid JSON.")
        else:
            st.error(f"Error: Failed to retrieve data. Status code: {response.status_code}")
    else:
        st.error("Please enter a book title to search.")
