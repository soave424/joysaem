# app.py
import streamlit as st
import requests
import json

# 네이버 검색 API를 위한 클라이언트 ID와 시크릿
CLIENT_ID = '4VEUTHOdiibOqzJdOu7P'
CLIENT_SECRET = 'p2GQWrdWmD'

def fetch_search_results(query):
    url = 'https://openapi.naver.com/v1/search/webkr.json'
    headers = {
        'X-Naver-Client-Id': CLIENT_ID,
        'X-Naver-Client-Secret': CLIENT_SECRET
    }
    params = {
        'query': query,
        'display': 10  # 결과 개수
    }
    response = requests.get(url, headers=headers, params=params)
    return response.json()

def main():
    st.title('네이버 검색 결과를 JSON으로 저장하기')
    
    query = st.text_input('검색어를 입력하세요:')
    
    if st.button('검색'):
        if query:
            results = fetch_search_results(query)
            st.json(results)  # JSON 결과를 화면에 표시
            
            # JSON 파일로 저장하기
            with open('search_results.json', 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=4)
            
            st.success('검색 결과가 search_results.json 파일로 저장되었습니다.')
        else:
            st.warning('검색어를 입력해주세요.')

if __name__ == '__main__':
    main()
