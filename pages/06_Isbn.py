import streamlit as st
import requests

# 네이버 API 설정
NAVER_CLIENT_ID = 'your_naver_client_id'
NAVER_CLIENT_SECRET = 'your_naver_client_secret'

# 국립중앙도서관 API 인증키
NL_CERT_KEY = '57cfd60d09be8111d421f49807146ec3f2806d19aa3741fbab5c95df3e61c00c'

# 네이버 API를 이용해 책 제목으로 ISBN 검색
def search_isbn_by_title(title):
    headers = {
        'X-Naver-Client-Id': NAVER_CLIENT_ID,
        'X-Naver-Client-Secret': NAVER_CLIENT_SECRET
    }
    response = requests.get(f'https://openapi.naver.com/v1/search/book.json?query={title}', headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        if result.get('items'):
            first_item = result['items'][0]  # 첫 번째 검색 결과
            isbn = first_item.get('isbn').split(' ')[1]  # ISBN 값 (통상적으로 두 개 중 뒤에 있는 것이 13자리)
            return isbn
    return None

# 국립중앙도서관 API를 이용해 ISBN으로 서지 정보 검색
def search_books_by_isbn(isbn):
    url = f"https://www.nl.go.kr/seoji/SearchApi.do?cert_key={NL_CERT_KEY}&result_style=json&page_no=1&page_size=1&isbn={isbn}"
    response = requests.get(url)
    
    if response.status_code == 200:
        try:
            result = response.json()
            if result['TOTAL_COUNT'] > 0:
                return result['docs'][0]  # 첫 번째 결과만 반환
        except (ValueError, KeyError):
            st.error("Error in processing the response.")
    return None

# 도서 정보 표시
def display_book_info(book):
    title = book.get('TITLE', 'Unknown Title')
    st.header(title)
    
    image_url = book.get('TITLE_URL')
    if image_url:
        st.image(image_url, caption=title, use_column_width=True)
    
    st.write(f"**저자:** {book.get('AUTHOR', 'Unknown Author')}")
    st.write(f"**ISBN:** {book.get('EA_ISBN', 'Unknown ISBN')}")
    st.write(f"**발행처:** [{book.get('PUBLISHER', 'Unknown Publisher')}]({book.get('PUBLISHER_URL', '')})")
    st.write(f"**판사항:** {book.get('EDITION_STMT', 'N/A')}")
    st.write(f"**예정가격:** {book.get('PRE_PRICE', 'N/A')}")
    st.write(f"**한국십진분류:** {book.get('KDC', 'N/A')}")
    st.write(f"**페이지:** {book.get('PAGE', 'N/A')} 페이지")
    st.write(f"**책크기:** {book.get('BOOK_SIZE', 'N/A')}")
    st.write(f"**출판예정일:** {book.get('PUBLISH_PREDATE', 'N/A')}")
    st.write(f"**주제:** {book.get('SUBJECT', 'N/A')}")
    st.write(f"**전자책 여부:** {'Yes' if book.get('EBOOK_YN', 'N') == 'Y' else 'No'}")

    if book.get('VOL'):
        st.write(f"**권차:** {book['VOL']}")
    if book.get('SERIES_TITLE'):
        st.write(f"**총서명:** {book['SERIES_TITLE']}")
    if book.get('SERIES_NO'):
        st.write(f"**총서편차:** {book['SERIES_NO']}")

    if book.get('BOOK_TB_CNT_URL'):
        with st.expander("목차 보기"):
            st.markdown(f'<iframe src="{book["BOOK_TB_CNT_URL"]}" width="700" height="500"></iframe>', unsafe_allow_html=True)
    
    if book.get('BOOK_INTRODUCTION_URL'):
        with st.expander("책 소개 보기"):
            st.markdown(f'<iframe src="{book["BOOK_INTRODUCTION_URL"]}" width="700" height="500"></iframe>', unsafe_allow_html=True)
    
    if book.get('BOOK_SUMMARY_URL'):
        with st.expander("책 요약 보기"):
            st.markdown(f'<iframe src="{book["BOOK_SUMMARY_URL"]}" width="700" height="500"></iframe>', unsafe_allow_html=True)

# Streamlit 인터페이스
st.title('도서 검색 및 서지정보 조회')

book_title = st.text_input('도서 제목을 입력하세요:')

if st.button('검색'):
    if book_title:
        isbn = search_isbn_by_title(book_title)
        
        if isbn:
            st.write(f"**ISBN:** {isbn}")
            book_info = search_books_by_isbn(isbn)
            
            if book_info:
                display_book_info(book_info)
            else:
                st.error("국립중앙도서관에서 도서 정보를 찾을 수 없습니다.")
        else:
            st.error("도서의 ISBN을 찾을 수 없습니다.")
    else:
        st.error("도서 제목을 입력하세요.")
