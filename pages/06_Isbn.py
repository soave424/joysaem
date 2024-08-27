

import streamlit as st
import requests


# 네이버 도서 API를 통해 책 검색
def search_books_by_title(title):
    client_id = "4VEUTHOdiibOqzJdOu7P"
    client_secret = "p2GQWrdWmD"
    url = "https://openapi.naver.com/v1/search/book.json"
    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret,
    }
    params = {"query": title}
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        return response.json().get('items', [])
    else:
        st.error(f"네이버 도서 API 요청 실패: {response.status_code}")
        return []

# 국립중앙도서관 API를 통해 ISBN으로 도서 정보 검색
def search_book_by_isbn(cert_key, isbn):
    url = "https://www.nl.go.kr/seoji/SearchApi.do"
    params = {
        "cert_key": cert_key,
        "result_style": "json",
        "page_no": 1,
        "page_size": 1,
        "isbn": isbn
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        result = response.json()
        if result['TOTAL_COUNT'] > 0:
            return result['docs'][0]  # 첫 번째 검색 결과만 반환
        else:
            st.error("도서 정보를 찾을 수 없습니다.")
            return None
    else:
        st.error(f"국립중앙도서관 API 오류 발생: {response.status_code}")
        return None

# Streamlit UI 구성
st.title("도서 검색 및 정보 조회")

# 인증키 입력
cert_key = st.text_input("국립중앙도서관 인증키를 입력하세요:")

# 책 제목 입력
title_input = st.text_input("책 제목을 입력하세요:")

# 도서 검색 및 결과 표시
if st.button("책 검색"):
    if cert_key and title_input:
        books = search_books_by_title(title_input)
        if books:
            selected_book = st.selectbox("책을 선택하세요:", books, format_func=lambda x: x['title'])

            if selected_book:
                isbn = selected_book.get('isbn').split(" ")[0]  # 첫 번째 ISBN만 사용
                st.write(f"선택된 책의 ISBN: {isbn}")

                # ISBN으로 도서 정보 검색
                book_info = search_book_by_isbn(cert_key, isbn)
                if book_info:
                    # 도서 정보 표시
                    st.subheader(book_info.get('TITLE', '제목 없음'))
                    
                    # 표지 이미지 표시
                    cover_image_url = book_info.get('TITLE_URL')
                    if cover_image_url:
                        st.image(cover_image_url, use_column_width=True)

                    st.write(f"저자: {book_info.get('AUTHOR', '저자 없음')}")
                    st.write(f"발행처: [{book_info.get('PUBLISHER', '발행처 없음')}]({book_info.get('PUBLISHER_URL', '')})")
                    st.write(f"ISBN: {book_info.get('EA_ISBN', 'ISBN 없음')}")
                    st.write(f"판사항: {book_info.get('EDITION_STMT', '판사항 없음')}")
                    st.write(f"예정가격: {book_info.get('PRE_PRICE', '예정가격 없음')}")
                    st.write(f"한국십진분류: {book_info.get('KDC', '한국십진분류 없음')}")
                    st.write(f"페이지: {book_info.get('PAGE', '페이지 정보 없음')}")
                    st.write(f"책크기: {book_info.get('BOOK_SIZE', '책크기 정보 없음')}")
                    st.write(f"출판예정일: {book_info.get('PUBLISH_PREDATE', '출판예정일 없음')}")
                    st.write(f"주제: {book_info.get('SUBJECT', '주제 없음')}")
                    
                    # 목차, 책소개, 책요약은 클릭 시 펼쳐지는 방식으로 처리
                    if st.button("목차 보기"):
                        st.markdown(f'<iframe src="{book_info.get("BOOK_TB_CNT_URL", "")}" width="100%" height="400px"></iframe>', unsafe_allow_html=True)
                    if st.button("책소개 보기"):
                        st.markdown(f'<iframe src="{book_info.get("BOOK_INTRODUCTION_URL", "")}" width="100%" height="400px"></iframe>', unsafe_allow_html=True)
                    if st.button("책요약 보기"):
                        st.markdown(f'<iframe src="{book_info.get("BOOK_SUMMARY_URL", "")}" width="100%" height="400px"></iframe>', unsafe_allow_html=True)

        else:
            st.error("검색 결과가 없습니다.")
    else:
        st.error("인증키와 책 제목을 입력해주세요.")
