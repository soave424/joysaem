import streamlit as st
import requests
from bs4 import BeautifulSoup

def fetch_books_and_images(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        books = []
        # 모든 책 목록을 찾기
        list_items = soup.select('.cCont_listArea .cCont_goodsSet')
        for item in list_items:
            # 책 제목 추출
            title_tag = item.select_one('.goods_info .goods_name a')
            if title_tag:
                title = title_tag.text.strip()
            else:
                title = "No Title Found"

            # 이미지 URL 추출
            img_tag = item.select_one('.goods_img img')
            if img_tag:
                img_url = img_tag['src']
            else:
                img_url = "No Image Found"

            books.append({
                'title': title,
                'image_url': img_url
            })

        return books
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return []

st.title('Fetch Book Titles and Images from Yes24')

# User inputs the URL via text input
url = st.text_input('Enter the URL of the Yes24 page:')

if st.button('Fetch Books'):
    if url:
        books = fetch_books_and_images(url)
        if books:
            st.write('Books Found:')
            for book in books:
                st.image(book['image_url'], caption=book['title'], width=100)  # Display image with title as caption
        else:
            st.error('No books found or bad URL')
    else:
        st.error('Please enter a valid URL')
