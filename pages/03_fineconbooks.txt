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
            title_tag = item.find('a', class_='gd_name')
            if not title_tag:
                continue  # 제목 태그가 없으면 다음 아이템으로 넘어갑니다.
            title = title_tag.text.strip()
            author_tag = item.find('span', class_='authPub info_auth')
            author = author_tag.text.strip() if author_tag else "Author not available"
            publisher_tag = item.find('span', class_='authPub info_pub')
            publisher = publisher_tag.text.strip() if publisher_tag else "Publisher not available"
            pub_date_tag = item.find('span', class_='authPub info_date')
            pub_date = pub_date_tag.text.strip() if pub_date_tag else "Date not available"
            price_tag = item.find('span', class_='priceB')
            price = price_tag.text.strip() if price_tag else "Price not available"
            link = title_tag['href'] if title_tag else "#"
            image_tag = item.find('img', class_='goods_img')
            image_url = image_tag['src'] if image_tag else "No image available"

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
