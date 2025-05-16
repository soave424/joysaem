import streamlit as st
import requests
import xml.etree.ElementTree as ET
import math

# ── 1) secrets.toml에 Bugs_API_Key 로 등록하세요
api_key       = st.secrets["Bugs_API_Key"]
BASE_URL      = "http://openapi.nature.go.kr/openapi/service/rest/InsectService"
ROWS_PER_PAGE = 10  # 한 페이지당 항목 수

st.title("🦋 곤충 도감 검색")

# ── 2) 검색창 & 실행
insect_name = st.text_input("곤충 국명 또는 학명 입력", "")
if st.button("검색"):
    st.session_state.page_no    = 1
    st.session_state.query_name = insect_name

# ── 3) session_state 기본값
if "page_no"     not in st.session_state: st.session_state.page_no     = 1
if "query_name"  not in st.session_state: st.session_state.query_name  = ""
if "total_ct"    not in st.session_state: st.session_state.total_ct    = 0
if "ilstr_items" not in st.session_state: st.session_state.ilstr_items = []
if "chosen"      not in st.session_state: st.session_state.chosen      = None
if "last_q"      not in st.session_state: st.session_state.last_q      = ("", 0)

# ── 4) 도감 일러스트 목록 검색 함수 (isctIlstrSearch)
def fetch_page(name, page_no):
    params = {
        "serviceKey": api_key,
        "st":         "1",               # 1=국명 포함 검색
        "sw":         name,
        "numOfRows":  str(ROWS_PER_PAGE),
        "pageNo":     str(page_no)
    }
    r    = requests.get(f"{BASE_URL}/isctIlstrSearch", params=params)
    root = ET.fromstring(r.text)
    total = int(root.findtext(".//totalCount") or "0")
    items = root.findall(".//item")
    return total, items

# ── 5) 검색어나 페이지 변경 시 데이터 갱신
current_q = (st.session_state.query_name, st.session_state.page_no)
if st.session_state.query_name and st.session_state.last_q != current_q:
    total, items = fetch_page(*current_q)
    st.session_state.total_ct    = total
    st.session_state.ilstr_items = items
    st.session_state.last_q      = current_q

# ── 6) 검색 결과 건수 표시
if st.session_state.query_name:
    st.write(f"🔎 '{st.session_state.query_name}' 검색 결과: 총 {st.session_state.total_ct}건")

# ── 7) 페이지 수 계산
max_page = max(1, math.ceil(st.session_state.total_ct / ROWS_PER_PAGE))

# ── 8) 목록+상세 레이아웃 (2:3 비율)
if st.session_state.ilstr_items:
    col1, col2 = st.columns([2, 3])

    # ◀ 이전 / 다음 ▶ 버튼 비활성화 여부
    prev_disabled = st.session_state.page_no <= 1
    next_disabled = st.session_state.page_no >= max_page

    # ── 왼쪽: 목록 + 페이징
    with col1:
        st.subheader("🔍 목록")
        for it in st.session_state.ilstr_items:
            common = it.findtext("insctOfnmKrlngNm") or ""
            sci    = it.findtext("btnc")             or ""
            pid    = it.findtext("insctPilbkNo")     or ""
            label  = f"{common or sci} ({pid})"
            if st.button(label, key=f"btn_{pid}"):
                st.session_state.chosen = pid

        nav1, _, nav3 = st.columns([1, 1, 1])
        with nav1:
            if st.button("◀ 이전", disabled=prev_disabled):
                st.session_state.page_no -= 1
        with nav3:
            if st.button("다음 ▶", disabled=next_disabled):
                st.session_state.page_no += 1

    # ── 오른쪽: 상세뷰 (isctIlstrInfo)
    with col2:
        if not st.session_state.chosen:
            st.info("왼쪽 목록에서 곤충을 선택하세요.")
        else:
            r2     = requests.get(
                        f"{BASE_URL}/isctIlstrInfo",
                        params={"serviceKey": api_key, "q1": st.session_state.chosen}
                     )
            root2  = ET.fromstring(r2.text)
            items2 = root2.findall(".//item")

            if not items2:
                st.error("상세정보가 없습니다.")
            else:
                item = items2[0]

                # 이미지
                img_url = item.findtext("imgUrl") or ""
                if img_url.strip():
                    st.subheader("🖼 이미지")
                    resp_img = requests.get(img_url)
                    if resp_img.status_code == 200:
                        st.image(resp_img.content, use_container_width=True)
                    else:
                        st.error(f"이미지 로드 실패 (HTTP {resp_img.status_code})")

                # 기본 정보
                st.subheader("📋 정보")
                st.write("• 학명:", item.findtext("btnc"))
                st.write("• 국명:", item.findtext("insctOfnmKrlngNm"))
                st.write("• 과명:", item.findtext("fmlyKorNm") or item.findtext("fmlyNm"))
                st.write("• 속명:", item.findtext("genusKorNm") or item.findtext("genusNm"))
                st.write("• 목명:", item.findtext("ordKorNm") or item.findtext("ordNm"))

                # 상세 설명
                def show(label, tag):
                    txt = item.findtext(tag) or ""
                    if txt.strip():
                        st.markdown(f"**{label}**")
                        st.write(txt)

                show("일반특징",   "cont1")
                show("유충",       "cont5")
                show("생태",       "cont7")
                show("습성",       "cont8")
                show("월동",       "cont9")
                show("출현시기",   "emrgcEraDscrt")
                show("참고사항",   "cont6")
