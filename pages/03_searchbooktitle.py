import streamlit as st
import requests
from bs4 import BeautifulSoup

def fetch_book_details(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        books = []
        list_items = soup.select('.cCont_listArea .cCont_goodsSet')
        for item in list_items:
            title_tag = item.select_one('.goods_info .goods_name a')
            title = title_tag.text.strip() if title_tag else "No Title Found"

            img_tag = item.select_one('.goods_img img')
            img_url = img_tag['src'] if img_tag else "No Image Found"

            author_tag = item.select_one('.goods_info .goods_auth a')
            author = author_tag.text.strip() if author_tag else "No Author Found"

            publisher_tag = item.select_one('.goods_info .goods_pub')
            publisher = publisher_tag.text.strip() if publisher_tag else "No Publisher Found"

            pub_date_tag = item.select_one('.goods_info .goods_date')
            pub_date = pub_date_tag.text.strip() if pub_date_tag else "No Pub Date Found"

            price_tag = item.select_one('.goods_price .yes_b')
            price = price_tag.text.strip() if price_tag else "No Price Found"

            books.append({
                'title': title,
                'image_url': img_url,
                'author': author,
                'publisher': publisher,
                'pub_date': pub_date,
                'price': price
            })

        return books
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return []

st.title('Fetch Book Details from Yes24')

# User inputs the URL via text input
url = st.text_input('Enter the URL of the Yes24 page:')

if st.button('Fetch Books'):
    if url:
        books = fetch_book_details(url)
        if books:
            st.write('Books Found:')
            for book in books:
                st.write(book)
        else:
            st.error('No books found or bad URL')
    else:
        st.error('Please enter a valid URL')
