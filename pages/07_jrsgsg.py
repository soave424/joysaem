import streamlit as st
import requests
from datetime import datetime

st.title('View PDFs')

# Custom CSS to style buttons
st.markdown("""
    <style>
    .stButton > button {
        color: black;
        border: 1px solid #d3d3d3;
        padding: 8px 16px;
        margin: 2px;
    }
    .stButton > button.displayed {
        background-color: red;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# 기본 URL 템플릿
url_template = "https://jrsgsg.hankyung.com/js/pdfjs/web/viewer.html?file=/pdfdata/{year}/{month}/{day}/{date}_0110_010"

# 날짜 선택 위젯
selected_date = st.date_input('날짜를 선택하세요', value=datetime.today())

# 선택한 날짜를 기반으로 URL 생성
formatted_date = selected_date.strftime('%Y%m%d')
year = selected_date.strftime('%Y')
month = selected_date.strftime('%m')
day = selected_date.strftime('%d')

# 최종 URL 생성
base_url = url_template.format(year=year, month=month, day=day, date=formatted_date)

# Initialize session state to keep track of displayed PDFs
if 'show_pdf' not in st.session_state:
    st.session_state['show_pdf'] = {i: False for i in range(1, 17)}

# Function to toggle all PDFs
def toggle_all(show):
    for i in range(1, 17):
        st.session_state['show_pdf'][i] = show

# Create columns for buttons to align them horizontally, plus one for "All" button
cols = st.columns(17)
with cols[0]:
    all_button_label = "All"
    if st.button(all_button_label):
        all_visible = all(st.session_state['show_pdf'].values())
        toggle_all(not all_visible)

for i in range(1, 17):
    with cols[i]:
        button_label = f"{i:02}"
        if st.button(button_label, key=f"btn_{i}"):
            st.session_state['show_pdf'][i] = not st.session_state['show_pdf'][i]
            
            # Add or remove the "displayed" class using JavaScript based on the state
            st.markdown(f"""
                <script>
                var btn = window.parent.document.querySelectorAll('button[key="btn_{i}"]')[0];
                if ({str(st.session_state['show_pdf'][i]).lower()}) {{
                    btn.classList.add("displayed");
                }} else {{
                    btn.classList.remove("displayed");
                }}
                </script>
                """, unsafe_allow_html=True)

# Display PDFs based on button clicks
for i in range(1, 17):
    if st.session_state['show_pdf'][i]:
        pdf_url = f"{base_url}{i:02}.pdf"
        st.markdown(f'<iframe src="{pdf_url}" width="700" height="1000" type="application/pdf"></iframe>', unsafe_allow_html=True)