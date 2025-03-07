import streamlit as st
import services.sheets_service as ss

df = ss.get_data_df()
st.dataframe(df)