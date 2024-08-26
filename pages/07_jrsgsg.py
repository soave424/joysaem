import streamlit as st

st.title('View PDFs from 1 to 16')

# Create an input field for the base URL
base_url = st.text_input('Enter the base URL without the PDF number (e.g., https://jrsgsg.hankyung.com/pdfdata/2024/08/26/20240826_0110_010):')

# Ensure the base URL is entered
if base_url:
    # Create buttons for each PDF number from 01 to 16
    for i in range(1, 17):
        button_label = f"View PDF {i:02}"
        if st.button(button_label):
            pdf_url = f"{base_url}{i:02}.pdf"
            st.write(f"Displaying PDF {i:02}")
            st.markdown(f'<iframe src="{pdf_url}" width="700" height="1000" type="application/pdf"></iframe>', unsafe_allow_html=True)
else:
    st.write("Please enter a base URL to display the PDFs.")
