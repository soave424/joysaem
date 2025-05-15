import streamlit as st
import requests
import xml.etree.ElementTree as ET

# secrets.toml에 PlankDrawD_API_Key로 등록된 디코딩된 키 사용
api_key = st.secrets["PlankDrawD_API_Key"]
BASE_URL = "http://openapi.nature.go.kr/openapi/service/rest/InsectService"

st.title("🐞 곤충 도감 검색")

# 1) 검색어 입력
insect_name = st.text_input("곤충 국명 또는 학명 입력", "")
if st.button("검색"):
    if not insect_name:
        st.warning("먼저 곤충 이름을 입력해주세요.")
    else:
        # 2) 목록 검색
        resp = requests.get(
            f"{BASE_URL}/isctIlstrSearch",
            params={"serviceKey": api_key, "st": "1", "sw": insect_name, "numOfRows": "20", "pageNo": "1"}
        )
        root = ET.fromstring(resp.text)
        items = root.findall(".//item")

        if not items:
            st.info("검색 결과가 없습니다.")
        else:
            # 3) 컬럼 나누기: 왼쪽(col1)은 목록, 오른쪽(col2)은 상세
            col1, col2 = st.columns([1, 3])

            # 왼쪽 열: 선택박스
            with col1:
                options = []
                map_id = {}
                for it in items:
                    name = it.findtext("insctOfnmKrlngNm") or it.findtext("btnc")
                    pilbk = it.findtext("insctPilbkNo")
                    detailYn = it.findtext("detailYn")
                    label = f"{name} ({pilbk})" + ("" if detailYn=="Y" else " – 상세없음")
                    options.append(label)
                    map_id[label] = {"pilbk": pilbk, "detailYn": detailYn}

                choice = st.selectbox("곤충 선택", options)

            # 오른쪽 열: 상세 정보
            with col2:
                info = map_id[choice]
                if info["detailYn"] != "Y":
                    st.warning("선택하신 곤충은 상세정보가 없습니다.")
                else:
                    # 4) 상세정보 호출
                    resp2 = requests.get(
                        f"{BASE_URL}/isctIlstrInfo",
                        params={"serviceKey": api_key, "q1": info["pilbk"]}
                    )
                    root2 = ET.fromstring(resp2.text)
                    item = root2.find(".//item")

                    # 이미지
                    img_url = item.findtext("imgUrl")
                    if img_url and img_url.strip().upper() != "NONE":
                        st.subheader("이미지")
                        img_resp = requests.get(img_url)
                        if img_resp.status_code == 200:
                            st.image(img_resp.content, use_container_width=True)
                        else:
                            st.error(f"이미지 로드 실패 (HTTP {img_resp.status_code})")

                    # 기본 정보
                    st.subheader("기본 정보")
                    st.write("• 학명:", item.findtext("btnc"))
                    st.write("• 국명:", item.findtext("insctOfnmKrlngNm"))
                    st.write("• 과명:", item.findtext("fmlyKorNm") or item.findtext("fmlyNm"))
                    st.write("• 속명:", item.findtext("genusKorNm") or item.findtext("genusNm"))
                    st.write("• 목명:", item.findtext("ordKorNm") or item.findtext("ordNm"))

                    # 상세 설명
                    def show_section(label, tag):
                        txt = item.findtext(tag)
                        if txt and txt.strip():
                            st.markdown(f"**{label}**")
                            st.write(txt)

                    show_section("일반특징", "cont1")
                    show_section("유충",      "cont5")
                    show_section("생태",      "cont7")
                    show_section("습성",      "cont8")
                    show_section("월동",      "cont9")
                    show_section("출현시기",  "emrgcEraDscrt")
                    show_section("참고사항",  "cont6")
