import streamlit as st
import requests
from bs4 import BeautifulSoup
import json

def extract_books_from_ul(ul_element):
    books = []

    # 모든 li 태그를 찾습니다.
    for li in ul_element.find_all('li'):
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

def fetch_html_from_url(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text

st.title("URL에서 도서 목록 추출")
url_input = st.text_input("URL을 입력하세요:")

if st.button("추출"):
    if url_input:
        try:
            html_content = fetch_html_from_url(url_input)
            soup = BeautifulSoup(html_content, 'html.parser')

            # 특정 ul 태그를 선택
            ul_tag = soup.select_one('ul.book-list')  # 'ul.book-list' 선택자에 따라 태그 선택
            if ul_tag:
                books = extract_books_from_ul(ul_tag)
                st.json(books)
            else:
                st.error("지정된 ul 태그를 찾을 수 없습니다.")
        except requests.exceptions.RequestException as e:
            st.error(f"URL을 가져오는 데 문제가 발생했습니다: {e}")
    else:
        st.error("URL을 입력하세요.")
