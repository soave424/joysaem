import streamlit as st
import requests
import json
import urllib.parse

# 기본 URL (searchKeyword 부분 제외)
base_url = "https://read365.edunet.net/PureScreen/SchoolSearchResult?searchKeyword={}&searchType=&provCode=J10&neisCode=J100001618&schoolName=%EB%82%A8%EC%96%91%EC%A3%BC%EC%96%91%EC%A7%80%EC%B4%88%EB%93%B1%ED%95%99%EA%B5%90"

st.title("Web Scraping to JSON")

# 사용자가 입력할 searchKeyword 부분
search_keyword = st.text_input("Enter the search keyword:")

if st.button('Search'):
    if search_keyword:
        # 입력받은 키워드를 URL 인코딩
        encoded_keyword = urllib.parse.quote(search_keyword)
        
        # 완성된 URL
        url = base_url.format(encoded_keyword)
        
        # URL로부터 데이터 요청
        response = requests.get(url)

        if response.status_code == 200:
            try:
                # JSON 파싱
                data = response.json()
                
                # 결과가 있는지 확인
                if data:
                    st.write("Data retrieved successfully!")
                    st.json(data)  # JSON 데이터를 스트림릿 앱에 출력
                else:
                    st.write("No data found in the response.")
            
            except json.JSONDecodeError:
                st.error("Failed to parse JSON. The content might not be in JSON format.")
        else:
            st.error(f"Failed to retrieve data. HTTP Status Code: {response.status_code}")
    else:
        st.error("Please enter a search keyword.")
