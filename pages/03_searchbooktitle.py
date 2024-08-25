import streamlit as st
import requests
from bs4 import BeautifulSoup

def fetch_images_and_titles(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            books = []
            # Find all <img> tags and extract 'src' for image and 'alt' for title
            for img in soup.find_all('img', alt=True):  # Ensure 'alt' attribute is present
                if 'goods' in img['src']:  # Filter to include only relevant images
                    books.append({
                        'title': img['alt'],
                        'image_src': img['src']
                    })
            return books
        else:
            return []
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return []

st.title('Yes24 Book Image and Title Fetcher')

# User inputs the URL via text input
url = st.text_input('Enter the URL of the Yes24 page:')

if st.button('Fetch Books'):
    if url:
        books = fetch_images_and_titles(url)
        if books:
            st.write('Books Found:')
            for book in books:
                st.image(book['image_src'], caption=book['title'], width=100)  # Display image with title as caption
        else:
            st.error('No books found or bad URL')
    else:
        st.error('Please enter a valid URL')
