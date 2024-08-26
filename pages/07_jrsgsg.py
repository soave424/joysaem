import streamlit as st

st.title('View PDF')

# Create an input field for the URL
pdf_url = st.text_input('Enter the PDF URL')

# Check if a URL has been entered and display it
if pdf_url:
    # Embed the PDF in an iframe within the Streamlit app
    st.markdown(f'<iframe src="{pdf_url}" width="700" height="1000" type="application/pdf"></iframe>', unsafe_allow_html=True)
else:
    st.write("Please enter a URL to display the PDF.")
