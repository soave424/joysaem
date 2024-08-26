import streamlit as st
import datetime
import requests
from PyPDF2 import PdfMerger

def generate_pdf_urls(base_date, issue_number):
    pdf_base_url = "https://jrsgsg.hankyung.com/js/pdfjs/web/viewer.html?file="
    date_str = base_date.strftime("%Y/%m/%d/%Y%m%d")
    return [f"{pdf_base_url}/pdfdata/{date_str}_0110_01{str(i).zfill(3)}.pdf" for i in range(10, 18)]

def download_and_merge_pdfs(pdf_urls, output_filename):
    merger = PdfMerger()
    for url in pdf_urls:
        response = requests.get(url)
        if response.status_code == 200:
            with open('temp.pdf', 'wb') as f:
                f.write(response.content)
            merger.append('temp.pdf')
    merger.write(output_filename)
    merger.close()

# 스트림릿 UI
st.title("PDF 다운로드 및 합치기")

# 시작 날짜 및 호수 설정
start_date = datetime.date(2022, 2, 21)
current_date = st.session_state.get('current_date', start_date)
issue_number = 126 - int((current_date - start_date).days / 7)

# 버튼 추가
if st.button('다음 주 PDF 가져오기'):
    current_date += datetime.timedelta(days=7)
    st.session_state['current_date'] = current_date
    issue_number -= 1

    pdf_urls = generate_pdf_urls(current_date, issue_number)
    output_filename = f"merged_{current_date.strftime('%Y%m%d')}.pdf"
    download_and_merge_pdfs(pdf_urls, output_filename)
    st.success(f"{output_filename} 생성 완료!")

# 현재 처리 날짜 표시
st.write(f"현재 처리 날짜: {current_date.strftime('%Y-%m-%d')} (호수: {issue_number})")
