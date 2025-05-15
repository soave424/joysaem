import streamlit as st
import requests

# API URL 불러오기
API_URL = "http://apis.data.go.kr/1400119/PlantMiniService/miniatureSearch"
API_KEY = st.secrets["PlankDraw_API_Key"]


# 식물 세밀화 검색 함수
def search_plants(keyword, page=1):
    params = {
        'serviceKey': API_KEY,
        'st': 1,  # 1: 국명으로 검색, 2: 학명으로 검색
        'sw': keyword,  # 검색어
        'numOfRows': 10,  # 페이지당 결과 수
        'pageNo': page,  # 페이지 번호
    }
    response = requests.get(API_URL, params=params)
    return response.json()

# 식물 세밀화 상세 정보 조회 함수
def get_plant_details(plant_id):
    details_url = f"http://apis.data.go.kr/1400119/PlantMiniService/miniatureInfo"
    params = {
        'serviceKey': API_KEY,
        'q1': plant_id  # 세밀화 순번
    }
    response = requests.get(details_url, params=params)
    return response.json()

# Streamlit UI 설정
st.title("식물 세밀화 검색")

# 검색 입력창
keyword = st.text_input("식물 이름을 입력하세요:", "가는")

# 검색 버튼을 눌렀을 때
if keyword:
    results = search_plants(keyword)
    
    if results.get("response").get("header").get("resultCode") == "00":
        plants = results["response"]["body"]["items"]["item"]
        
        # 검색된 식물 목록 출력
        st.write(f"총 {len(plants)}개의 결과가 찾았습니다:")
        
        for plant in plants:
            plant_name = plant["plantGnrlNm"]
            scientific_name = plant["plantSpecsScnm"]
            family = plant["familyKorNm"]
            plant_id = plant["plantMinitrSeq"]
            
            # 식물별 상세 정보 보기
            with st.expander(f"{plant_name} ({scientific_name})"):
                st.write(f"과: {family}")
                st.image(plant["imgUrl"], use_column_width=True)
                
                if st.button(f"{plant_name}의 세부정보 보기"):
                    details = get_plant_details(plant_id)
                    if details.get("response").get("header").get("resultCode") == "00":
                        detail = details["response"]["body"]["items"]["item"][0]
                        st.write(f"저자: {detail['plantMinitrAthrNm']}")
                        st.write(f"제작 연도: {detail['plantMinitrMnfctYr']}")
                        st.write(f"분포 정보: {detail['distrAraDscrt']}")
                    else:
                        st.error("세부 정보를 가져오는 데 오류가 발생했습니다.")
    else:
        st.error("식물 정보를 찾을 수 없거나 API에서 오류가 발생했습니다.")
