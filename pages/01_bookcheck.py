

import streamlit as st
import pandas as pd
import re
import asyncio
import aiohttp
from io import StringIO
import os

# 네이버 API 접속 정보
CLIENT_ID = '4VEUTHOdiibOqzJdOu7P'
CLIENT_SECRET = 'p2GQWrdWmD'

# 도서관 장서 파일 업로드
uploaded_file = st.file_uploader("현재 도서관 장서 CSV 파일을 업로드하세요.", type="csv")

# 이미지 파일 경로 설정
image_path = 'image/설명.png'

# 이미지 파일이 존재하는지 확인
if os.path.exists(image_path):
    if not uploaded_file:
        st.image(image_path, caption='설명 이미지')
else:
    st.error(f"이미지 파일을 찾을 수 없습니다: {image_path}")

# 도서명에서 부제목 제거 함수
def clean_title(title):
    if title is None or not isinstance(title, str):
        return ""
    return re.sub(r'\(.*?\)', '', title).strip()

# 비동기 HTTP 요청 함수
async def fetch_book(session, url, headers):
    try:
        async with session.get(url, headers=headers, timeout=1) as response:
            return await response.json()
    except asyncio.TimeoutError:
        return None  # 타임아웃 발생 시 None 반환

# 비동기 책 검색 함수
async def search_books(book_titles, current_books):
    headers = {
        'X-Naver-Client-Id': CLIENT_ID,
        'X-Naver-Client-Secret': CLIENT_SECRET
    }
    base_url = 'https://openapi.naver.com/v1/search/book.json?query='
    books_info = []

    async with aiohttp.ClientSession() as session:
        tasks = []
        for title in book_titles:
            cleaned_title = clean_title(title)
            task = asyncio.ensure_future(fetch_book(session, base_url + cleaned_title, headers))
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        for response, title in zip(responses, book_titles):
            if response is None or not response.get('items'):  # 타임아웃 또는 검색 결과 없음 처리
                # 네이버 검색 결과가 없거나 검색 불가인 경우 CSV 파일에서 도서명 확인
                match = ""
                call_number = ""
                matched_title = ""
                for _, row in current_books.iterrows():
                    if clean_title(title) == clean_title(row['서명(자료명)']):
                        match = "일치"
                        call_number = row['청구기호']
                        matched_title = row['서명(자료명)']
                        break
                if match:
                    books_info.append({
                        '도서명': title,
                        '저자': "로컬 데이터 일치",
                        '출판사': "로컬 데이터 일치",
                        '발행': "",
                        '가격': "",
                        '일치': match,
                        '청구기호': call_number,
                        '도서관 서명(자료명)': matched_title,
                        '표지': ''
                    })
                else:
                    books_info.append({
                        '도서명': title,
                        '저자': '검색 결과 없음',
                        '출판사': '검색 결과 없음',
                        '발행': '',
                        '가격': '',
                        '일치': '',
                        '청구기호': '',
                        '도서관 서명(자료명)': '',
                        '표지': ''
                    })
            else:
                item = response['items'][0]
                result_title = item.get('title', title)
                author = item.get('author', "저자 정보 없음")
                publisher = item.get('publisher', "출판사 정보 없음")
                pubdate = item.get('pubdate', "")
                price = item.get('discount', "0")
                image = item.get('image', "")  # 이미지 URL

                formatted_date = pubdate[:4] + '년 ' + pubdate[4:6] + '월' if len(pubdate) >= 6 else pubdate
               
                # 정가 계산 (할인된 판매가에서 10% 할인 금액을 역산)
                try:
                    price_numeric = int(price)
                    # 원래 정가는 할인된 가격을 1/0.9로 계산하고, 소수점 두 번째 자리에서 반올림
                    original_price = round(price_numeric / 0.9)
                    price_text = f"{original_price:,}원"
                except ValueError:
                    price_text = "Price Error"


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
                    '일치': match,
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

# 검색 및 결과 처리
if uploaded_file:
    current_books = pd.read_csv(uploaded_file)

    st.title('여러 권의 책을 한 번에 검색하기')
    book_titles_input = st.text_area("줄바꿈 혹은 ','로 구분된 책 목록을 입력해주세요.")

    if st.button('책 검색'):
        # 책 제목 파싱
        book_titles = re.split(r'[,\n]+', book_titles_input)
        book_titles = [title.strip() for title in book_titles if title.strip()]

        if book_titles:
            with st.spinner(f'검색 중... 총 {len(book_titles)}권을 검색합니다.'):
                books_df = asyncio.run(search_books(book_titles, current_books))
                if not books_df.empty:
                    books_df['표지'] = format_images(books_df)
                    st.write(
                        books_df.to_html(escape=False, index=False),
                        unsafe_allow_html=True
                    )

                    st.download_button(
                        label="목록 다운로드",
                        data=to_csv(books_df),
                        file_name='book_list.csv',
                        mime='text/csv'
                    )
                else:
                    st.error("검색 결과가 없습니다.")
        else:
            st.error("최소한 하나의 책 제목을 입력해주세요.")
else:
    st.warning("도서관 장서 파일을 업로드하세요.")
