import streamlit as st
import requests
import xml.etree.ElementTree as ET
import math

# 1) secrets.toml에 등록된 키 사용
api_key  = st.secrets["PlankDrawD_API_Key"]
BASE_URL = "http://openapi.nature.go.kr/openapi/service/rest/InsectService"
ROWS_PER_PAGE = 10  # 한 페이지당 결과 수

st.title("🐞 곤충 도감 검색")

# --- 검색어 입력 및 검색 실행 ---
insect_name = st.text_input("곤충 국명 또는 학명 입력", "")
if st.button("검색"):
    # 페이지 초기화
    st.session_state.page_no = 1
    st.session_state.insect_name = insect_name

# --- session_state 기본 초기화 ---
if "page_no" not in st.session_state:
    st.session_state.page_no = 1
if "insect_name" not in st.session_state:
    st.session_state.insect_name = ""
if "total_count" not in st.session_state:
    st.session_state.total_count = 0
if "items" not in st.session_state:
    st.session_state.items = []

# --- 데이터 조회 함수 ---
def fetch_page(name, page_no):
    params = {
        "serviceKey": api_key,
        "st":         "1",               # 국명 포함 검색
        "sw":         name,
        "numOfRows":  str(ROWS_PER_PAGE), 
        "pageNo":     str(page_no)
    }
    resp = requests.get(f"{BASE_URL}/isctIlstrSearch", params=params)
    root = ET.fromstring(resp.text)

    # 전체 건수, 페이지 정보 파싱
    total = int(root.findtext(".//totalCount") or "0")  # 전체카운트 :contentReference[oaicite:5]{index=5}:contentReference[oaicite:6]{index=6}
    page  = int(root.findtext(".//pageNo") or "1")
    items = root.findall(".//item")

    return total, page, items

# --- 새로 검색했거나 페이지를 변경했을 때 데이터 갱신 ---
needs_fetch = (
    st.session_state.insect_name != "" and
    (
        "last_query" not in st.session_state or
        st.session_state.last_query != (st.session_state.insect_name, st.session_state.page_no)
    )
)
if needs_fetch:
    total, page, items = fetch_page(st.session_state.insect_name, st.session_state.page_no)
    st.session_state.total_count = total
    st.session_state.items = items
    st.session_state.last_query = (st.session_state.insect_name, st.session_state.page_no)

# --- 검색 결과 정보 표시 ---
if st.session_state.insect_name:
    st.write(f"🔎 '{st.session_state.insect_name}' 검색 결과: 총 {st.session_state.total_count} 건")

# --- 페이징 계산 ---
max_page = math.ceil(st.session_state.total_count / ROWS_PER_PAGE) if st.session_state.total_count else 1

# --- 목록 및 상세 영역 ---
if st.session_state.items:
    col1, col2 = st.columns([1, 3])

    # 왼쪽: 곤충 목록 + 페이지 네비게이션
    with col1:
        st.subheader("곤충 목록")
        for it in st.session_state.items:
            name     = it.findtext("insctOfnmKrlngNm") or it.findtext("btnc")
            pilbk    = it.findtext("insctPilbkNo")
            detailYn = it.findtext("detailYn")
            label = f"{name} ({pilbk})" + ("" if detailYn=="Y" else " – 상세없음")
            if st.button(label, key=pilbk):
                st.session_state.chosen = pilbk

        # 페이지 네비게이션 버튼
        prev_disabled = st.session_state.page_no <= 1
        next_disabled = st.session_state.page_no >= max_page

        nav1, nav2, nav3 = st.columns([1, 1, 1])
        with nav1:
            if st.button("◀ 이전", disabled=prev_disabled):
                st.session_state.page_no -= 1
        with nav3:
            if st.button("다음 ▶", disabled=next_disabled):
                st.session_state.page_no += 1

    # 오른쪽: 선택된 곤충 상세 정보
    with col2:
        chosen = st.session_state.get("chosen", None)
        if not chosen:
            st.info("목록에서 곤충 버튼을 눌러주세요.")
        else:
            # 도감번호로 상세조회
            resp2 = requests.get(
                f"{BASE_URL}/isctIlstrInfo",
                params={"serviceKey": api_key, "q1": chosen}
            )
            root2 = ET.fromstring(resp2.text)
            item = root2.find(".//item")

            # 이미지
            img_url = item.findtext("imgUrl")
            if img_url and img_url.strip().upper() != "NONE":
                st.subheader("🖼️ 이미지")
                # HTTP 직접 다운로드 후 표시
                img_resp = requests.get(img_url)
                if img_resp.status_code == 200:
                    st.image(img_resp.content, use_container_width=True)
                else:
                    st.error(f"이미지 로드 실패 (HTTP {img_resp.status_code})")

            # 기본 정보
            st.subheader("📋 기본 정보")
            st.write("• 학명:", item.findtext("btnc"))
            st.write("• 국명:", item.findtext("insctOfnmKrlngNm"))
            st.write("• 과명:", item.findtext("fmlyKorNm") or item.findtext("familyNm"))
            st.write("• 속명:", item.findtext("genusKorNm") or item.findtext("genusNm"))
            st.write("• 목명:", item.findtext("ordKorNm") or item.findtext("ordNm"))

            # 상세 설명 섹션
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
