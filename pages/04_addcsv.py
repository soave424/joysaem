import streamlit as st
import pandas as pd

def combine_files(uploaded_files):
    combined_df = pd.DataFrame()
    for uploaded_file in uploaded_files:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file)
        else:
            st.error("Unsupported file format. Please upload CSV or Excel files.")
            return None
        combined_df = pd.concat([combined_df, df], ignore_index=True)
    return combined_df

st.title('File Merger')

uploaded_files = st.file_uploader("Choose files to merge (.csv or .xlsx)", accept_multiple_files=True, type=['csv', 'xlsx'])

if uploaded_files:
    combined_df = combine_files(uploaded_files)
    if combined_df is not None:
        st.write(combined_df)
        csv = combined_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download combined file as CSV",
            data=csv,
            file_name='combined.csv',
            mime='text/csv',
        )
