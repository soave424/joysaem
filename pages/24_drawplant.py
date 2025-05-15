import streamlit as st
import requests

# API 키를 Streamlit의 설정에서 불러오기
API_KEY = st.secrets["PlankDraw_API_Key"]

# API URL
API_URL = "http://apis.data.go.kr/1400119/PlantMiniService/miniatureSearch"

def search_plants(keyword, page=1):
    params = {
        'serviceKey': API_KEY,  # 보안에서 불러온 API 키
        'st': 1,  # 1: 국명으로 검색, 2: 학명으로 검색
        'sw': keyword,  # 검색어
        'numOfRows': 10,  # 페이지당 결과 수
        'pageNo': page,  # 페이지 번호
    }
    
    try:
        response = requests.get(API_URL, params=params)
        response.raise_for_status()  # HTTP 상태 코드가 200이 아닌 경우 예외 발생
        
        # JSON 응답 처리
        data = response.json()
        if "response" in data and data["response"]["header"]["resultCode"] == "00":
            return data
        else:
            st.error("API 응답에 문제가 있습니다.")
            return None
        
    except requests.exceptions.HTTPError as http_err:
        st.error(f"HTTP 오류 발생: {http_err}")
    except requests.exceptions.RequestException as req_err:
        st.error(f"요청 오류 발생: {req_err}")
    except ValueError as json_err:
        st.error(f"JSON 디코딩 오류 발생: {json_err}")
    except Exception as err:
        st.error(f"알 수 없는 오류 발생: {err}")
    
    return None

# 예시로 '가는'이라는 키워드로 검색
result = search_plants("가는")
if result:
    st.write(result)
