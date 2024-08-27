import streamlit as st
import requests
import pandas as pd

# 기본 인증키
DEFAULT_CERT_KEY = '57cfd60d09be8111d421f49807146ec3f2806d19aa3741fbab5c95df3e61c00c'


def kdc_description(class_no):
    descriptions = {
        '0': '총류', '1': '철학', '2': '종교', '3': '사회과학',
        '4': '자연과학', '5': '기술과학', '6': '예술', '7': '언어',
        '8': '문학', '9': '역사'
    }
    
    if class_no and class_no[0] in descriptions:
        return f"{class_no} ({descriptions[class_no[0]]})"
    else:
        return class_no

def search_books_by_title(title, client_id, client_secret):
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

def search_book_by_isbn(cert_key, isbn):
    url = f"https://www.nl.go.kr/seoji/SearchApi.do?cert_key={cert_key}&result_style=json&page_no=1&page_size=1&isbn={isbn}"
    
    response = requests.get(url)
    result = response.json()

    
    if 'TOTAL_COUNT' in result and int(result['TOTAL_COUNT']) > 0:
        item = result['docs'][0]
        return {
            'title': item.get('TITLE', ''),
            'vol': item.get('VOL', ''),
            'series_title': item.get('SERIES_TITLE', ''),
            'class_no': item.get('CLASS_NO', ''),
            'author': item.get('AUTHOR', ''),
            'isbn': item.get('EA_ISBN', ''),
            'publisher': item.get('PUBLISHER', ''),
            'edition_stmt': item.get('EDITION_STMT', ''),
            'pre_price': item.get('PRE_PRICE', ''),
            'page': item.get('PAGE', ''),
            'book_size': item.get('BOOK_SIZE', ''),
            'publish_predate': item.get('PUBLISH_PREDATE', ''),
            'subject': item.get('SUBJECT', ''),
            'ebook_yn': item.get('EBOOK_YN', ''),
            'title_url': item.get('TITLE_URL', ''),
            'book_tb_cnt_url': item.get('BOOK_TB_CNT_URL', ''),
            'book_introduction_url': item.get('BOOK_INTRODUCTION_URL', ''),
            'book_summary_url': item.get('BOOK_SUMMARY_URL', ''),
            'publisher_url': item.get('PUBLISHER_URL', '')
        }
    else:
        return None

st.title('도서 검색 및 정보 조회')

# 인증키 입력
cert_key = st.text_input('인증키를 입력하세요 (입력하지 않으면 기본 키가 사용됩니다):', value=DEFAULT_CERT_KEY)

# 네이버 API 클라이언트 ID와 시크릿
client_id = '4VEUTHOdiibOqzJdOu7P'
client_secret = 'p2GQWrdWmD'

# 책 제목 입력
book_title = st.text_input('검색할 책 제목을 입력하세요:', '')

# 검색 버튼을 입력창 옆에 배치
if st.button('검색'):
    if book_title:
        book_info = search_books_by_title(book_title, client_id, client_secret)
        
        if book_info:
            st.write("### 도서 정보")
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(book_info['image'], use_column_width=True)
            with col2:
                st.write(f"**제목:** {book_info['title']}")
                st.write(f"**저자:** {book_info['author']}")
            if 'publisher_url' in book_info:
                st.write(f"**출판사:** [{book_info['publisher']}]({book_info['publisher_url']})")
            else:
                st.write(f"**출판사:** {book_info['publisher']}")
                
                isbn = book_info['isbn'].split(' ')[-1]  # ISBN-13이 있으면 사용
                book_metadata = search_book_by_isbn(cert_key, isbn)
                
                if book_metadata:
                    
                    st.write(f"**예정가격:** {book_metadata['pre_price']}")
                    # st.write(f"**한국십진분류:** {kdc_description(book_metadata['kdc'])}")
                    st.write(f"**페이지:** {book_metadata['page']}")
                    st.write(f"**책크기:** {book_metadata['book_size']}")
                    st.write(f"**출판예정일:** {book_metadata['publish_predate']}")
                    st.write(f"**분류:** {book_metadata['class_no']}")
                    st.write(f"**전자책 여부:** {book_metadata['ebook_yn']}")
                    
                    if book_metadata['book_tb_cnt_url']:
                        if st.button("목차 펼쳐보기"):
                            st.markdown(f'<iframe src="{book_metadata["book_tb_cnt_url"]}" width="100%" height="400px"></iframe>', unsafe_allow_html=True)
                    if book_metadata['book_introduction_url']:
                        if st.button("책 소개 펼쳐보기"):
                            st.markdown(f'<iframe src="{book_metadata["book_introduction_url"]}" width="100%" height="400px"></iframe>', unsafe_allow_html=True)
                    if book_metadata['book_summary_url']:
                        if st.button("책 요약 펼쳐보기"):
                            st.markdown(f'<iframe src="{book_metadata["book_summary_url"]}" width="100%" height="400px"></iframe>', unsafe_allow_html=True)
                    

                else:
                    st.error("도서 정보를 가져올 수 없습니다.")
        else:
            st.error("네이버에서 도서 정보를 가져올 수 없습니다.")
