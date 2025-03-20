import streamlit as st
import time
from components.footer import display_footer

def login_page():
    # Check if authentication is required first
    if "auth_required" in st.session_state and st.session_state.auth_required:
        # Clear the flag to prevent infinite loops
        st.session_state.pop("auth_required")
        
        # Initiate Google login directly
        st.login()
        st.stop()

    if st.experimental_user.is_logged_in and st.experimental_user.email not in st.secrets.allowed_users.emails:
        st.error("Access denied. Your email is not authorized to access the admin area.")
        time.sleep(4)
        st.logout()
        st.stop()
    
    _, login_col, _ = st.columns([1, 3, 1])

    with login_col:
        login_container = st.container(border=False, key='login_container')
        pic_col, form_col = login_container.columns([1, 1])
        
        with pic_col:
            st.image("static/images/landing-img-pane.svg", use_container_width=True)
        
        with form_col:
            st.header("Welcome to E-LAMP")
            st.markdown("Contribute to Mabini's growing knowledge repository.")
            
            login_form = st.form(key="login_form", border=False)
            with login_form:
                username = st.text_input("Username", placeholder="Publisher ID")
                password = st.text_input("Password", type="password", placeholder="Access key")
                submit_button = st.form_submit_button("Login to Publish", use_container_width=True, type="primary")
                
            if submit_button:
                if username == "admin" and password == "mabini123":
                    show_google_login()
                else:
                    st.toast("Invalid credentials. Please try again.")
            
            st.divider()
            if st.button("Login as Visitor", use_container_width=True, type="primary"):
                st.switch_page("interfaces/visitor.py")  # Redirect to visitor/dashboard page
            st.caption("No publisher account yet? Contact the E-LAMP team to get started.")

        display_footer()

@st.dialog("Access Confirmation")
def show_google_login():
    st.write("To protect the integrity of the research papers of the institution, you need to log in to the college account to access admin account.")
    if st.button("Proceed with Google Login", type="primary"):
        # Set flag and close dialog
        st.session_state.auth_required = True
        st.rerun()