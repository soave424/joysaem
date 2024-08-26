import streamlit as st
import pdfplumber
import requests
from io import BytesIO

st.title('Extract Text from PDF')

# Input field for the PDF URL
pdf_url = st.text_input('Enter the PDF URL')

def extract_text_from_pdf(url):
    response = requests.get(url)
    with pdfplumber.open(BytesIO(response.content)) as pdf:
        pages = pdf.pages
        text = ''
        for page in pages:
            text += page.extract_text() + '\n'  # Extract text from each page
        return text

if pdf_url:
    extracted_text = extract_text_from_pdf(pdf_url)
    if extracted_text:
        st.text_area("Extracted Text", extracted_text, height=300)
    else:
        st.error("No text could be extracted from the PDF.")
else:
    st.write("Please enter a URL to extract text from a PDF.")
