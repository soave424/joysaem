import streamlit as st
import pandas as pd
import requests

# 네이버 API 설정
NAVER_CLIENT_ID = '4VEUTHOdiibOqzJdOu7P'
NAVER_CLIENT_SECRET = 'p2GQWrdWmD'


def search_books(title):
    headers = {
        'X-Naver-Client-Id': NAVER_CLIENT_ID,
        'X-Naver-Client-Secret': NAVER_CLIENT_SECRET
    }
    params = {'query': title}
    response = requests.get('https://openapi.naver.com/v1/search/book.json', headers=headers, params=params)
    return response.json().get('items', [])

def create_book_list(titles):
    books_info = []
    for title in titles:
        books = search_books(title)
        if books:
            for book in books:
                books_info.append({
                    'Title': book.get('title', ''),
                    'Author': book.get('author', ''),
                    'Publisher': book.get('publisher', ''),
                    'ISBN': book.get('isbn', ''),
                    'Link': book.get('link', ''),
                })
    return pd.DataFrame(books_info)

def compare_books(new_books, current_books):
    current_isbns = set(current_books['ISBN'])
    new_books['In Current Library'] = new_books['ISBN'].apply(lambda x: 'O' if x in current_isbns else '')
    return new_books

# 스트림릿 인터페이스 설정
st.title("Book Purchase List Management")

# 1. 현재 도서 장부 업로드
st.header("Step 1: Upload Current Library Inventory")
current_books_file = st.file_uploader("Upload current library CSV", type="csv")

if current_books_file is not None:
    current_books = pd.read_csv(current_books_file)
    st.write("Current Library Inventory")
    st.dataframe(current_books)

# 2. 도서 제목 입력 및 네이버 API로 도서 목록 생성
st.header("Step 2: Enter Book Titles to Purchase")
book_titles = st.text_area("Enter book titles separated by commas")

if st.button("Generate Purchase List"):
    if book_titles:
        titles = [title.strip() for title in book_titles.split(',')]
        new_books = create_book_list(titles)
        
        if current_books_file is not None:
            new_books = compare_books(new_books, current_books)
        
        st.write("Generated Purchase List")
        st.dataframe(new_books)
        
        # CSV 파일로 다운로드
        csv = new_books.to_csv(index=False).encode('utf-8')
        st.download_button("Download CSV", csv, "purchase_list.csv", "text/csv", key='download-csv')
    else:
        st.error("Please enter book titles.")
