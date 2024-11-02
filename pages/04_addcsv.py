import streamlit as st
import pandas as pd

def combine_files(uploaded_files):
    combined_df = None
    for uploaded_file in uploaded_files:
        # Load the file depending on the extension
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file)
        else:
            st.error("Unsupported file format. Please upload CSV or Excel files.")
            return None
        
        # Merge or concatenate based on whether combined_df is initialized
        if combined_df is None:
            combined_df = df  # Initialize with the first file's data
        else:
            # Merge on common columns; you can specify a list of common columns to match on
            combined_columns = combined_df.columns.intersection(df.columns).tolist()
            combined_df = pd.merge(combined_df, df, on=combined_columns, how='outer')
    
    return combined_df

st.title('File Merger')

uploaded_files = st.file_uploader(
    "Choose files to merge (.csv or .xlsx)", 
    accept_multiple_files=True, 
    type=['csv', 'xlsx']
)

# Ensure there is at least one uploaded file
if uploaded_files:
    combined_df = combine_files(uploaded_files)
    # Check if the combination was successful and display or download the result
    if combined_df is not None:
        st.write(combined_df)
        csv = combined_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download combined file as CSV",
            data=csv,
            file_name='combined.csv',
            mime='text/csv',
        )
else:
    st.info("Please upload at least one CSV or Excel file.")
