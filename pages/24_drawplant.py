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
        # 1) 목록 검색
        resp = requests.get(
            f"{BASE_URL}/miniatureSearch",
            params={"serviceKey": api_key, "st": "1", "sw": plant_name, "numOfRows": "10", "pageNo": "1"}
        )
        root = ET.fromstring(resp.text)

        # 2) detailYn == "Y"인 항목 찾기
        items = root.findall(".//item")
        valid = next((it for it in items if it.findtext("detailYn")=="Y"), None)
        if not valid:
            st.info("세밀화 이미지가 존재하지 않습니다.")
        else:
            # 3) 상세 정보 조회
            seq = valid.findtext("plantMinitrSeq")
            resp2 = requests.get(
                f"{BASE_URL}/miniatureInfo",
                params={"serviceKey": api_key, "q1": seq}
            )
            root2 = ET.fromstring(resp2.text)
            img_url = root2.findtext(".//imgUrl")  # ex: http://www.nature.go.kr/fileUpload/miniature/89_2004_8283.jpg

            if not img_url:
                st.info("이미지 URL이 없습니다.")
            else:
                st.write("이미지 원본 URL:", img_url)

                # 4) HTTP URL 그대로 백엔드에서 다운로드
                img_resp = requests.get(img_url)
                if img_resp.status_code == 200:
                    # st.image에 바이너리(이미지 bytes) 넘기기
                    st.image(img_resp.content, caption=f"{plant_name} 세밀화")
                else:
                    st.error(f"이미지 다운로드 실패: HTTP {img_resp.status_code}")
