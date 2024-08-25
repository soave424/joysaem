import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

def calculate_original_price(discounted_price):
    if discounted_price:
        try:
            price_numeric = int(discounted_price.replace(",", "").replace("원", "").strip())
            original_price = int(price_numeric / 0.9)  # 10% 할인된 가격에서 원래 가격을 역산
            return f"{original_price:,}원"
        except ValueError:
            return discounted_price
    return "No Price Found"

def fetch_books_from_url(url):
    books = []
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
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
            discounted_price = price_tag.text.strip() if price_tag else "No Price Found"
            original_price = calculate_original_price(discounted_price)

            books.append({
                'title': title,
                'image_url': img_url,
                'author': author,
                'publisher': publisher,
                'pub_date': pub_date,
                'price': original_price
            })
    except Exception as e:
        st.error(f"Failed to fetch data: {str(e)}")
        return None
    return books

st.title('Fetch Book Details from Yes24')

base_url = st.text_input('Enter the URL:')

use_page_range = st.checkbox('Add Page Range')
if use_page_range:
    start_page = st.number_input('Start Page Number', min_value=1, value=1)
    end_page = st.number_input('End Page Number', min_value=1, value=1)

if st.button('Fetch Books'):
    if use_page_range and start_page <= end_page:
        books = []
        for page in range(start_page, end_page + 1):
            page_url = f"{base_url}&PageNumber={page}"
            page_books = fetch_books_from_url(page_url)
            if page_books:
                books.extend(page_books)
        if books:
            df = pd.DataFrame(books)
            st.table(df)
        else:
            st.error('No books found or bad URL')
    else:
        books = fetch_books_from_url(base_url)
        if books:
            df = pd.DataFrame(books)
            st.table(df)
        else:
            st.error('No books found or bad URL')
