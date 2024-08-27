import streamlit as st
import requests
import json

# Set up the API key and base URL
API_KEY = '57cfd60d09be8111d421f49807146ec3f2806d19aa3741fbab5c95df3e61c00c'  
BASE_URL = 'https://www.nl.go.kr/NL/search/openApi/search.do'

st.title("National Library Book Search")

# Input for book title
book_title = st.text_input("Enter the book title to search:")

# Search button
if st.button("Search"):
    if book_title:
        # API request parameters
        params = {
            'key': API_KEY,
            'kwd': book_title,
            'pageNum': 1,
            'pageSize': 10,
            'apiType': 'json'
        }

        # Make the API request
        response = requests.get(BASE_URL, params=params)

        # Check if the request was successful
        if response.status_code == 200:
            try:
                # Load the response as JSON
                json_data = response.json()

                # Display the JSON data
                st.write("### JSON Response:")
                st.json(json_data)

            except json.JSONDecodeError:
                st.error("Error: The response is not a valid JSON.")
        else:
            st.error(f"Error: Failed to retrieve data. Status code: {response.status_code}")
    else:
        st.error("Please enter a book title to search.")
