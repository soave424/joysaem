import streamlit as st
import requests
import xml.etree.ElementTree as ET
import pandas as pd

st.title("학교 정보 조회기 (NEIS OpenAPI 기반)")
st.markdown("학교명을 복사해서 붙여넣으면 시도명, 교육청명, 주소 정보를 보여줍니다.")

# 인증키
API_KEY = "23fc73f44f164862894394b02006b73d"

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
                row = root.find(".//row")
                if row is not None:
                    results.append({
                        "학교명": row.findtext("SCHUL_NM", ""),
                        "시도명": row.findtext("LCTN_SC_NM", ""),
                        "도로명주소": row.findtext("ORG_RDNMA", ""),
                    })
                else:
                    results.append({"학교명": name, "시도명": "-", "도로명주소": "검색결과 없음"})
            else:
                results.append({"학교명": name, "시도명": "-",  "도로명주소": f"에러: {res.status_code}"})
        except Exception as e:
            results.append({"학교명": name, "시도명": "-", "도로명주소": str(e)})

    df = pd.DataFrame(results)
    st.success("조회 완료!")
    st.dataframe(df)

    # 다운로드 옵션
    csv = df.to_csv(index=False, encoding="utf-8-sig")
    st.download_button("CSV로 다운로드", data=csv, file_name="학교정보.csv", mime="text/csv")
