import streamlit as st
import pandas as pd
import datetime
import io
import openai
import os
import requests
import xml.etree.ElementTree as ET
import math

st.set_page_config(page_title="쉬운 곤충 도감", layout="wide")
st.title("🦋 쉬운 곤충 도감")

client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# 기준 문서 로드
txt_path = os.path.join("txt", "navi.txt")
if os.path.exists(txt_path):
    with open(txt_path, "r", encoding="utf-8") as f:
        reference_doc = f.read()
else:
    reference_doc = ""

# ── 곤충도감 API 설정 ──
api_key = st.secrets["Bugs_API_Key"]
BASE_URL      = "http://openapi.nature.go.kr/openapi/service/rest/InsectService"
ROWS_PER_PAGE = 10

st.subheader("🔎 EasyBugs 곤충 도감 검색")
insect_name = st.text_input("곤충 국명 또는 학명 입력", "")
if st.button("검색"):
    st.session_state.page_no = 1
    st.session_state.query_name = insect_name

if "page_no" not in st.session_state: st.session_state.page_no = 1
if "query_name" not in st.session_state: st.session_state.query_name = ""
if "total_ct" not in st.session_state: st.session_state.total_ct = 0
if "ilstr_items" not in st.session_state: st.session_state.ilstr_items = []
if "chosen" not in st.session_state: st.session_state.chosen = None
if "last_q" not in st.session_state: st.session_state.last_q = ("", 0)

def fetch_page(name, page_no):
    params = {
        "serviceKey": api_key,
        "st": "1",
        "sw": name,
        "numOfRows": str(ROWS_PER_PAGE),
        "pageNo": str(page_no)
    }
    r = requests.get(f"{BASE_URL}/isctIlstrSearch", params=params)
    root = ET.fromstring(r.text)
    total = int(root.findtext(".//totalCount") or "0")
    items = root.findall(".//item")
    return total, items

def simplify_for_kids(text):
    if not text.strip():
        return ""
    prompt = f"""
다음 설명을 초등학생도 이해할 수 있도록 쉬운 말로 바꿔줘. 너무 어렵거나 학술적인 단어는 풀어서 설명해줘.

원문: {text}

쉬운 설명:
"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ 변환 실패: {e}"

current_q = (st.session_state.query_name, st.session_state.page_no)
if st.session_state.query_name and st.session_state.last_q != current_q:
    total, items = fetch_page(*current_q)
    st.session_state.total_ct = total
    st.session_state.ilstr_items = items
    st.session_state.last_q = current_q

if st.session_state.query_name:
    st.write(f"🔎 '{st.session_state.query_name}' 검색 결과: 총 {st.session_state.total_ct}건")

max_page = max(1, math.ceil(st.session_state.total_ct / ROWS_PER_PAGE))

if st.session_state.ilstr_items:
    col1, col2 = st.columns([2, 3])
    prev_disabled = st.session_state.page_no <= 1
    next_disabled = st.session_state.page_no >= max_page

    with col1:
        st.subheader("📚 목록")
        for it in st.session_state.ilstr_items:
            common = it.findtext("insctOfnmKrlngNm") or ""
            sci = it.findtext("btnc") or ""
            pid = it.findtext("insctPilbkNo") or ""
            label = f"{common or sci} ({pid})"
            if st.button(label, key=f"btn_{pid}"):
                st.session_state.chosen = pid

        nav1, _, nav3 = st.columns([1, 1, 1])
        with nav1:
            if st.button("◀ 이전", disabled=prev_disabled):
                st.session_state.page_no -= 1
        with nav3:
            if st.button("다음 ▶", disabled=next_disabled):
                st.session_state.page_no += 1

    with col2:
        if not st.session_state.chosen:
            st.info("왼쪽 목록에서 곤충을 선택하세요.")
        else:
            r2 = requests.get(f"{BASE_URL}/isctIlstrInfo", params={"serviceKey": api_key, "q1": st.session_state.chosen})
            root2 = ET.fromstring(r2.text)
            items2 = root2.findall(".//item")

            if not items2:
                st.error("상세정보가 없습니다.")
            else:
                item = items2[0]
                img_url = item.findtext("imgUrl") or ""
                if img_url.strip():
                    st.image(img_url, use_container_width=True)

                st.subheader("📋 곤충 정보")
                st.write("• 학명:", item.findtext("btnc"))
                st.write("• 국명:", item.findtext("insctOfnmKrlngNm"))
                st.write("• 과명:", item.findtext("fmlyKorNm") or item.findtext("fmlyNm"))
                st.write("• 속명:", item.findtext("genusKorNm") or item.findtext("genusNm"))
                st.write("• 목명:", item.findtext("ordKorNm") or item.findtext("ordNm"))

                def show(label, tag):
                    txt = item.findtext(tag) or ""
                    if txt.strip():
                        st.markdown(f"**{label} (원문)**")
                        st.write(txt)
                        st.markdown(f"**{label} (쉬운 말)**")
                        st.info(simplify_for_kids(txt))

                show("일반특징", "cont1")
                show("유충", "cont5")
                show("생태", "cont7")
                show("습성", "cont8")
                show("월동", "cont9")
                show("출현시기", "emrgcEraDscrt")
                show("참고사항", "cont6")
