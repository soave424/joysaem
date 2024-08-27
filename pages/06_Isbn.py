import streamlit as st
import requests

# 기본 인증키
DEFAULT_CERT_KEY = '57cfd60d09be8111d421f49807146ec3f2806d19aa3741fbab5c95df3e61c00c'

# KDC 분류 기준 매핑 함수
def get_kdc_category(subject):
    kdc_mapping = {
        '0': '총류',
        '1': '철학',
        '2': '종교',
        '3': '사회과학',
        '4': '자연과학',
        '5': '기술과학',
        '6': '예술',
        '7': '언어',
        '8': '문학',
        '9': '역사'
    }
    return kdc_mapping.get(subject[0], '분류 없음') if subject else '분류 없음'

# 네이버 API를 통해 책 제목으로 도서 검색
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

# ISBN을 이용해 상세 도서 정보 조회
def search_book_by_isbn(cert_key, isbn):
    url = f"https://www.nl.go.kr/seoji/SearchApi.do?cert_key={cert_key}&result_style=json&page_no=1&page_size=1&isbn={isbn}"
    
    response = requests.get(url)
    result = response.json()

    if 'TOTAL_COUNT' in result and int(result['TOTAL_COUNT']) > 0:
        item = result['docs'][0]
        
        subject = item.get('SUBJECT', '')  # KDC_CODE로 변경
        kdc_category = get_kdc_category(subject)
        
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
            'publisher_url': item.get('PUBLISHER_URL', ''),
            'call_no': item.get('CALL_NO', '청구기호 없음'),
            'kdc_code': subject,
            'kdc_category': kdc_category
        }
    else:
        return None

# Streamlit 앱 구성
st.title('도서 검색 및 정보 조회')

# 인증키 입력
cert_key = DEFAULT_CERT_KEY

# 네이버 API 클라이언트 ID와 시크릿
client_id = '4VEUTHOdiibOqzJdOu7P'
client_secret = 'p2GQWrdWmD'

# 책 제목 입력
book_title = st.text_input('검색할 책 제목을 입력하세요:', '')

# 검색 버튼 클릭 시 동작
if st.button('검색'):
    if book_title:
        book_info = search_books_by_title(book_title, client_id, client_secret)
        
        if book_info:
            st.write("### 도서 정보")
            col1, col2 = st.columns([1, 2])
            with col1:
                if book_info['image']:
                    st.image(book_info['image'], use_column_width=True)
                else:
                    st.write("이미지가 없습니다.")
            with col2:
                st.write(f"**제목:** {book_info['title']}")
                st.write(f"**ISBN:** {book_info['isbn']}")
                
                # ISBN으로 상세 도서 정보 조회
                isbn = book_info['isbn'].split(' ')[-1]  # ISBN-13이 있으면 사용
                book_metadata = search_book_by_isbn(cert_key, isbn)
                
                if book_metadata:
                    st.write(f"**저자:** {book_metadata['author']}")
                    st.write(f"**출판사:** {book_metadata['publisher']}")
                    st.write(f"**가격:** {book_metadata['pre_price']}")
                    st.write(f"**페이지 수:** {book_metadata['page'] if book_metadata['page'] else '정보 없음'}")
                    st.write(f"**출간일:** {book_metadata['publish_predate']}")
                    st.write(f"**청구기호:** {book_metadata['call_no']}")
                    st.write(f"**분야:** {book_metadata['kdc_category']}")
                    
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
            st.error("도서 정보를 가져올 수 없습니다.")
    else:
        st.error("책 제목을 입력해 주세요.")
