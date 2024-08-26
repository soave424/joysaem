import streamlit as st

st.title('View PDFs from 1 to 16')

# Generate URLs for PDFs numbered from 01 to 16
base_url = "https://jrsgsg.hankyung.com/js/pdfjs/web/viewer.html?file=/pdfdata/2024/08/26/20240826_0110_01"
pdf_urls = {f"{i:02}": f"{base_url}{i:02}.pdf" for i in range(1, 17)}

# Create buttons for each PDF and display the selected PDF
selected_pdf = st.selectbox("Select a PDF number:", options=list(pdf_urls.keys()), format_func=lambda x: f"PDF {x}")
pdf_url = pdf_urls[selected_pdf]

if pdf_url:
    st.write(f"Displaying PDF {selected_pdf}")
    st.markdown(f'<iframe src="{pdf_url}" width="700" height="1000" type="application/pdf"></iframe>', unsafe_allow_html=True)
else:
    st.write("Please select a PDF number to display the PDF.")
