import streamlit as st
import requests
import xml.etree.ElementTree as ET

api_key  = st.secrets["PlankDrawD_API_Key"]
BASE_URL = "http://openapi.nature.go.kr/openapi/service/rest/InsectService"

st.title("🐞 곤충 도감 검색")

# 검색어 입력
insect_name = st.text_input("곤충 국명 또는 학명 입력", "")
page_no     = st.number_input("페이지 번호", 1, 1, 1)

# 검색 결과를 session_state에 저장
if st.button("검색"):
    params = {
        "serviceKey": api_key,
        "st":         "1",
        "sw":         insect_name,
        "numOfRows":  "20",
        "pageNo":     str(page_no)
    }
    resp = requests.get(f"{BASE_URL}/isctIlstrSearch", params=params)
    root = ET.fromstring(resp.text)
    items = root.findall(".//item")
    st.session_state["items"] = items
    # 선택 초기화
    st.session_state["chosen"] = None

# 초기값 세팅
if "items" not in st.session_state:
    st.session_state["items"] = []
if "chosen" not in st.session_state:
    st.session_state["chosen"] = None

items = st.session_state["items"]

if items:
    col1, col2 = st.columns([1, 3])
    # 왼쪽: 버튼 리스트
    with col1:
        st.subheader("🔍 곤충 목록")
        for it in items:
            name     = it.findtext("insctOfnmKrlngNm") or it.findtext("btnc")
            pilbk    = it.findtext("insctPilbkNo")
            detailYn = it.findtext("detailYn")
            label = f"{name} ({pilbk})" + ("" if detailYn=="Y" else " – 상세없음")
            if st.button(label, key=pilbk):
                st.session_state["chosen"] = it

    # 오른쪽: 상세 정보
    with col2:
        chosen = st.session_state["chosen"]
        if not chosen:
            st.info("좌측 목록에서 곤충 버튼을 눌러주세요.")
        else:
            # detailYn 체크
            if chosen.findtext("detailYn") != "Y":
                st.warning("선택하신 곤충은 상세정보가 없습니다.")
            else:
                # 상세 조회
                pilbk = chosen.findtext("insctPilbkNo")
                resp2 = requests.get(
                    f"{BASE_URL}/isctIlstrInfo",
                    params={"serviceKey": api_key, "q1": pilbk}
                )
                root2 = ET.fromstring(resp2.text)
                item  = root2.find(".//item")

                st.subheader("📷 이미지")
                img_url = item.findtext("imgUrl")
                if img_url and img_url.strip().upper()!="NONE":
                    img_resp = requests.get(img_url)
                    if img_resp.status_code == 200:
                        st.image(img_resp.content, use_container_width=True)
                    else:
                        st.error(f"이미지 로드 실패 (HTTP {img_resp.status_code})")

                st.subheader("📋 기본 정보")
                st.write("• 학명:", item.findtext("btnc"))
                st.write("• 국명:", item.findtext("insctOfnmKrlngNm"))
                st.write("• 과명:", item.findtext("fmlyKorNm") or item.findtext("fmlyNm"))
                st.write("• 속명:", item.findtext("genusKorNm") or item.findtext("genusNm"))
                st.write("• 목명:", item.findtext("ordKorNm") or item.findtext("ordNm"))

                def show_section(label, tag):
                    txt = item.findtext(tag)
                    if txt and txt.strip():
                        st.markdown(f"**{label}**")
                        st.write(txt)

                show_section("일반특징",  "cont1")
                show_section("유충",      "cont5")
                show_section("생태",      "cont7")
                show_section("습성",      "cont8")
                show_section("월동",      "cont9")
                show_section("출현시기",  "emrgcEraDscrt")
                show_section("참고사항",  "cont6")
