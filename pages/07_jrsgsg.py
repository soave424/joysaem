import streamlit as st
import requests
from streamlit import download_button

def download_pdf(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    return None

st.title('Download PDF')

# URL of the PDF file
pdf_url = "https://jrsgsg.hankyung.com/js/pdfjs/web/viewer.html?file=/pdfdata/2024/08/26/20240826_0110_01001.pdf"  # Replace with your actual URL

if st.button('Download PDF'):
    pdf_data = download_pdf(pdf_url)
    if pdf_data:
        st.download_button(
            label="Download PDF",
            data=pdf_data,
            file_name="downloaded_file.pdf",
            mime="application/octet-stream"
        )
    else:
        st.error("Failed to download PDF")
