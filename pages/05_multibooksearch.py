import streamlit as st
import requests
import pandas as pd
import re
from io import StringIO

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
            image = item.get('image', "")  # 이미지 URL 추가

            # 출간일 처리 (연도와 월만 추출)
            formatted_date = pubdate[:4] + '년 ' + pubdate[4:6] + '월' if len(pubdate) >= 6 else pubdate

            # 정가 계산 (판매가의 100%)
            try:
                price_numeric = int(price)
                original_price = int(price_numeric / 0.9)
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
                'image': image,  # 이미지 열 추가
                'note': note  # 비고란 추가
            })

    return pd.DataFrame(books_info)

# CSV 파일 생성 함수 (이미지 열 제거)
def to_csv(df):
    df = df.drop(columns=['image'])  # 이미지 열 제거
    output = StringIO()
    df.to_csv(output, index=False)
    processed_data = output.getvalue()
    return processed_data

# 이미지 표시 함수
def format_images(df):
    return [f'<img src="{url}" width="50">' if url else '' for url in df['image']]

st.title('Naver Book Search')
book_titles_input = st.text_area("Enter the names of the books to search for, separated by commas or new lines:")

if st.button('Search Books'):
    # 책 제목 파싱
    book_titles = re.split(r'[,\n]+', book_titles_input)
    book_titles = [title.strip() for title in book_titles if title.strip()]

    if book_titles:
        books_df = search_books(book_titles)
        if not books_df.empty:
            # 이미지 열을 HTML 형식으로 변환하여 표시
            books_df['image'] = format_images(books_df)
            st.write(
                books_df.to_html(escape=False, index=False), 
                unsafe_allow_html=True
            )

            # CSV 다운로드 버튼 추가
            st.download_button(
                label="Download List",
                data=to_csv(books_df),
                file_name='book_list.csv',
                mime='text/csv'
            )
        else:
            st.error("No books found for the given titles.")
    else:
        st.error("Please enter at least one book name.")
