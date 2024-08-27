import streamlit as st
import requests
import pandas as pd
import re
from io import StringIO

# 국립중앙도서관 API 인증 키
CERT_KEY = '57cfd60d09be8111d421f49807146ec3f2806d19aa3741fbab5c95df3e61c00c'

def search_books(book_titles):
    base_url = 'https://www.nl.go.kr/seoji/SearchApi.do'
    
    books_info = []

    for title in book_titles:
        params = {
            'cert_key': CERT_KEY,
            'result_style': 'json',
            'page_no': 1,
            'page_size': 1,
            'title': title
        }
        response = requests.get(base_url, params=params)
        result = response.json()
        docs = result.get('docs')
        if docs:
            # 첫 번째 검색 결과만 사용
            item = docs[0]
            # 안전하게 데이터 추출
            result_title = item.get('TITLE', "No Title Found")
            author = item.get('AUTHOR', "No Author Found")
            publisher = item.get('PUBLISHER', "No Publisher Found")
            pubdate = item.get('PUBLISH_PREDATE', "")
            price = item.get('PRE_PRICE', "")
            isbn = item.get('EA_ISBN', "No ISBN Info")  
            

            # 출간일 처리 (연도와 월만 추출)
            formatted_date = pubdate[:4] + '년 ' + pubdate[4:6] + '월' if len(pubdate) >= 6 else pubdate

            # 비고란에 "확인 필요" 추가
            note = "확인 필요" if title.strip().lower() != result_title.strip().lower() else ""

            books_info.append({
                'title': result_title,
                'author': author,
                'publisher': publisher,
                'pub_date': formatted_date,
                'price' : price,
                'isbn': isbn,
                'note': note  # 비고란 추가
            })

    return pd.DataFrame(books_info)

# CSV 파일 생성 함수
def to_csv(df):
    output = StringIO()
    df.to_csv(output, index=False)
    processed_data = output.getvalue()
    return processed_data

st.title('National Library Book Search')
book_titles_input = st.text_area("Enter the names of the books to search for, separated by commas or new lines:")

if st.button('Search Books'):
    # 책 제목 파싱
    book_titles = re.split(r'[,\n]+', book_titles_input)
    book_titles = [title.strip() for title in book_titles if title.strip()]

    if book_titles:
        books_df = search_books(book_titles)
        if not books_df.empty:
            st.dataframe(books_df)

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
