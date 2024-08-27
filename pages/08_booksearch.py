import streamlit as st
import requests
import json

# Set up the API key and base URL for National Library of Korea
API_KEY = '57cfd60d09be8111d421f49807146ec3f2806d19aa3741fbab5c95df3e61c00c'
BASE_URL = 'https://www.nl.go.kr/NL/search/openApi/search.do'

# Naver API credentials
NAVER_CLIENT_ID = '4VEUTHOdiibOqzJdOu7P'
NAVER_CLIENT_SECRET = 'p2GQWrdWmD'

st.title("도서 검색 및 정보 조회")

# Input for book title
book_title = st.text_input("검색할 책 제목을 입력하세요:")

def search_books_from_naver(title, client_id, client_secret):
    headers = {
        'X-Naver-Client-Id': client_id,
        'X-Naver-Client-Secret': client_secret
    }
    base_url = 'https://openapi.naver.com/v1/search/book.json'
    params = {'query': title, 'display': 1}
    
    response = requests.get(base_url, headers=headers, params=params)
    result = response.json()
    
    if result.get('items'):
        item = result['items'][0]  # 첫 번째 결과만 사용
        return {
            'title': item.get('title', ''),
            'author': item.get('author', ''),
            'publisher': item.get('publisher', ''),
            'isbn': item.get('isbn', ''),
            'image': item.get('image', '')
        }
    else:
        return None

# Search button
if st.button("검색"):
    if book_title:
        # National Library API request parameters
        params = {
            'key': API_KEY,
            'kwd': book_title,
            'pageNum': 1,
            'pageSize': 1,
            'apiType': 'json'
        }

        # Make the API request to National Library
        response = requests.get(BASE_URL, params=params)

        # Check if the request was successful
        if response.status_code == 200:
            try:
                # Load the response as JSON
                json_data = response.json()

                # Check if result key exists and is not empty
                if 'result' in json_data and json_data['result']:
                    book_data = json_data['result'][0]  # First item in the result

                    # Extracting the required fields
                    title = book_data.get('titleInfo', 'N/A')
                    authors = book_data.get('authorInfo', 'N/A')
                    publisher = book_data.get('pubInfo', 'N/A')
                    pub_year = book_data.get('pubYearInfo', 'N/A')
                    isbn = book_data.get('isbn', 'N/A')
                    call_no = book_data.get('callNo', 'N/A')
                    kdc_code = book_data.get('kdcCode1s', 'N/A')
                    kdc_name = book_data.get('kdcName1s', 'N/A')
                    class_no = book_data.get('classNo', 'N/A')
                    ebook_yn = book_data.get('EBOOK_YN', ''),
                    page = book_data.get('PAGE', ''),



                    # Clean the title to remove HTML tags
                    clean_title = title.replace('<span class="searching_txt">', '').replace('</span>', '')

                    # Fetch book image and page count from Naver API using the cleaned title
                    naver_book_info = search_books_from_naver(clean_title, NAVER_CLIENT_ID, NAVER_CLIENT_SECRET)


                    if naver_book_info:
                        image_url = naver_book_info['image']
                        # Try to extract page count from Naver API (if available)
                        # naver_page_count = naver_book_info['page_count']
                    else:
                        image_url = None
                        naver_page_count = 'N/A'

                    # Displaying the book image and details
                    col1, col2 = st.columns([1, 2])

                    with col1:
                        if image_url:
                            st.image(image_url, use_column_width=True)
                        else:
                            st.write("이미지가 없습니다.")

                    with col2:
                        st.write(f"**제목:** {clean_title}")
                        st.write(f"**저자:** {authors}")
                        st.write(f"**출판사:** {publisher}")
                        st.write(f"**출판년도:** {pub_year}")
                        st.write(f"**ISBN:** {isbn}")
                        st.write(f"**청구기호:** {call_no}")
                        st.write(f"**KDC 코드:** {kdc_code} ({kdc_name})")
                        st.write(f"**페이지 수:** {naver_page_count}")

                else:
                    st.error("도서 정보를 찾을 수 없습니다.")

            except json.JSONDecodeError:
                st.error("오류: 응답이 유효한 JSON이 아닙니다.")
        else:
            st.error(f"오류: 데이터 검색에 실패했습니다. 상태 코드: {response.status_code}")
    else:
        st.error("책 제목을 입력해 주세요.")
