import streamlit as st

def display_footer():
    """
    Display a consistent footer across all pages that matches the design shown in the image.
    """
    
    # Footer HTML structure
    st.markdown("""
    <div class="footer-container">
        <div class="logo-container">
            <img src="app/static/images/logo/mabini-100-logo.png" alt="Nursing Logo">
            <img src="app/static/images/logo/mabini-1924-logo.png" alt="Mabini Logo">
            <img src="app/static/images/logo/mabini-logo.png" alt="College Logo">
            <img src="app/static/images/logo/nursing-logo.png" alt="CON Logo">
        </div>
        <div class="footer-title">THE MABINIAN E-LAMP</div>
        <div class="footer-subtitle">Research Management System</div>
        <div class="footer-college">Mabini Colleges Inc.</div>
        <div class="footer-links">
            <a href="/about_us">About Us</a>
            <a href="/privacy_policy">Privacy Policy</a>
            <a href="/guide">Guide</a>
        </div>
        <div class="footer-copyright">©Mabini Colleges Inc. | The Mabinian E-Lamp Research Management System | All Rights Reserved</div>
    </div>
    """, unsafe_allow_html=True)