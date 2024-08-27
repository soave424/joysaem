import streamlit as st
import json

st.title("JSON File Viewer")

# File uploader for JSON files
uploaded_file = st.file_uploader("Upload a JSON file", type=["json"])

if uploaded_file is not None:
    try:
        # Read and parse the JSON file
        json_data = json.load(uploaded_file)
        
        # Display the JSON data
        st.write("### JSON Content:")
        st.json(json_data)
        
    except json.JSONDecodeError:
        st.error("The file is not a valid JSON file.")
else:
    st.info("Please upload a JSON file to view its content.")
