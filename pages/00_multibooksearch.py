import streamlit as st
import requests
import pandas as pd
import re
from io import StringIO
from decimal import Decimal, ROUND_HALF_UP
import math

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


            # 정가 계산 (할인된 판매가에서 10% 할인 금액을 역산, 100원 단위로 올림)
            try:
                price_numeric = Decimal(price)  # Decimal로 변환
                # 원래 정가는 할인된 가격을 1/0.9로 계산
                original_price = price_numeric / Decimal('0.9')
                
                # 100원 단위로 올림 (Decimal 사용)
                original_price = (original_price.quantize(Decimal('1'), rounding=ROUND_HALF_UP) + Decimal('99')).quantize(Decimal('100'), rounding=ROUND_HALF_UP)

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
                '표지': image,
                '비고': note
            })
        else:
            # 검색 결과가 없을 경우
            books_info.append({
                '도서명': title,
                '저자': "검색 결과 없음",
                '출판사': "검색 결과 없음",
                '발행': "검색 결과 없음",
                '가격': "검색 결과 없음",
                '표지': "",
                '비고': "검색 결과 없음"
            })

    return pd.DataFrame(books_info)

# CSV 파일 생성 함수 (이미지 열 제거)
def to_csv(df):
    df = df.drop(columns=['표지'])  # 이미지 열 제거
    output = StringIO()
    df.to_csv(output, index=False)
    processed_data = output.getvalue()
    return processed_data

# 이미지 표시 함수
def format_images(df):
    return [f'<img src="{url}" width="50">' if url else '' for url in df['표지']]  # 'image' 대신 '표지' 사용

st.title('여러 권의 책을 한 번에 검색하기')
book_titles_input = st.text_area("줄바꿈 혹은 ','로 구분된 책 목록을 아래 입력창에 넣어주세요. 검색하기 버튼을 눌러 책 목록을 확인한 후 csv파일로 다운 받으실 수 있습니다. 책 제목이 완벽하게 일치하지 않는 경우 비고란에 확인필요가 뜹니다.")

if st.button('책 검색'):
    # 책 제목 파싱
    book_titles = re.split(r'[,\n]+', book_titles_input)
    book_titles = [title.strip() for title in book_titles if title.strip()]

    if book_titles:
        books_df = search_books(book_titles)
        if not books_df.empty:
            # 이미지 열을 HTML 형식으로 변환하여 표시
            books_df['표지'] = format_images(books_df)
            st.write(
                books_df.to_html(escape=False, index=False), 
                unsafe_allow_html=True
            )

            # CSV 다운로드 버튼 추가
            st.download_button(
                label="목록다운받기",
                data=to_csv(books_df),
                file_name='book_list.csv',
                mime='text/csv'
            )
        else:
            st.error("No books found for the given titles.")
    else:
        st.error("Please enter at least one book name.")
