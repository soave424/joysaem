import streamlit as st
import requests
from bs4 import BeautifulSoup

def fetch_book_titles(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            titles = []
            # Look for the specific container and tag that hold the book titles
            for item in soup.find_all('td', class_='goodsTxtInfo'):
                title = item.find('a', class_='N=a:bta.title')
                if title:
                    titles.append(title.text.strip())
            return titles
        else:
            return ["Failed to retrieve data: HTTP Status " + str(response.status_code)]
    except Exception as e:
        return [str(e)]

st.title('Yes24 Book Titles Fetcher')

# User inputs the URL via text input
url = st.text_input('Enter the URL of the Yes24 page:')

if st.button('Fetch Titles'):
    if url:
        titles = fetch_book_titles(url)
        if titles:
            st.write('Book Titles Found:')
            for title in titles:
                st.text(title)
        else:
            st.error('No titles found or bad URL')
    else:
        st.error('Please enter a valid URL')
