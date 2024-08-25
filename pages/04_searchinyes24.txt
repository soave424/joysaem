import streamlit as st
import requests
from bs4 import BeautifulSoup
import csv

def fetch_books_from_url(base_url, start_page, end_page):
    books = []
    for page in range(start_page, end_page + 1):
        url = f"{base_url}?FetchSize=40&PageNumber={page}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        for item in soup.find_all('div', class_='goods_info'):
            title_tag = item.find('a', class_='gd_name')
            if not title_tag:
                continue
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

def save_to_csv(data, filename):
    keys = data[0].keys()
    with open(filename, 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)

# Streamlit UI
st.title('Yes24 Book Scraper')

# User input
base_url = st.text_input('Enter the base URL', 'https://www.yes24.com/24/Category/Display/001001016015013001')
start_page = st.number_input('Start page number', min_value=1, value=1)
end_page = st.number_input('End page number', min_value=1, value=10)

if st.button('Fetch Books'):
    books = fetch_books_from_url(base_url, start_page, end_page)
    if books:
        st.write('Books fetched successfully!')
        for book in books:
            st.write(book)
    else:
        st.write('No books found.')

if st.button('Download CSV'):
    if books:
        save_to_csv(books, 'yes24_books.csv')
        st.success('File downloaded successfully!')
