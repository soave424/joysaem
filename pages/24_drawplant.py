import streamlit as st
import requests
import xml.etree.ElementTree as ET

api_key = st.secrets["PlankDrawD_API_Key"]

BASE_URL = "http://apis.data.go.kr/1400119/PlantMiniService"

st.title("🌿 식물 세밀화 조회")

plant_name = st.text_input("식물 국명 입력", "")

if st.button("검색"):
    if not plant_name:
        st.warning("먼저 식물 이름을 입력해주세요.")
    else:
        # 2) 목록 검색 호출
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
            # 3) detailYn=="Y"인 첫 번째 항목 찾기 :contentReference[oaicite:2]{index=2}:contentReference[oaicite:3]{index=3}
            items = root.findall(".//item")
            valid = next((it for it in items if it.findtext("detailYn")=="Y"), None)
            if not valid:
                st.info("세밀화 이미지가 존재하지 않습니다.")
            else:
                seq = valid.findtext("plantMinitrSeq")
                # 4) 상세 정보 조회
                params_info = {
                    "serviceKey": api_key,
                    "q1": seq         # q1 = 세밀화순번 :contentReference[oaicite:4]{index=4}:contentReference[oaicite:5]{index=5}
                }
                resp2 = requests.get(f"{BASE_URL}/miniatureInfo", params=params_info)
                if resp2.status_code != 200:
                    st.error(f"상세 API 오류: HTTP {resp2.status_code}")
                else:
                    root2 = ET.fromstring(resp2.text)
                    img_url = root2.findtext(".//imgUrl")  # 이미지url :contentReference[oaicite:6]{index=6}:contentReference[oaicite:7]{index=7}
                    if not img_url:
                        st.info("이미지 URL이 없습니다.")
                    else:
                        # 5) HTTP→HTTPS 변환 및 바이너리 로드
                        https_url = img_url.replace("http://", "https://")
                        img_resp = requests.get(https_url)
                        if img_resp.status_code == 200:
                            st.image(img_resp.content, caption=f"{plant_name} 세밀화")
                        else:
                            st.error(f"이미지 로드 실패 (HTTP {img_resp.status_code})")
