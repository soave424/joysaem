import streamlit as st
import requests
from bs4 import BeautifulSoup

# 기본 URL (searchKeyword 부분 제외)
base_url = "https://read365.edunet.net/PureScreen/SchoolSearchResult?searchKeyword={}&searchType=&provCode=J10&neisCode=J100001618&schoolName=%EB%82%A8%EC%96%91%EC%A3%BC%EC%96%91%EC%A7%80%EC%B4%88%EB%93%B1%ED%95%99%EA%B5%90"

st.title("도서 제목 추출")

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

            # 도서 제목 추출
            book_titles = soup.find_all('strong', class_='prod-name')
            
            if book_titles:
                st.write("도서 제목 목록:")
                for title in book_titles:
                    st.write(title.get_text())
            else:
                st.write("No book titles found in the HTML response.")
        else:
            st.error(f"Failed to retrieve data. HTTP Status Code: {response.status_code}")
    else:
        st.error("Please enter a search keyword.")
