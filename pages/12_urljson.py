import streamlit as st
import requests
from bs4 import BeautifulSoup
import json

def extract_li_items_from_ul(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 특정 ul 태그를 선택 - ul 태그에 class가 있는 경우 이를 사용해 선택합니다.
    ul_tag = soup.select_one('ul.book-list.list-type.list')
    
    if not ul_tag:
        return {"error": "ul 태그를 찾을 수 없습니다."}
    
    # 모든 li 요소를 추출합니다.
    li_items = []
    for li in ul_tag.find_all('li'):
        item = {}
        
        # 예시로 이미지, 제목, 저자 등을 추출
        img_tag = li.find('img')
        if img_tag:
            item['image_url'] = img_tag.get('src', '')
        
        title_tag = li.find('strong', class_='prod-name')
        if title_tag:
            item['title'] = title_tag.get_text(strip=True)
        
        author_tag = li.find('span', class_='writer')
        if author_tag:
            item['author'] = author_tag.get_text(strip=True)
        
        li_items.append(item)
    
    return li_items

# URL로부터 HTML 가져오기
def fetch_html_from_url(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text

st.title('URL에서 ul 태그 안의 li 요소 추출')

# URL 입력창
url = st.text_input('URL을 입력하세요:')

if url:
    try:
        # HTML 콘텐츠 가져오기
        html_content = fetch_html_from_url(url)
        
        # li 요소 추출
        li_items = extract_li_items_from_ul(html_content)
        
        # JSON 출력
        st.json(li_items)
    except Exception as e:
        st.error(f"오류 발생: {e}")
