import streamlit as st
from components.footer import display_footer


_, feed_col, _ = st.columns([1, 8, 1])

with feed_col:
    with st.container(key="feed_container"):
        # Header section
        st.markdown("<h1 class='page-title'>Meet Our Team</h1>", unsafe_allow_html=True)
        st.markdown("<p class='page-subtitle'>The dedicated minds behind E-LAMP Research Management System</p>", unsafe_allow_html=True)

        st.header("About E-LAMP")
        st.markdown("""
        <div class='about-content'>
        E-LAMP (Electronic Library and Management Platform) is the official online Research Journal of Mabini Colleges, Inc.—College of Nursing. 
        This comprehensive platform serves as a centralized repository for academic research papers, enabling easy publishing, browsing, and 
        downloading of scholarly work conducted by nursing students.
        
        <p>This initiative aims to foster a culture of scientific inquiry, critical thinking, and innovation among nursing students. 
        It provides an avenue for disseminating research findings that address various healthcare challenges, improve patient care, 
        and support the continuous development of the nursing profession.</p>
        
        <p>This is a project of BSN 2-B Group 2 in the subject NCM 110: Nursing Informatics under Mr. Art Z. Tribunal, RN, LPT.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            #### Established
            March 21, 2025
            """)
        
        with col2:
            st.markdown("""
            #### Institution
            Mabini Colleges, Inc. -- College of Nursing
            """)
        
        st.markdown("</div>", unsafe_allow_html=True)

        # Group Members List
        group_members = [
            {"name": "Goyal, Ashley R.", "role": "Team Leader", "image": "app/static/images/about_us/goyal.png", "facebook": "https://www.facebook.com/ashleyrafer.goya/", "linkedin": "https://www.linkedin.com/", "is_leader": True},
            {"name": "Dela Mata, Katrina Cassandra P.", "image": "app/static/images/about_us/dela_mata.png", "facebook": "https://www.facebook.com/profile.php?id=100091580852393/", "linkedin": "https://www.linkedin.com/", "is_leader": False},
            {"name": "Dominguez, Brein Lebron M.", "image": "app/static/images/about_us/dominguez.png", "facebook": "https://www.facebook.com/moygeorgeee/", "linkedin": "https://www.linkedin.com/", "is_leader": False},
            {"name": "Eboña, Kyla L.", "image": "app/static/images/about_us/eboña.png", "facebook": "https://www.facebook.com/xyza.kai/", "linkedin": "https://www.linkedin.com/", "is_leader": False},
            {"name": "Echano, Samantha Shane V.", "image": "app/static/images/about_us/echano.png", "facebook": "https://www.facebook.com/smntshane.echano/", "linkedin": "https://www.linkedin.com/", "is_leader": False},
            {"name": "Espanto, Ryza Regina A.", "image": "app/static/images/about_us/espanto.png", "facebook": "https://www.facebook.com/RyzaEspanto/", "linkedin": "https://www.linkedin.com/", "is_leader": False},
            {"name": "Estilles, Necamae B.", "image": "app/static/images/about_us/estilles.png", "facebook": "https://www.facebook.com/necamae.estilles/", "linkedin": "https://www.linkedin.com/", "is_leader": False},
            {"name": "Francisco, Dan Angelo R.", "image": "app/static/images/about_us/francisco.png", "facebook": "https://www.facebook.com/danfrancisco57/", "linkedin": "https://www.linkedin.com/", "is_leader": False},
            {"name": "Gaya, Princess Jannah V.", "image": "app/static/images/about_us/gaya.png", "facebook": "https://www.facebook.com/wwamim/", "linkedin": "https://www.linkedin.com/", "is_leader": False},
            {"name": "Gomez, Daphne A.", "image": "app/static/images/about_us/gomez.png", "facebook": "https://www.facebook.com/daphne.gomez.773/", "linkedin": "https://www.linkedin.com/", "is_leader": False},
        ]

        # Developers List
        developers = [
            {"name": "John Paul Curada", "role": "Lead Developer - J&G Innovations", "image": "app/static/images/about_us/curada.png", "facebook": "https://www.facebook.com/jp.curada.3", "linkedin": "https://www.linkedin.com/in/jpcurada/", "is_leader": True},
            {"name": "Carlos Jerico Dela Torre", "role": "Developer", "image": "app/static/images/about_us/dela_torre.png", "facebook": "https://www.facebook.com/2iLiTE", "linkedin": "https://www.linkedin.com/in/delatorrecj/", "is_leader": False},
        ]

        def display_member_card(member, is_centered=False):
            """Display a styled card for each team member."""
            leader_class = "leader-card" if member.get("is_leader", False) else ""
            centered_style = "text-align: center;" if is_centered else ""
            
            st.markdown(f"""
            <div class="member-card {leader_class}" style="{centered_style}">
                <div class="member-image">
                    <img src="{member['image']}" alt="{member['name']}">
                </div>
                <div class="member-name">{member['name']}</div>
                {f'<div class="member-role">{member["role"]}</div>' if "role" in member else ''}
            </div>
            """, unsafe_allow_html=True)

        # Display Student Team
        st.markdown("<div class='team-header'><h2>Group 2 Nursing Informatics</h2></div>", unsafe_allow_html=True)
        
        # Find the team leader
        leader = next((m for m in group_members if m.get("is_leader", False)), None)
        non_leaders = [m for m in group_members if not m.get("is_leader", False)]
        
        # Display the team in a grid with 3 columns, with leader in middle of first row
        cols_per_row = 3
        
        # First row with Ashley Goyal in middle position (2nd column)
        first_row = st.columns(cols_per_row)
        
        # First column of first row will be empty/blank
        
        # Place leader in middle column (2nd column)
        with first_row[1]:
            if leader:
                display_member_card(leader)
        
        # Third column of first row will be empty/blank
                
        # All non-leaders start in second row
        remaining_members = non_leaders
        
        # Create rows with 3 members each
        for i in range(0, len(remaining_members), cols_per_row):
            row_members = remaining_members[i:i+cols_per_row]
            cols = st.columns(cols_per_row)
            
            for j, member in enumerate(row_members):
                with cols[j]:
                    display_member_card(member)

        st.markdown("<hr>", unsafe_allow_html=True)

        # Display Development Team
        st.header("Development Team")
        
        # Display developers in 2 columns
        dev_cols = st.columns(2)
        for i, developer in enumerate(developers):
            with dev_cols[i]:
                display_member_card(developer)
        
        st.markdown("<hr>", unsafe_allow_html=True)
        st.header("Contact Us")
        st.markdown("""
        <div class='about-content'>
            If you have any inquiries, suggestions, or need assistance with The Mabinian E-Lamp, we are here to help. Don’t hesitate to reach out to us anytime, and our team will be happy to assist you. Your insights and concerns are always welcome as we strive to improve and provide the best experience possible. 
                    
            General Support 
            Email: mabinicolleges.con@gmail.com 
            Phone: +63 (994) 436-2980 
        </div>
        """, unsafe_allow_html=True)

    # Add the custom footer
    display_footer()