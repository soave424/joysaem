import streamlit as st
import requests
import pandas as pd
import re
from io import StringIO
import os

# 네이버 API 접속 정보
CLIENT_ID = '4VEUTHOdiibOqzJdOu7P'
CLIENT_SECRET = 'p2GQWrdWmD'

# 기본 파일 경로 설정
default_file_path = '/Users/joeunlee/Desktop/coding/joysaem/joysaem-1/csv/남양주양지초등학교 도서관 전체장서(2024.8.30) - sheet 1.csv'

# 도서관 장서 파일 로드
if os.path.exists(default_file_path):
    current_books = pd.read_csv(default_file_path)
    st.write(f"Using default file: {default_file_path}")
else:
    current_books = None
    st.warning("기본 도서관 장서 파일을 찾을 수 없습니다.")

if current_books is not None:
    # 도서명에서 부제목과 특정 문자를 제거하는 함수
    def clean_title(title):
        if title is None or not isinstance(title, str):
            return ""
        # 부제목 제거 및 "?", "!" 등의 문자 제거
        return re.sub(r'[?!]', '', re.sub(r'\(.*?\)', '', title)).strip()

    def search_books(book_titles):
        headers = {
            'X-Naver-Client-Id': CLIENT_ID,
            'X-Naver-Client-Secret': CLIENT_SECRET
        }
        base_url = 'https://openapi.naver.com/v1/search/book.json?query='

        books_info = []

        for title in book_titles:
            cleaned_title = clean_title(title)  # 부제목 및 특정 문자 제거
            response = requests.get(base_url + cleaned_title, headers=headers)
            result = response.json()
            items = result.get('items')

            if items:
                # 첫 번째 검색 결과만 사용
                item = items[0]
                result_title = item.get('title', "No Title Found")
            else:
                # 검색 결과가 없으면 입력된 제목을 사용
                result_title = title
            
            author = item.get('author', "No Author Found") if items else "검색 결과 없음"
            publisher = item.get('publisher', "No Publisher Found") if items else "검색 결과 없음"
            pubdate = item.get('pubdate', "") if items else ""
            price = item.get('discount', "0") if items else "0"
            isbn = item.get('isbn', "No ISBN Info") if items else "No ISBN Info"
            image = item.get('image', "") if items else ""  # 이미지 URL 추가

            # 출간일 처리 (연도와 월만 추출)
            formatted_date = pubdate[:4] + '년 ' + pubdate[4:6] + '월' if len(pubdate) >= 6 else pubdate

            # 정가 계산 (판매가의 100%)
            try:
                price_numeric = int(price)
                original_price = int(price_numeric / 0.9)
                price_text = f"{original_price:,}원"
            except ValueError:
                price_text = "Price Error"

            # 장서와 비교하여 일치 여부 확인
            match = ""
            call_number = ""
            matched_title = ""

            for _, row in current_books.iterrows():
                if clean_title(result_title) == clean_title(row['서명(자료명)']):
                    match = "일치"
                    call_number = row['청구기호']
                    matched_title = row['서명(자료명)']
                    break

            if not match:
                # 네이버 검색 결과가 없거나 일치하는 도서가 없을 경우, 입력된 제목으로 장서 검색
                for _, row in current_books.iterrows():
                    if clean_title(title) == clean_title(row['서명(자료명)']):
                        match = "일치"
                        call_number = row['청구기호']
                        matched_title = row['서명(자료명)']
                        break

            books_info.append({
                '도서명': result_title,
                '저자': author,
                '출판사': publisher,
                '발행': formatted_date,
                '가격': price_text,
                '표지': image,
                '일치여부': match,
                '청구기호': call_number,
                '도서관 서명(자료명)': matched_title
            })

        return pd.DataFrame(books_info)

    # 이미지 표시 함수
    def format_images(df):
        return [f'<img src="{url}" width="50">' if url else '' for url in df['표지']]

    # CSV 파일 생성 함수 (이미지 열 제거)
    def to_csv(df):
        df = df.drop(columns=['표지'])  # 이미지 열 제거
        output = StringIO()
        df.to_csv(output, index=False)
        processed_data = output.getvalue()
        return processed_data

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
else:
    st.warning("기본 도서관 장서 파일을 찾을 수 없습니다.")
