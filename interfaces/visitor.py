import streamlit as st
from services import sheets_service as ss

st.title("Visitor Page")

# Load data from Google Sheets
research_data = ss.get_data_ls_dict("research_data")
st.dataframe(research_data)

st.button("Log out", on_click=st.logout)