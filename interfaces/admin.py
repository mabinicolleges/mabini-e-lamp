import streamlit as st
import services.sheets_service as ss
import services.drive_service as ds
import pandas as pd
import os
from datetime import datetime
import uuid

# home.py
import streamlit as st



st.header("Research Publisher Dashboard")
# Load data from Google Sheets
research_data = ss.get_data_df("research_data")
st.dataframe(research_data)

st.button("Log out", on_click=st.logout)