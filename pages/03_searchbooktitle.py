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

def fetch_books_from_pages(base_url, start_page, end_page):
    books = []
    if start_page == 0 and end_page == 0:  # Single page without pagination
        page_url = base_url
        response = requests.get(page_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        list_items = soup.select('.info_row.info_name')
        for item in list_items:
            title_tag = item.select_one('.gd_name')
            title = title_tag.text.strip() if title_tag else "No Title Found"

            img_tag = item.select_one('img')
            img_url = img_tag['src'] if img_tag else "No Image Found"

            author_tag = item.select_one('.info_pubGrp .info_auth a')
            author = author_tag.text.strip() if author_tag else "No Author Found"

            publisher_tag = item.select_one('.info_pubGrp .info_pub')
            publisher = publisher_tag.text.strip() if publisher_tag else "No Publisher Found"

            pub_date_tag = item.select_one('.info_pubGrp .info_date')
            pub_date = pub_date_tag.text.strip() if pub_date_tag else "No Pub Date Found"

            price_tag = item.select_one('.info_price .yes_b')
            discounted_price = price_tag.text.strip() if price_tag else "No Price Found"
            original_price = calculate_original_price(discounted_price)

            books.append({
                'Title': title,
                'Image URL': img_url,
                'Author': author,
                'Publisher': publisher,
                'Publication Date': pub_date,
                'Price': original_price
            })
    else:  # Pages with pagination
        for page_number in range(start_page, end_page + 1):
            page_url = f"{base_url}&PageNumber={page_number}"
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
                    'Title': title,
                    'Image URL': img_url,
                    'Author': author,
                    'Publisher': publisher,
                    'Publication Date': pub_date,
                    'Price': original_price
                })
    return books

st.title('Fetch Book Details from Yes24')

base_url = st.text_input('Enter the base URL:')
add_pages = st.checkbox('Add Pages?')

if add_pages:
    start_page = st.number_input('Start Page Number', min_value=1, value=1)
    end_page = st.number_input('End Page Number', min_value=1, value=1)
else:
    start_page, end_page = 0, 0

if st.button('Fetch Books'):
    if base_url:
        books = fetch_books_from_pages(base_url, start_page, end_page)
        if books:
            df = pd.DataFrame(books)
            st.dataframe(df)
            csv_data = df.to_csv(index=False)
            st.download_button("Download CSV", csv_data, "book_details.csv", "text/csv", key='download-csv')
        else:
            st.error('No books found or bad URL')
    else:
        st.error('Please enter a URL')
