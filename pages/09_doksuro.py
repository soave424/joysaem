import streamlit as st
import requests
from bs4 import BeautifulSoup

# 기본 URL (searchKeyword 부분 제외)
base_url = "https://read365.edunet.net/PureScreen/SchoolSearchResult?searchKeyword={}&searchType=&provCode=J10&neisCode=J100001618&schoolName=%EB%82%A8%EC%96%91%EC%A3%BC%EC%96%91%EC%A7%80%EC%B4%88%EB%93%B1%ED%95%99%EA%B5%90"

st.title("도서 목록 추출")

# 사용자가 입력할 searchKeyword 부분
search_keyword = st.text_input("검색할 키워드를 입력하세요:")

if st.button('Search'):
    if search_keyword:
        # 입력받은 키워드를 URL 인코딩
        encoded_keyword = requests.utils.quote(search_keyword)
        
        # 완성된 URL
        url = base_url.format(encoded_keyword)
        
        # URL로부터 데이터 요청
        response = requests.get(url)

        if response.status_code == 200:
            # HTML 파싱
            soup = BeautifulSoup(response.content, 'html.parser')

            # 도서 리스트 요소 추출
            book_list_container = soup.find('div', {'class': 'book-list list-type list'})  # 'ul'이 포함된 부모 요소 찾기
            if book_list_container:
                book_items = book_list_container.find_all('li')  # ul 요소 아래의 모든 li 요소를 선택

                if book_items:
                    st.write("도서 목록:")
                    for item in book_items:
                        # 제목
                        title = item.find('strong', class_='prod-name').get_text(strip=True)

                        # 저자, 출판사, 출판년도, 소장학교, 청구기호 등 정보
                        info = item.find('span', class_='writer').get_text(strip=True)

                        # 도서 상태 (대출 가능/대출 중)
                        state = item.find('div', class_='book-state').get_text(strip=True)

                        # 이미지 URL
                        img_src = item.find('img')['src']

                        # Streamlit을 통한 출력
                        st.write(f"**제목**: {title}")
                        st.write(f"**정보**: {info}")
                        st.write(f"**상태**: {state}")
                        st.image(img_src)
                        st.write("---")
                else:
                    st.write("도서 목록을 찾을 수 없습니다.")
            else:
                st.write("도서 목록 컨테이너를 찾을 수 없습니다.")
        else:
            st.error(f"데이터를 가져오지 못했습니다. HTTP 상태 코드: {response.status_code}")
    else:
        st.error("검색어를 입력해 주세요.")
