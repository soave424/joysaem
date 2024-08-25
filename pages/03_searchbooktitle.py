import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO

def calculate_original_price(discounted_price):
    if discounted_price:
        try:
            price_numeric = int(discounted_price.replace(",", "").replace("원", "").strip())
            original_price = int(price_numeric / 0.9)  # 10% 할인된 가격에서 원래 가격을 역산
            return f"{original_price:,}원"
        except ValueError:
            return discounted_price
    return "No Price Found"

def fetch_books_from_pages(base_url, start_page, end_page):
    books = []
    if start_page == 0:
        urls_to_fetch = [base_url]
    else:
        urls_to_fetch = [f"{base_url}&PageNumber={page_number}" for page_number in range(start_page, end_page + 1)]
    
    for page_url in urls_to_fetch:
        try:
            response = requests.get(page_url)
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
            st.error(f"Failed to fetch data from URL {page_url}: {str(e)}")

    return books

def convert_to_csv(books):
    if books:
        df = pd.DataFrame(books)
        return df.to_csv(index=False)
    return None

st.title('Fetch Book Details from Yes24')

base_url = st.text_input('Enter the base URL (without page number parameter):')
start_page = st.number_input('Start Page Number', min_value=0, value=1)
end_page = st.number_input('End Page Number', min_value=0, value=1)

if st.button('Fetch Books'):
    if base_url and (start_page == 0 or start_page <= end_page):
        books = fetch_books_from_pages(base_url, start_page, end_page)
        if books:
            csv_data = convert_to_csv(books)
            st.download_button(label="Download as CSV", data=csv_data, file_name='books.csv', mime='text/csv')
        else:
            st.error('No books found or bad URL')
    else:
        st.error('Please ensure the URL is correct and the start page is less than or equal to the end page.')
