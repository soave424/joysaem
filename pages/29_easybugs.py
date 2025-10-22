import streamlit as st
import pandas as pd
import datetime
import io
import openai
import os
import requests
import xml.etree.ElementTree as ET
import math
import re

st.set_page_config(page_title="쉬운 곤충 도감", layout="wide")
st.title("🦋 쉬운 곤충 도감")

# API 키 설정 (환경변수 또는 직접 설정)
try:
    # Streamlit secrets에서 가져오기 시도
    try:
        openai_api_key = st.secrets["OPENAI_API_KEY"]
        bugs_api_key = st.secrets["Bugs_API_Key"]
    except:
        # secrets가 없으면 환경변수에서 가져오기
        openai_api_key = os.getenv("OPENAI_API_KEY")
        bugs_api_key = os.getenv("Bugs_API_Key")
    
    if not openai_api_key:
        st.error("⚠️ OpenAI API 키가 설정되지 않았습니다.")
        st.info("다음 중 하나의 방법으로 API 키를 설정해주세요:")
        st.code("""
# 방법 1: 환경변수 설정
export OPENAI_API_KEY="your_api_key_here"

# 방법 2: .streamlit/secrets.toml 파일에 추가
OPENAI_API_KEY = "your_api_key_here"
        """)
        st.stop()
    
    if not bugs_api_key or bugs_api_key == "your_bugs_api_key_here":
        st.warning("⚠️ 곤충도감 API 키가 설정되지 않았습니다.")
        st.info("""
        **곤충도감 API 키 발급 방법:**
        1. [국립생물자원관 공공데이터포털](https://www.data.go.kr/) 방문
        2. "곤충도감" 검색
        3. API 신청 후 키 발급받기
        4. 발급받은 키를 아래 방법으로 설정:
        """)
        st.code("""
# 방법 1: 환경변수 설정
export Bugs_API_Key="실제_발급받은_API_키"

# 방법 2: .streamlit/secrets.toml 파일에 추가
Bugs_API_Key = "실제_발급받은_API_키"
        """)
        
        # API 키가 없어도 앱은 계속 실행 (데모 모드)
        st.info("🔧 **데모 모드**: API 키 없이도 앱 구조를 확인할 수 있습니다.")
        bugs_api_key = None
        
    client = openai.OpenAI(api_key=openai_api_key)
except Exception as e:
    st.error(f"⚠️ API 키 설정 오류: {e}")
    st.stop()

# 기준 문서 로드
txt_path = os.path.join("txt", "navi.txt")
if os.path.exists(txt_path):
    with open(txt_path, "r", encoding="utf-8") as f:
        reference_doc = f.read()
else:
    reference_doc = ""
    st.warning("⚠️ navi.txt 파일을 찾을 수 없습니다.")

# ── 곤충도감 API 설정 ──
api_key = bugs_api_key
BASE_URL = "http://openapi.nature.go.kr/openapi/service/rest/InsectService"
ROWS_PER_PAGE = 10

st.subheader("🔎 EasyBugs 곤충 도감 검색")

# 디버깅 정보 표시
with st.expander("🔧 디버깅 정보"):
    st.write(f"OpenAI API 키 설정됨: {'✅' if openai_api_key else '❌'}")
    st.write(f"곤충도감 API 키 설정됨: {'✅' if bugs_api_key and bugs_api_key != 'your_bugs_api_key_here' else '❌'}")
    st.write(f"navi.txt 파일 존재: {'✅' if os.path.exists(txt_path) else '❌'}")
    if bugs_api_key == "your_bugs_api_key_here":
        st.warning("⚠️ 곤충도감 API 키가 예시 값으로 설정되어 있습니다. 실제 API 키를 발급받아 설정해주세요.")

insect_name = st.text_input("곤충 국명 또는 학명 입력", "")
if st.button("검색"):
    st.session_state.page_no = 1
    st.session_state.query_name = insect_name

display_mode = st.radio("정보 보기 방식 선택", ["원문 보기", "쉬운 말로 보기"], horizontal=True)

# 세션 상태 초기화
if "page_no" not in st.session_state: st.session_state.page_no = 1
if "query_name" not in st.session_state: st.session_state.query_name = ""
if "total_ct" not in st.session_state: st.session_state.total_ct = 0
if "ilstr_items" not in st.session_state: st.session_state.ilstr_items = []
if "chosen" not in st.session_state: st.session_state.chosen = None
if "last_q" not in st.session_state: st.session_state.last_q = ("", 0)

# ── 데이터 요청 함수 ──
def fetch_page(name, page_no):
    if not api_key:
        st.warning("🔧 데모 모드: 실제 API 키가 필요합니다.")
        return 0, []
    
    try:
        params = {
            "serviceKey": api_key,
            "st": "1",
            "sw": name,
            "numOfRows": str(ROWS_PER_PAGE),
            "pageNo": str(page_no)
        }
        r = requests.get(f"{BASE_URL}/isctIlstrSearch", params=params, timeout=10)
        r.raise_for_status()  # HTTP 오류 확인
        
        root = ET.fromstring(r.text)
        total = int(root.findtext(".//totalCount") or "0")
        items = root.findall(".//item")
        return total, items
    except requests.exceptions.RequestException as e:
        st.error(f"⚠️ API 요청 실패: {e}")
        return 0, []
    except ET.ParseError as e:
        st.error(f"⚠️ XML 파싱 오류: {e}")
        return 0, []
    except Exception as e:
        st.error(f"⚠️ 예상치 못한 오류: {e}")
        return 0, []

# ── 설명을 학생 수준으로 바꾸기 ──
def simplify_for_students(text):
    if not text.strip():
        return ""
    prompt = f"""
다음 설명은 곤충에 대한 설명이야. 원래 문장의 구조나 표현을 최대한 유지하되, 진짜 어려운 단어만 중학생이 이해할 수 있도록 풀어서 말해줘. 너무 많이 바꾸지 말고 꼭 필요한 단어만 쉬운 단어로 바꿔줘. 번데기, 애벌레 등은 그대로 남겨줘.

원문: {text}

쉬운 말로 바꾼 문장:
"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ 변환 실패: {e}"

# ── 출현 시기 표현 다듬기 ──
def format_emergence(text):
    if not text:
        return ""
    matches = re.findall(r"\d+", text)
    if display_mode == "쉬운 말로 보기" and matches:
        return ", ".join([f"{m}월" for m in matches])
    return text

# ── 정보 표시 함수 ──
def show(item, label, tag, format_func=None):
    txt = item.findtext(tag) or ""
    if format_func:
        txt = format_func(txt)
    if txt.strip():
        if display_mode == "원문 보기":
            st.markdown(f"**{label}**")
            st.write(txt)
        else:
            if label == "월동":
                st.markdown("**겨울을 나는 모습**")
                st.write(txt)
            elif label == "출현시기":
                st.markdown("**출현시기(월)**")
                st.write(txt)
            elif label in ["일반특징", "생태", "습성"]:
                st.markdown(f"**{label} (쉬운 말)**")
                st.info(simplify_for_students(txt))
            else:
                st.markdown(f"**{label}**")
                st.write(txt)

# ── 페이지별 결과 가져오기 ──
current_q = (st.session_state.query_name, st.session_state.page_no)
if st.session_state.query_name and st.session_state.last_q != current_q:
    total, items = fetch_page(*current_q)
    st.session_state.total_ct = total
    st.session_state.ilstr_items = items
    st.session_state.last_q = current_q

if st.session_state.query_name:
    st.write(f"🔎 '{st.session_state.query_name}' 검색 결과: 총 {st.session_state.total_ct}건")

max_page = max(1, math.ceil(st.session_state.total_ct / ROWS_PER_PAGE))

# ── 곤충 목록 및 상세정보 표시 ──
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
            if not api_key:
                st.warning("🔧 데모 모드: 실제 API 키가 필요합니다.")
            else:
                try:
                    r2 = requests.get(f"{BASE_URL}/isctIlstrInfo", params={"serviceKey": api_key, "q1": st.session_state.chosen}, timeout=10)
                    r2.raise_for_status()
                    root2 = ET.fromstring(r2.text)
                    items2 = root2.findall(".//item")

                    if not items2:
                        st.error("상세정보가 없습니다.")
                    else:
                        item = items2[0]
                        img_url = item.findtext("imgUrl") or ""
                        if img_url.strip():
                            st.subheader("🖼 이미지")
                            try:
                                resp_img = requests.get(img_url, timeout=10)
                                resp_img.raise_for_status()
                                st.image(resp_img.content, use_container_width=True)
                            except Exception as e:
                                st.error(f"이미지 로드 실패: {e}")

                        st.subheader("📋 곤충 정보")
                        st.write("• 학명:", item.findtext("btnc"))
                        st.write("• 국명:", item.findtext("insctOfnmKrlngNm"))
                        st.write("• 과명:", item.findtext("fmlyKorNm") or item.findtext("fmlyNm"))
                        st.write("• 속명:", item.findtext("genusKorNm") or item.findtext("genusNm"))
                        st.write("• 목명:", item.findtext("ordKorNm") or item.findtext("ordNm"))

                        # 상세 정보 출력
                        show(item, "일반특징", "cont1")
                        show(item, "유충", "cont5")
                        show(item, "생태", "cont7")
                        show(item, "습성", "cont8")
                        show(item, "월동", "cont9")
                        show(item, "출현시기", "emrgcEraDscrt", format_func=format_emergence)
                        show(item, "참고사항", "cont6")
                except requests.exceptions.RequestException as e:
                    st.error(f"⚠️ 상세정보 API 요청 실패: {e}")
                except ET.ParseError as e:
                    st.error(f"⚠️ 상세정보 XML 파싱 오류: {e}")
                except Exception as e:
                    st.error(f"⚠️ 상세정보 로드 오류: {e}")
