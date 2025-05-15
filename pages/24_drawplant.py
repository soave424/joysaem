import streamlit as st
import requests
import xml.etree.ElementTree as ET

# 1) Secrets에 api_key를 등록하세요 (key 이름은 "api_key" 가정)
api_key = st.secrets["PlankDrawD_API_Key"]

BASE_URL = "http://apis.data.go.kr/1400119/PlantMiniService"

st.title("🌿 식물 세밀화 조회")

# 2) 사용자 입력
plant_name = st.text_input("식물 국명 입력", "")

if st.button("검색"):
    if not plant_name:
        st.warning("먼저 식물 이름을 입력해주세요.")
    else:
        # 3) 목록 검색 호출
        params_search = {
            "serviceKey": api_key,
            "st": "1",          # 1=국명 포함 검색 :contentReference[oaicite:0]{index=0}:contentReference[oaicite:1]{index=1}
            "sw": plant_name,   
            "numOfRows": "10",
            "pageNo": "1"
        }
        resp = requests.get(f"{BASE_URL}/miniatureSearch", params=params_search)
        if resp.status_code != 200:
            st.error(f"검색 API 오류: HTTP {resp.status_code}")
        else:
            root = ET.fromstring(resp.text)
            code = root.findtext(".//resultCode")
            msg  = root.findtext(".//resultMsg")
            if code != "00":
                st.error(f"검색 실패: {msg}")
            else:
                items = root.findall(".//item")
                if not items:
                    st.info("검색 결과가 없습니다.")
                else:
                    # 4) 첫 번째 항목의 세밀화순번 가져오기
                    seq = items[0].findtext("plantMinitrSeq")
                    # 5) 상세정보 조회 호출
                    params_info = {
                        "serviceKey": api_key,
                        "q1": seq        # q1 = 세밀화순번 :contentReference[oaicite:2]{index=2}:contentReference[oaicite:3]{index=3}
                    }
                    resp2 = requests.get(f"{BASE_URL}/miniatureInfo", params=params_info)
                    if resp2.status_code != 200:
                        st.error(f"상세 API 오류: HTTP {resp2.status_code}")
                    else:
                        root2 = ET.fromstring(resp2.text)
                        code2 = root2.findtext(".//resultCode")
                        msg2  = root2.findtext(".//resultMsg")
                        if code2 != "00":
                            st.error(f"상세 조회 실패: {msg2}")
                        else:
                            img_url = root2.findtext(".//imgUrl")
                            st.image(img_url, caption=f"{plant_name} 세밀화")  # 이미지 표시
