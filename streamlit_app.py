import streamlit as st
import os
from services.auth_service import login_page

# Page configuration
st.set_page_config(page_title="E-LAMP", page_icon="static/images/MC_MIDNURSING_Logo.gif", layout="wide", initial_sidebar_state="collapsed")

# Load custom CSS
with open("static/styles.css") as css:
    st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)

login = st.Page(login_page, title="Login", icon="🔑")
admin = st.Page("interfaces/admin.py", title="Admin", icon="🏠", default=True)
visitor = st.Page("interfaces/visitor.py", title="Visitor", icon="📊")

# Set up navigation based on authentication status and authorization
if not st.experimental_user.is_logged_in or st.experimental_user.email not in st.secrets.allowed_users.emails:
    # Only show login page if not authenticated or not authorized
    pg = st.navigation([login, visitor], position="hidden")  # Include dashboard for visitor access
else:
    # Show all pages if authenticated and authorized
    pg = st.navigation([admin])

# Run the selected page
pg.run()