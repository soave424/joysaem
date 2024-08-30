import streamlit as st
import requests
import pandas as pd
import re
from io import StringIO
from difflib import SequenceMatcher


def preprocess_title(title):
    # 괄호 안의 부제목 등을 제거
    title = re.sub(r'\(.*?\)', '', title)
    # 필요하면 다른 전처리 추가
    return title.strip()

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def find_in_library(title):
    for _, row in current_books.iterrows():
        processed_row_title = preprocess_title(row['서명(자료명)'])
        processed_input_title = preprocess_title(title)
        if similar(processed_input_title, processed_row_title) > 0.3:  # 임계값을 낮추거나 조정
            return f"O ({row['청구기호']})"
    return ""









# 네이버 API 접속 정보
CLIENT_ID = '4VEUTHOdiibOqzJdOu7P'
CLIENT_SECRET = 'p2GQWrdWmD'

# 문자열 유사도 비교 함수
def similar(a, b):
    if a is None or b is None:
        return 0
    return SequenceMatcher(None, a, b).ratio()

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
            item = items[0]
            result_title = item.get('title', "No Title Found")
            author = item.get('author', "No Author Found")
            publisher = item.get('publisher', "No Publisher Found")
            pubdate = item.get('pubdate', "")
            price = item.get('discount', "0")
            isbn = item.get('isbn', "No ISBN Info")
            image = item.get('image', "")

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
                '도서명': result_title,
                '저자': author,
                '출판사': publisher,
                '발행': formatted_date,
                '가격': price_text,
                'ISBN': isbn,
                '표지': image,
                '비고': note
            })
        else:
            books_info.append({
                '도서명': title,
                '저자': "검색 결과 없음",
                '출판사': "검색 결과 없음",
                '발행': "검색 결과 없음",
                '가격': "검색 결과 없음",
                'ISBN': "검색 결과 없음",
                '표지': "",
                '비고': "검색 결과 없음"
            })

    return pd.DataFrame(books_info)

# CSV 파일 생성 함수 (이미지 열 제거)
def to_csv(df):
    df = df.drop(columns=['표지'])
    output = StringIO()
    df.to_csv(output, index=False)
    processed_data = output.getvalue()
    return processed_data

# 이미지 표시 함수
def format_images(df):
    return [f'<img src="{url}" width="50">' if url else '' for url in df['표지']]

# 도서 장부와 비교
def compare_books(new_books, current_books):
    current_books['청구기호'] = current_books['청구기호'].fillna('')
    
    def find_in_library(title):
        for _, row in current_books.iterrows():
            # 비어있는 값이 없도록 체크
            library_title = row['서명(자료명)']
            if pd.notna(library_title) and similar(title, library_title) > 0.7:  # 유사도 0.7 이상일 때 동일한 책으로 간주
                return f"O ({row['청구기호']})"
        return ''
    
    new_books['장서에 있음'] = new_books['도서명'].apply(find_in_library)

    return new_books

st.title('도서 장부와 새로운 도서 목록 비교')

# 현재 도서 장부 업로드
st.header("현재 도서 장부 업로드")
current_books_file = st.file_uploader("현재 도서 장부 CSV 파일을 업로드하세요.", type="csv")

if current_books_file is not None:
    current_books = pd.read_csv(current_books_file)
    st.write("현재 도서 장부:")
    st.dataframe(current_books)

# 새로운 도서 목록 생성
st.header("새로운 도서 목록 생성")
book_titles_input = st.text_area("줄바꿈 혹은 ','로 구분된 책 목록을 아래 입력창에 넣어주세요. 검색하기 버튼을 눌러 책 목록을 확인한 후 csv파일로 다운 받으실 수 있습니다. 책 제목이 완벽하게 일치하지 않는 경우 비고란에 확인필요가 뜹니다.")

if st.button('책 검색'):
    book_titles = re.split(r'[,\n]+', book_titles_input)
    book_titles = [title.strip() for title in book_titles if title.strip()]

    if book_titles:
        new_books = search_books(book_titles)
        
        if not new_books.empty:
            if current_books_file is not None:
                new_books = compare_books(new_books, current_books)

            new_books['표지'] = format_images(new_books)
            st.write(
                new_books.to_html(escape=False, index=False),
                unsafe_allow_html=True
            )

            st.download_button(
                label="목록다운받기",
                data=to_csv(new_books),
                file_name='new_book_list.csv',
                mime='text/csv'
            )
        else:
            st.error("No books found for the given titles.")
    else:
        st.error("Please enter at least one book name.")
