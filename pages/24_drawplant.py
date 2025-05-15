import streamlit as st
import requests
import xml.etree.ElementTree as ET

# 1) secrets.toml에 설정한 PlankDrawD_API_Key 를 사용
api_key = st.secrets["PlankDrawD_API_Key"]

BASE_URL = "http://apis.data.go.kr/1400119/PlantMiniService"

st.title("🌿 식물 세밀화 조회")

plant_name = st.text_input("식물 국명 입력", "")

if st.button("검색"):
    if not plant_name:
        st.warning("먼저 식물 이름을 입력해주세요.")
    else:
        # 2) 목록 검색
        params_search = {
            "serviceKey": api_key,
            "st": "1",
            "sw": plant_name,
            "numOfRows": "10",
            "pageNo": "1"
        }
        resp = requests.get(f"{BASE_URL}/miniatureSearch", params=params_search)
        root = ET.fromstring(resp.text)

        # 3) detailYn == "Y"인 항목 찾기
        items = root.findall(".//item")
        valid = next((it for it in items if it.findtext("detailYn")=="Y"), None)
        if not valid:
            st.info("세밀화 이미지가 존재하지 않습니다.")
        else:
            seq = valid.findtext("plantMinitrSeq")

            # 4) 상세 정보 조회
            params_info = {"serviceKey": api_key, "q1": seq}
            resp2 = requests.get(f"{BASE_URL}/miniatureInfo", params=params_info)
            root2 = ET.fromstring(resp2.text)
            img_url = root2.findtext(".//imgUrl")

            if not img_url:
                st.info("이미지 URL이 없습니다.")
            else:
                # 5) HTTPS로 변환 후, 브라우저 직접 로드
                https_url = img_url.replace("http://", "https://")
                st.write("이미지 URL:", img_url)  # URL 확인용
                st.image(img_url, caption=f"{plant_name} 세밀화")
