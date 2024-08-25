import streamlit as st
import requests
from bs4 import BeautifulSoup
import csv
import os
from io import StringIO

# CSV 파일을 메모리에 저장하여 Streamlit에서 다운로드할 수 있게 하는 함수
def convert_df_to_csv(data):
    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)
    return buffer.getvalue()

# 책 정보를 스크래핑하는 함수
def fetch_books_from_url(base_url, start_page, end_page):
    books = []
    for page in range(start_page, end_page + 1):
        url = f"{base_url}?FetchSize=40&PageNumber={page}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        for item in soup.find_all('div', class_='goods_info'):
            title = item.find('a', class_='gd_name').text.strip()
            author = item.find('span', class_='authPub info_auth').text.strip()
            publisher = item.find('span', class_='authPub info_pub').text.strip()
            pub_date = item.find('span', class_='authPub info_date').text.strip()
            price = item.find('span', class_='priceB').text.strip()
            link = item.find('a', class_='gd_name')['href']
            image_url = item.find('img', class_='goods_img')['src']

            books.append({
                'Title': title,
                'Author': author,
                'Publisher': publisher,
                'PubDate': pub_date,
                'Price': price,
                'Link': 'https://www.yes24.com' + link,
                'ImageURL': image_url
            })

    return books

st.title('Yes24 Book Scraper')

if st.button('Fetch and Download Book List'):
    urls = [
        ('https://www.yes24.com/24/Category/Display/001001016015013001', 1, 10),
        ('https://www.yes24.com/24/Category/Display/001001016016013001', 1, 18),
        ('https://www.yes24.com/24/Category/Display/001001016017013001', 1, 16)
    ]

    all_books = []
    for base_url, start_page, end_page in urls:
        books = fetch_books_from_url(base_url, start_page, end_page)
        all_books.extend(books)

    csv_data = convert_df_to_csv(all_books)
    st.download_button(label='Download CSV', data=csv_data, file_name='yes24_books.csv', mime='text/csv')
