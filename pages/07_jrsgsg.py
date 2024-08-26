import streamlit as st

st.title('View PDFs from 1 to 16')

# Create an input field for the base URL
base_url = st.text_input('Enter the base URL without the PDF number:')

# Ensure the base URL is entered
if base_url:
    # Generate URLs for PDFs numbered from 01 to 16
    pdf_urls = {f"{i:02}": f"{base_url}{i:02}.pdf" for i in range(1, 17)}

    # Create buttons for each PDF
    selected_pdf = st.selectbox("Select a PDF number:", options=list(pdf_urls.keys()), format_func=lambda x: f"PDF {x}")
    pdf_url = pdf_urls[selected_pdf]

    # Display the selected PDF
    if pdf_url:
        st.write(f"Displaying PDF {selected_pdf}")
        st.markdown(f'<iframe src="{pdf_url}" width="700" height="1000" type="application/pdf"></iframe>', unsafe_allow_html=True)
else:
    st.write("Please enter a base URL to display the PDFs.")
