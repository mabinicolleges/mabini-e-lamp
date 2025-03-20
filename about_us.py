import streamlit as st
from components.footer import display_footer  # Import the footer component

# Title and Project Description
st.title("About Us")
st.write("---")

# Group Members List
group_members = [
    {"name": "Dela Mata,  \nKatrina Cassandra P.", "image": r"static/images/about_us/dela_mata.png", "facebook": "https://www.facebook.com/share/1E4Nd41pQc/", "linkedin": "#"},
    {"name": "Dominguez,  \nBrein Lebron M.", "image": r"static\images\about_us\dominguez.png", "facebook": "https://www.facebook.com/share/191JYgG1qo/", "linkedin": "#"},
    {"name": "Eboña,  \nKyla L.", "image": r"static\images\about_us\eboña.png", "facebook": "https://www.facebook.com/share/15aucJZkXs/", "linkedin": "#"},
    {"name": "Echano,  \nSamantha Shane V.", "image": r"static\images\about_us\echano.png", "facebook": "https://www.facebook.com/share/15YnWcdq13/", "linkedin": "#"},
    {"name": "Espanto,  \nRyza Regina A.", "image": r"static\images\about_us\espanto.png", "facebook": "https://www.facebook.com/share/17eJ51YbS1/", "linkedin": "#"},
    {"name": "Estilles,  \nNecamae B.", "image": r"static\images\about_us\estilles.png", "facebook": "https://www.facebook.com/share/1A2JYf7MPK/", "linkedin": "#"},
    {"name": "Francisco,  \nDan Angelo R.", "image": r"static\images\about_us\francisco.png", "facebook": "https://www.facebook.com/share/1ALefGwrr7/", "linkedin": "#"},
    {"name": "Gaya,  \nPrincess Jannah V.", "image": r"static\images\about_us\gaya.png", "facebook": "https://www.facebook.com/share/163xwL7fDN/", "linkedin": "#"},
    {"name": "Gomez,  \nDaphne A.", "image": r"static\images\about_us\gomez.png", "facebook": "https://www.facebook.com/share/1FASbk6sxM/", "linkedin": "#"},
    {"name": "Goyal,  \nAshley R.", "image": r"static\images\about_us\goyal.png", "facebook": "https://www.facebook.com/share/1DkJv4Cdt9/", "linkedin": "#"},
]

# Developers List
developers = [
    {"name": "John Paul Curada", "role": "Developer - J&G Innovations", "image": r"static\images\about_us\curada.png", "facebook": "https://www.facebook.com/jp.curada.3", "linkedin": "https://www.linkedin.com/in/jpcurada/"},
    {"name": "Carlos Jerico Dela Torre", "role": "Developer", "image": r"static\images\about_us\dela_torre.png", "facebook": "https://www.facebook.com/2iLiTE", "linkedin": "https://www.linkedin.com/in/delatorrecj/"}
]

def display_members(members, show_linkedin=False):
    """Display a list of members in two columns."""
    # Create two columns for the entire layout
    main_cols = st.columns(2)
    
    for i, member in enumerate(members):
        with main_cols[i % 2]:
            # Create two columns for image and info within each member's section
            col1, col2 = st.columns([1, 2])
            
            with col1:
                # Display member image
                st.image(member["image"], width=10000)
            
            with col2:
                # Display name
                st.markdown(f"**{member['name']}**")
                
                # Display role if available
                if "role" in member:
                    st.markdown(f"{member['role']}")
                
                # Social media links with HTML to control image size
                st.markdown(f"""
                <a href="{member['facebook']}" target="_blank"><img src="https://cdn-icons-png.flaticon.com/512/733/733547.png" width="20"></a>
                {f'<a href="{member["linkedin"]}" target="_blank"><img src="https://cdn-icons-png.flaticon.com/512/174/174857.png" width="20"></a>' if show_linkedin and "linkedin" in member and member["linkedin"] != "#" else ""}
                """, unsafe_allow_html=True)
            
            # Add some space between members
            st.write("")

# Display Group Members
st.write("### Group 2 | Members")
display_members(group_members)

st.write("---")

# Display Developers
st.write("### Developers")
display_members(developers, show_linkedin=True)

# Footer
st.write("---")
st.write("_PROJECT IN NCM 110: NURSING INFORMATICS | BATCH 2024-2025  \n© 2025 Group 2 | E-lamp | All Rights Reserved_")

# Add the custom footer
display_footer()