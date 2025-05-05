import streamlit as st
import requests
import xml.etree.ElementTree as ET
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

st.title("학교 정보 조회기 (NEIS OpenAPI 기반)")
st.markdown("학교명을 복사해서 붙여넣으면 시도명, 주소 정보를 보여줍니다.")

# 인증키
API_KEY = "23fc73f44f164862894394b02006b73d"

# 기준 위치: 경기도 고양시 지효초등학교
geolocator = Nominatim(user_agent="school_locator")
base_location = geolocator.geocode("지효초등학교, 경기도 고양시")
base_coords = (base_location.latitude, base_location.longitude)

# 사용자 입력
school_input = st.text_area("학교명을 줄 단위로 입력하세요:", height=300, placeholder="예:\n판교대장중학교\n서해중학교\n...")

if st.button("학교 정보 조회"):
    school_names = [name.strip() for name in school_input.split("\n") if name.strip()]
    results = []

    for name in school_names:
        url = (
            f"https://open.neis.go.kr/hub/schoolInfo"
            f"?KEY={API_KEY}&Type=xml&pIndex=1&pSize=100&SCHUL_NM={name}"
        )
        try:
            res = requests.get(url)
            if res.status_code == 200:
                root = ET.fromstring(res.content)
                rows = root.findall(".//row")

                # 정확히 일치하는 학교명 목록 추출
                exact_matches = [row for row in rows if row.findtext("SCHUL_NM", "") == name]

                # 경기 우선 선택
                selected_row = None
                for row in exact_matches:
                    if "경기" in row.findtext("ATPT_OFCDC_SC_NM", ""):
                        selected_row = row
                        break

                # 경기 없으면 정확히 일치하는 것 중 첫 번째
                if not selected_row and exact_matches:
                    selected_row = exact_matches[0]

                # 정확히 일치한 게 없으면 전체 중 첫 번째
                if not selected_row and rows:
                    selected_row = rows[0]

                if selected_row:
                    school_name = selected_row.findtext("SCHUL_NM", "")
                    city_name = selected_row.findtext("LCTN_SC_NM", "")
                    address = selected_row.findtext("ORG_RDNMA", "")
                    try:
                        location = geolocator.geocode(address)
                        if location:
                            school_coords = (location.latitude, location.longitude)
                            distance_km = round(geodesic(base_coords, school_coords).km, 2)
                        else:
                            distance_km = "좌표 없음"
                    except:
                        distance_km = "계산 오류"

                    results.append({
                        "학교명": school_name,
                        "시도명": city_name,
                        "도로명주소": address,
                        "기준지(지효초)까지 거리(km)": distance_km
                    })
                else:
                    results.append({"학교명": name, "시도명": "-", "도로명주소": "검색결과 없음", "기준지(지효초)까지 거리(km)": "-"})
            else:
                results.append({"학교명": name, "시도명": "-",  "도로명주소": f"에러: {res.status_code}", "기준지(지효초)까지 거리(km)": "-"})
        except Exception as e:
            results.append({"학교명": name, "시도명": "-", "도로명주소": str(e), "기준지(지효초)까지 거리(km)": "-"})

    df = pd.DataFrame(results)
    st.success("조회 완료!")
    st.dataframe(df)

    # 다운로드 옵션
    csv = df.to_csv(index=False, encoding="utf-8-sig")
    st.download_button("CSV로 다운로드", data=csv, file_name="학교정보.csv", mime="text/csv")