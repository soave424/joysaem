import streamlit as st
import requests
import pandas as pd

def search_books_by_isbn(cert_key, isbn):
    base_url = 'https://www.nl.go.kr/seoji/SearchApi.do'
    params = {
        'cert_key': cert_key,
        'result_style': 'json',
        'isbn': isbn,
        'page_no': 1,
        'page_size': 10
    }

    response = requests.get(base_url, params=params)
    result = response.json()
    books_info = []
    
    if result['TOTAL_COUNT'] > 0:
        for item in result['docs']:
            books_info.append({
                'Title': item.get('TITLE', "No Title Found"),
                'Author': item.get('AUTHOR', "No Author Found"),
                'Publisher': item.get('PUBLISHER', "No Publisher Found"),
                'PubDate': item.get('PUBLISH_PREDATE', "No PubDate Found"),
                'Page': item.get('PAGE', "No Page Info"),
                'ISBN': item.get('EA_ISBN', "No ISBN Found")
            })

    return pd.DataFrame(books_info)

st.title('ISBN Book Search via National Library of Korea')
cert_key = st.text_input("Enter your certification key:")
isbn_input = st.text_input("Enter the ISBN of the book:")

if st.button('Search by ISBN'):
    if cert_key and isbn_input:
        books_df = search_books_by_isbn(cert_key, isbn_input)
        if not books_df.empty:
            st.dataframe(books_df)
        else:
            st.error("No book found for the given ISBN.")
    else:
        st.error("Please enter both a certification key and an ISBN.")
