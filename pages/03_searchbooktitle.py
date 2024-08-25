import streamlit as st
import requests
from bs4 import BeautifulSoup

def calculate_original_price(discounted_price):
    if discounted_price:
        try:
            # 가격에서 쉼표 제거 후 정수로 변환
            price_numeric = int(discounted_price.replace(",", "").replace("원", "").strip())
            # 10% 할인된 가격에서 원래 가격을 계산
            original_price = int(price_numeric / 0.9)  # 10% 할인을 역산
            return f"{original_price:,}원"
        except ValueError:
            return discounted_price  # 변환에 실패할 경우, 원래 문자열 반환
    return "No Price Found"

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
