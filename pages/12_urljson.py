import streamlit as st
import requests
from bs4 import BeautifulSoup
import json

def extract_books_from_ul(ul_html):
    soup = BeautifulSoup(ul_html, 'html.parser')
    books = []

    # 모든 li 태그를 찾습니다.
    for li in soup.find_all('li'):
        book = {}
        # 책 표지 이미지 URL
        img_tag = li.find('img')
        if img_tag:
            book['image_url'] = img_tag.get('src', '')

        # 책 제목
        title_tag = li.find('strong', class_='prod-name')
        if title_tag:
            book['title'] = title_tag.get_text(strip=True)

        # 저자, 출판사, 출판년도, 청구기호 등 정보
        writer_info = li.find('span', class_='writer')
        if writer_info:
            book['details'] = writer_info.get_text(strip=True)

        # 대출 상태
        state_tag = li.find('div', class_='book-state')
        if state_tag:
            book['availability'] = state_tag.get_text(strip=True)

        books.append(book)
    
    return books

# HTML 입력
st.title("HTML에서 도서 목록 추출")
html_input = st.text_area("ul 태그가 포함된 HTML 코드를 입력하세요:")

if st.button("추출"):
    if html_input:
        books = extract_books_from_ul(html_input)
        st.json(books)
    else:
        st.error("HTML 코드를 입력하세요.")
