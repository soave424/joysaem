import streamlit as st
import requests
import pandas as pd

# Google Books API를 사용하여 책 정보 검색 함수
def search_book_google(title):
    base_url = 'https://www.googleapis.com/books/v1/volumes?q='
    response = requests.get(base_url + title)
    result = response.json()
    
    if 'items' in result:
        book = result['items'][0]['volumeInfo']
        book_title = book.get('title', 'No Title Found')
        authors = ', '.join(book.get('authors', 'No Author Found'))
        page_count = book.get('pageCount', 'No Page Count Info')
        
        return {
            'title': book_title,
            'authors': authors,
            'page_count': page_count
        }
    else:
        return None

# Streamlit 앱 구성
st.title("책 검색 (Google Books API)")
book_title_input = st.text_input("책 제목을 입력하세요")

if st.button("책 검색"):
    if book_title_input:
        book_info = search_book_google(book_title_input)
        
        if book_info:
            st.write(f"**Title**: {book_info['title']}")
            st.write(f"**Authors**: {book_info['authors']}")
            st.write(f"**Page Count**: {book_info['page_count']}")
        else:
            st.error("책을 찾을 수 없습니다.")
    else:
        st.warning("책 제목을 입력하세요.")

# 추가로 검색된 결과를 데이터프레임 형식으로 변환하여 CSV로 저장 가능
if st.button("결과 CSV 다운로드"):
    if book_info:
        df = pd.DataFrame([book_info])
        csv = df.to_csv(index=False)
        st.download_button(
            label="CSV 파일로 다운로드",
            data=csv,
            file_name="book_info.csv",
            mime="text/csv"
        )
    else:
        st.warning("먼저 책을 검색하세요.")
