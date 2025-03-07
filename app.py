import streamlit as st



st.set_page_config(page_title="E-LAMP", page_icon="static\images\MC_MIDNURSING_Logo.gif", layout="wide", initial_sidebar_state="collapsed")

with open( "static\styles.css" ) as css:
    st.markdown( f'<style>{css.read()}</style>' , unsafe_allow_html= True)

_, login_col, _ = st.columns([1,3,1])

with login_col:
    login_container = st.container(border=True)
    pic_col, form_col = login_container.columns([1,1])
    
    with pic_col:
        st.image(r"static\images\landing-img-pane.svg", use_container_width=True)
    
    with form_col:
        st.header("Research Publisher Login")
        st.markdown("Contribute to Mabini's growing knowledge repository.")
        login_form = st.form(key="login_form", border=False)
        with login_form:
            username = st.text_input("Username", placeholder="Publisher ID")
            password = st.text_input("Password", type="password", placeholder="Access key")
            st.form_submit_button("Login to Publish")
        st.markdown("---")
        st.markdown("Just here to explore? [Login as Guest](#)")