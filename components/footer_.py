import streamlit as st


def display_footer():
    """
    Display a consistent footer across all pages.
    """
    with st.container(key="feed_container"):
        st.markdown("---")
        
        footer_col1, footer_col2, footer_col3 = st.columns(3)
        
        with footer_col1:
            st.image("static/images/MC_MIDNURSING_Logo.gif", width=100)
        
        with footer_col2:
            st.markdown("### E-LAMP")
            st.markdown("Research Management System")
            st.markdown("Mabini Colleges")
        
        with footer_col3:
            st.markdown("**Quick Links**")
            st.markdown("[About Us](/about_us)")  
        
        st.markdown("<div style='text-align: center; color: #888; padding: 20px 0 10px;'>© 2025 Mabini Colleges | E-LAMP Research Management System | All Rights Reserved</div>", unsafe_allow_html=True)