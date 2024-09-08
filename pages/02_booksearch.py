
import streamlit as st
import requests

def search_books(query):
    client_id = "4VEUTHOdiibOqzJdOu7P"
    client_secret = "p2GQWrdWmD"
    headers = {
        'X-Naver-Client-Id': client_id,
        'X-Naver-Client-Secret': client_secret
    }
    url = f"https://openapi.naver.com/v1/search/book.json?query={query}"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 오류가 있을 경우 예외 발생
        return response.json()  # 정상적으로 데이터 반환
    except requests.exceptions.HTTPError as err:
        return {"error": str(err)}  # HTTP 오류 발생 시 오류 메시지 반환

st.title('네이버 도서 검색')

query = st.text_input('검색할 책의 제목을 입력하세요.')

if st.button('검색'):
    if query:
        results = search_books(query)
        if 'error' in results:
            st.error(results['error'])  # 오류 메시지 출력
        elif 'items' in results:
            for item in results['items']:
                st.write(f"**제목:** {item['title']}")
                st.write(f"**저자:** {item['author']}")
                st.write(f"**출판사:** {item['publisher']}")
                st.write(f"**출판일:** {item['pubdate']}")
                st.write(f"**정가:** {item['price']}원")
                st.write(f"**판매가:** {item['discount']}원")
                st.write(f"**설명:** {item['description']}") 
                st.write(f"**링크:** [링크]({item['link']})")
                st.image(item['image'], width=100)
                st.write("---")  # 구분선
        else:
            st.error('검색 결과가 없습니다.')
    else:
        st.error('검색어를 입력해주세요.')
