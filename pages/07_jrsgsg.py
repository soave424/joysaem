import streamlit as st
import requests
import pdfkit
import os

st.title('View and Download PDFs')

# Create an input field for the base URL
base_url = st.text_input('Enter the base URL without the PDF number (e.g., https://jrsgsg.hankyung.com/pdfdata/2024/08/26/20240826_0110_010):')

# Initialize session state to keep track of displayed PDFs
if 'show_pdf' not in st.session_state:
    st.session_state['show_pdf'] = {i: False for i in range(1, 17)}

# Ensure the base URL is entered
if base_url:
    # Create buttons for each PDF number from 01 to 16
    for i in range(1, 17):
        button_label = f"View PDF {i:02}"
        if st.button(button_label):
            st.session_state['show_pdf'][i] = not st.session_state['show_pdf'][i]
        
        # If the corresponding button was pressed, show or hide the PDF
        if st.session_state['show_pdf'][i]:
            pdf_url = f"{base_url}{i:02}.pdf"
            st.write(f"Displaying PDF {i:02}")
            st.markdown(f'<iframe src="{pdf_url}" width="700" height="1000" type="application/pdf"></iframe>', unsafe_allow_html=True)
        else:
            st.write(f"PDF {i:02} is hidden")

    # Download and merge all PDFs
    if st.button("Download All PDFs as One"):
        pdf_urls = [f"{base_url}{i:02}.pdf" for i in range(1, 17)]
        output_filename = "merged.pdf"
        pdfs = []

        for url in pdf_urls:
            response = requests.get(url)
            if response.status_code == 200:
                temp_filename = f'temp_{os.path.basename(url)}'
                with open(temp_filename, 'wb') as f:
                    f.write(response.content)
                pdfs.append(temp_filename)

        pdfkit.from_file(pdfs, output_filename)

        # Clean up temp files
        for temp_filename in pdfs:
            if os.path.exists(temp_filename):
                os.remove(temp_filename)

        with open(output_filename, "rb") as f:
            st.download_button(
                label="Download Merged PDF",
                data=f,
                file_name=output_filename,
                mime="application/pdf"
            )

        st.success(f"Merged PDF created and ready to download!")
else:
    st.write("Please enter a base URL to display and download the PDFs.")
