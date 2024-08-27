import requests
import streamlit as st
import pandas as pd

def search_books_by_isbn(cert_key, isbn):
    url = f"https://www.nl.go.kr/NL/search/openApi/search.do?key={cert_key}&kwd={isbn}"
    response = requests.get(url)
    
    try:
        result = response.json()
    except ValueError:
        st.error("Failed to decode JSON. The response might not be in JSON format.")
        return pd.DataFrame()  # Return an empty DataFrame if the response is not JSON

    # Now proceed with the existing checks
    if 'TOTAL_COUNT' in result and isinstance(result['TOTAL_COUNT'], int) and result['TOTAL_COUNT'] > 0:
        items = result.get('docs', [])
        books = []
        for item in items:
            books.append({
                'Title': item.get('TITLE', 'No Title Found'),
                'Author': item.get('AUTHOR', 'No Author Found'),
                'Publisher': item.get('PUBLISHER', 'No Publisher Found'),
                'Publication Date': item.get('PUBLISHER_YEAR', 'No Date Found'),
                'ISBN': item.get('ISBN', isbn)  # Default to the searched ISBN if not found
            })
        return pd.DataFrame(books)
    else:
        st.error("No books found for the given ISBN.")
        return pd.DataFrame()  # Return an empty DataFrame if no books are found

# Streamlit app layout
st.title('Search Books by ISBN')

cert_key = st.text_input("Enter your certification key:")
isbn_input = st.text_input("Enter ISBN:")

if st.button('Search'):
    if cert_key and isbn_input:
        books_df = search_books_by_isbn(cert_key, isbn_input)
        if not books_df.empty:
            st.dataframe(books_df)
        else:
            st.write("No data available.")
    else:
        st.error("Please provide both certification key and ISBN.")
