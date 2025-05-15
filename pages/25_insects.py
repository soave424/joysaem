import streamlit as st
import requests
import xml.etree.ElementTree as ET

# secrets.toml에 PlankDrawD_API_Key로 등록된 디코딩된 키 사용
api_key = st.secrets["Bugs_API_Key"]

BASE_URL = "http://openapi.nature.go.kr/openapi/service/rest/InsectService"

st.title("🐞 곤충 도감 검색")

# 1) 검색어 입력
insect_name = st.text_input("곤충 국명 또는 학명 입력", "")

if st.button("검색"):
    if not insect_name:
        st.warning("먼저 곤충 이름을 입력해주세요.")
    else:
        # 2) 곤충도감 목록 검색 (isctIlstrSearch) :contentReference[oaicite:0]{index=0}:contentReference[oaicite:1]{index=1}
        params_search = {
            "serviceKey": api_key,
            "st": "1",           # 1=국명 포함 검색
            "sw": insect_name,
            "numOfRows": "20",
            "pageNo": "1"
        }
        resp = requests.get(f"{BASE_URL}/isctIlstrSearch", params=params_search)
        root = ET.fromstring(resp.text)

        items = root.findall(".//item")
        if not items:
            st.info("검색 결과가 없습니다.")
        else:
            # 3) 목록에서 선택할 이름 리스트 생성
            options = []
            map_id = {}
            for it in items:
                name = it.findtext("insctOfnmKrlngNm") or it.findtext("btnc")
                pilbk = it.findtext("insctPilbkNo")  # 도감번호
                detailYn = it.findtext("detailYn")
                display = f"{name} ({pilbk})" + ("" if detailYn=="Y" else " - 상세없음")
                options.append(display)
                map_id[display] = {"pilbk": pilbk, "detailYn": detailYn}

            choice = st.selectbox("목록에서 곤충 선택", options)

            info = map_id[choice]
            if info["detailYn"] != "Y":
                st.warning("선택하신 곤충은 상세정보가 없습니다.")
            else:
                # 4) 상세정보 조회 (isctIlstrInfo) :contentReference[oaicite:2]{index=2}:contentReference[oaicite:3]{index=3}
                params_info = {
                    "serviceKey": api_key,
                    "q1": info["pilbk"]    # q1 = 도감번호(insctPilbkNo)
                }
                resp2 = requests.get(f"{BASE_URL}/isctIlstrInfo", params=params_info)
                root2 = ET.fromstring(resp2.text)
                item = root2.find(".//item")

                # 5) 이미지 로드
                img_url = item.findtext("imgUrl")
                if img_url and img_url.strip().upper() != "NONE":
                    st.subheader("이미지")
                    # HTTP 그대로 백엔드에서 받아오기
                    img_resp = requests.get(img_url)
                    if img_resp.status_code == 200:
                        st.image(img_resp.content, use_column_width=True)
                    else:
                        st.error(f"이미지 로드 실패 (HTTP {img_resp.status_code})")

                # 6) 주요 정보 출력
                st.subheader("기본 정보")
                st.write("• 학명:", item.findtext("btnc"))
                st.write("• 국명:", item.findtext("insctOfnmKrlngNm"))
                st.write("• 과명:", item.findtext("fmlyKorNm") or item.findtext("fmlyNm"))
                st.write("• 속명:", item.findtext("genusKorNm") or item.findtext("genusNm"))
                st.write("• 목명:", item.findtext("ordKorNm") or item.findtext("ordNm"))

                # 7) 상세 설명 항목별로
                def show_section(label, tag):
                    text = item.findtext(tag)
                    if text and text.strip():
                        st.markdown(f"**{label}**")
                        st.write(text)

                show_section("일반특징", "cont1")
                show_section("유충", "cont5")
                show_section("생태", "cont7")
                show_section("습성", "cont8")
                show_section("월동", "cont9")
                show_section("참고사항", "cont6")
                show_section("출현시기", "emrgcEraDscrt")
                show_section("출현수", "emrgcCnt")
