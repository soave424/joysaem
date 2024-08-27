import streamlit as st
import requests
import json

# 국립중앙도서관 API 키 설정
CERT_KEY = '57cfd60d09be8111d421f49807146ec3f2806d19aa3741fbab5c95df3e61c00c'

# 도서 검색 함수
def search_books(keyword):
    url = "https://www.nl.go.kr/NL/search/openApi/search.do"
    params = {
        'key': CERT_KEY,
        'kwd': keyword,
        'pageNum': 1,
        'pageSize': 10,
        'apiType': 'json'
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get('result', [])
    else:
        return []

# 도서 상세 정보 함수
def get_book_details(isbn):
    url = "https://www.nl.go.kr/seoji/SearchApi.do"
    params = {
        'cert_key': CERT_KEY,
        'result_style': 'json',
        'page_no': 1,
        'page_size': 10,
        'isbn': isbn
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get('docs', [])
    else:
        return []

# Streamlit UI 설정
st.title("국립중앙도서관 도서 검색")

# 도서 검색 입력창
keyword = st.text_input("검색어를 입력하세요:")

if keyword:
    books = search_books(keyword)
    
    if books:
        st.write("검색 결과:")
        book_titles = [book['title_info'] for book in books]
        selected_book = st.selectbox("도서를 선택하세요:", book_titles)
        
        if selected_book:
            selected_isbn = next(book['isbn'] for book in books if book['title_info'] == selected_book)
            book_details = get_book_details(selected_isbn)
            
            if book_details:
                book = book_details[0]  # 첫 번째 결과 선택
                
                st.image(book.get('TITLE_URL'), use_column_width=True)
                st.header(book.get('TITLE'))
                st.subheader(f"저자: {book.get('AUTHOR')}")
                st.write(f"ISBN: {book.get('EA_ISBN')}")
                st.write(f"발행처: [{book.get('PUBLISHER')}]({book.get('PUBLISHER_URL')})")
                st.write(f"출판예정일: {book.get('PUBLISH_PREDATE')}")
                st.write(f"판사항: {book.get('EDITION_STMT')}")
                st.write(f"예정가격: {book.get('PRE_PRICE')}")
                st.write(f"페이지: {book.get('PAGE')}")
                st.write(f"책크기: {book.get('BOOK_SIZE')}")
                st.write(f"주제: {book.get('SUBJECT')}")
                st.write(f"전자책 여부: {book.get('EBOOK_YN')}")

                with st.expander("목차 보기"):
                    st.write(f"[목차 보기]({book.get('BOOK_TB_CNT_URL')})")
                
                with st.expander("책 소개 보기"):
                    st.write(f"[책 소개 보기]({book.get('BOOK_INTRODUCTION_URL')})")
                
                with st.expander("책 요약 보기"):
                    st.write(f"[책 요약 보기]({book.get('BOOK_SUMMARY_URL')})")
            else:
                st.error("도서 정보를 가져올 수 없습니다.")
    else:
        st.error("검색 결과가 없습니다.")
