import streamlit as st
import requests
import pandas as pd
import re
from math import ceil
from io import BytesIO

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
        items = result.get('items')
        if items:
            # 첫 번째 검색 결과만 사용
            item = items[0]
            # 안전하게 데이터 추출
            result_title = item.get('title', "No Title Found")
            author = item.get('author', "No Author Found")
            publisher = item.get('publisher', "No Publisher Found")
            pubdate = item.get('pubdate', "")
            price = item.get('discount', "0")
            isbn = item.get('isbn', "No ISBN Info")  

            # 출간일 처리 (연도와 월만 추출)
            formatted_date = pubdate[:4] + '년 ' + pubdate[4:6] + '월' if len(pubdate) >= 6 else pubdate

            # 정가 계산 (판매가의 100%)
            try:
                price_numeric = int(price)
                original_price = ceil(price_numeric / 0.9 / 10) * 10
                price_text = f"{original_price:,}원"
            except ValueError:
                price_text = "Price Error"

            # 비고란에 "확인 필요" 추가
            note = "확인 필요" if title.strip().lower() != result_title.strip().lower() else ""

            books_info.append({
                'title': result_title,
                'author': author,
                'publisher': publisher,
                'pub_date': formatted_date,
                'price': price_text,
                'isbn': isbn,
                'note': note  # 비고란 추가
            })

    return pd.DataFrame(books_info)

# 엑셀 파일 생성 함수
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    processed_data = output.getvalue()
    return processed_data

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

            # 엑셀 다운로드 버튼 추가
            st.download_button(
                label="Download List",
                data=to_excel(books_df),
                file_name='book_list.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        else:
            st.error("No books found for the given titles.")
    else:
        st.error("Please enter at least one book name.")
