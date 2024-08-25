
import streamlit as st
import requests
import pandas as pd
import re

# 네이버 API 접속 정보
CLIENT_ID = '4VEUTHOdiibOqzJdOu7P'
CLIENT_SECRET = 'p2GQWrdWmD'

def search_books(book_titles):
    headers = {
        'X-Naver-Client-Id': CLIENT_ID,
        'X-Naver-Client-Secret': CLIENT_SECRET
    }
    base_url = 'https://openapi.naver.com/v1/search/book.json?query='

    books_info = []

    for title in book_titles:
        response = requests.get(base_url + title, headers=headers)
        result = response.json()
        if result.get('items'):
            for item in result['items']:
                # 안전하게 데이터 추출
                title = item.get('title', "No Title Found")
                author = item.get('author', "No Author Found")
                publisher = item.get('publisher', "No Publisher Found")
                pubdate = item.get('pubdate', "")
                price = item.get('price', "0")

                # 출간일 처리 (연도와 월만 추출)
                formatted_date = pubdate[:4] + '년 ' + pubdate[4:6] + '월' if len(pubdate) >= 6 else pubdate

                # 정가 계산 (판매가의 100%)
                try:
                    price_numeric = int(price)
                    original_price = int(price_numeric / 0.9)
                    price_text = f"{original_price:,}원"
                except ValueError:
                    price_text = "Price Error"

                books_info.append({
                    'title': title,
                    'author': author,
                    'publisher': publisher,
                    'pub_date': formatted_date,
                    'price': price_text
                })

    return pd.DataFrame(books_info)

st.title('Naver Book Search')
book_titles_input = st.text_area("Enter the names of the books to search for, separated by commas or new lines:")
if st.button('Search Books'):
    # 책 제목 파싱
    book_titles = re.split(r'[,\n]+', book_titles_input)
    book_titles = [title.strip() for title in book_titles if title.strip()]

    if book_titles:
        books_df = search_books(book_titles)
        if not books_df.empty:
            st.dataframe(books_df)
        else:
            st.error("No books found for the given titles.")
    else:
        st.error("Please enter at least one book name.")
