import streamlit as st
import requests
import xml.etree.ElementTree as ET
import math

# 1) secrets.toml에 설정된 Bugs_API_Key 사용
api_key       = st.secrets["Bugs_API_Key"]
BASE_URL      = "http://openapi.nature.go.kr/openapi/service/rest/InsectService"
ROWS_PER_PAGE = 10

st.title("🐞 곤충 표본 검색")

# 검색어 및 버튼
insect_name = st.text_input("곤충 국명 또는 학명 입력", "")
if st.button("검색"):
    st.session_state.page_no     = 1
    st.session_state.insect_name = insect_name

# 세션 초기화
if "page_no"      not in st.session_state: st.session_state.page_no     = 1
if "insect_name"  not in st.session_state: st.session_state.insect_name = ""
if "total_count"  not in st.session_state: st.session_state.total_count = 0
if "bug_items"    not in st.session_state: st.session_state.bug_items   = []
if "chosen"       not in st.session_state: st.session_state.chosen      = None
if "last_query"   not in st.session_state: st.session_state.last_query  = ("", 0)

# 데이터 조회 함수 (spcmSearch)
def fetch_bug_page(name, page_no):
    resp = requests.get(
        f"{BASE_URL}/spcmSearch",
        params={
            "serviceKey": api_key,
            "st":         "1",
            "sw":         name,
            "numOfRows":  str(ROWS_PER_PAGE),
            "pageNo":     str(page_no)
        }
    )
    root = ET.fromstring(resp.text)
    total = int(root.findtext(".//totalCount") or "0")
    items = root.findall(".//item")
    return total, items

# 검색/페이징 시 데이터 갱신
current_query = (st.session_state.insect_name, st.session_state.page_no)
if st.session_state.insect_name and st.session_state.last_query != current_query:
    total, items = fetch_bug_page(*current_query)
    st.session_state.total_count = total
    st.session_state.bug_items   = items
    st.session_state.last_query  = current_query

# 결과 건수 표시
if st.session_state.insect_name:
    st.write(f"🔎 '{st.session_state.insect_name}' 검색 결과: 총 {st.session_state.total_count} 건")

max_page = max(1, math.ceil(st.session_state.total_count / ROWS_PER_PAGE))

# 목록 및 상세뷰
if st.session_state.bug_items:
    col1, col2 = st.columns([1, 3])

    with col1:
        st.subheader("표본 목록")
        for it in st.session_state.bug_items:
            name    = it.findtext("insctofnmkrlngnm") or it.findtext("insctOfnmScnm")
            smpl_no = it.findtext("insctSmplNo")
            label   = f"{name} ({smpl_no})"
            if st.button(label, key=smpl_no):
                st.session_state.chosen = smpl_no

        prev_disabled = st.session_state.page_no <= 1
        next_disabled = st.session_state.page_no >= max_page
        p1, _, p3 = st.columns([1,1,1])
        with p1:
            if st.button("◀ 이전", disabled=prev_disabled):
                st.session_state.page_no -= 1
        with p3:
            if st.button("다음 ▶", disabled=next_disabled):
                st.session_state.page_no += 1

    with col2:
        if not st.session_state.chosen:
            st.info("왼쪽에서 표본을 선택하세요.")
        else:
            resp2 = requests.get(
                f"{BASE_URL}/spcmInfo",
                params={"serviceKey": api_key, "q1": st.session_state.chosen}
            )
            root2 = ET.fromstring(resp2.text)
            item  = root2.find(".//item")

            # 이미지
            img_url = item.findtext("imgUrl")
            if img_url and img_url.strip() and img_url.upper()!="NONE":
                img_resp = requests.get(img_url)
                if img_resp.status_code == 200:
                    st.image(img_resp.content, use_container_width=True)
                else:
                    st.error(f"이미지 로드 실패 (HTTP {img_resp.status_code})")

            # 기본 정보
            st.subheader("기본 정보")
            st.write("• 표본번호:", item.findtext("insctSmplNo"))
            st.write("• 학명:",     item.findtext("insctOfnmScnm"))
            st.write("• 국명:",     item.findtext("insctofnmkrlngnm"))
            st.write("• 채집일:",   item.findtext("clctDyDesc"))
            st.write("• 몸통길이:", item.findtext("torsoLngth"), "mm")
            st.write("• 날개길이:", item.findtext("wingLngth"), "mm")
            st.write("• 과명:",     item.findtext("fmlyKorNm") or item.findtext("fmlyNm"))
            st.write("• 목명:",     item.findtext("ordKorNm") or item.findtext("ordNm"))

            # 추가 설명
            def show_section(label, tag):
                txt = item.findtext(tag)
                if txt and txt.strip():
                    st.markdown(f"**{label}**")
                    st.write(txt)

            show_section("• 저작권",      "cprtCtnt")
            show_section("• 중국명",      "chnNm")
            show_section("• 라벨 채집지","labelUsgCllcnNmplc")
            show_section("• 최종수정일시","lastUpdtDtm")
