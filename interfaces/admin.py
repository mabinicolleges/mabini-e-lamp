import streamlit as st
from services import sheets_service as ss
from services import drive_service as ds
import time

# Main header
st.title("Admin Dashboard")
st.caption("Manage research papers and upload new content to the database")
st.markdown("---")

# Load data from Google Sheets
@st.cache_data # Cache data for 5 minutes
def load_research_data():
    """Load and cache research data to improve performance"""
    return ss.get_data_ls_dict("research_data")

research_data = load_research_data()

# Define the upload dialog function with improved UI
@st.dialog("Upload New Paper", width="large")
def upload_paper_dialog():
    st.subheader("Add New Research Paper")
    st.caption("Fill in all fields to publish a new research paper to the database")
    
    # Create two columns for better form layout
    col1, col2 = st.columns(2)
    
    with col1:
        # Basic paper information
        title = st.text_input("Title", placeholder="Enter paper title")
        author_name = st.text_input("Author Name", placeholder="Enter author's full name")
        
        # Get existing categories for dropdown
        existing_categories = sorted(list(set(item['category'] for item in research_data if 'category' in item)))
        category_options = existing_categories if existing_categories else ["Category 1", "Category 2", "Category 3"]
        
        category = st.selectbox("Category", category_options)
        created_year = st.number_input("Year Published", min_value=1900, max_value=2100, value=2023)
        keywords = st.text_input("Keywords (comma separated)", placeholder="e.g., machine learning, climate, healthcare")
        st.caption("Keywords help users find this paper when searching")
    
    with col2:
        # Abstract and file uploads
        abstract = st.text_area("Abstract", placeholder="Enter paper abstract", height=150)
        
        st.markdown("### Upload Files")
        author_img_file = st.file_uploader("Author Image", type=["jpg", "jpeg", "png"])
        st.caption("Author image should be square format for best display")
        
        paper_file = st.file_uploader("Paper File (PDF)", type=["pdf"])
        st.caption("Maximum file size: 50MB")
    
    # Validation and submission
    st.markdown("---")
    
    # Create columns for buttons
    button_col1, button_col2 = st.columns([1, 3])
    
    with button_col1:
        publish_button = st.button("Publish Paper", type="primary", use_container_width=True)
    
    # Validation message area
    message_container = st.empty()
    
    if publish_button:
        # Validate all fields are filled
        missing_fields = []
        if not title: missing_fields.append("Title")
        if not abstract: missing_fields.append("Abstract")
        if not author_name: missing_fields.append("Author Name")
        if not author_img_file: missing_fields.append("Author Image")
        if not paper_file: missing_fields.append("Paper File")
        if not keywords: missing_fields.append("Keywords")
        
        if missing_fields:
            message_container.error(f"Please fill in all required fields: {', '.join(missing_fields)}")
        else:
            try:
                with st.spinner("Publishing paper..."):
                    # Upload files to Google Drive
                    author_img_url = ds.upload_img(author_img_file)
                    file_url = ds.upload_pdf(paper_file)
                    
                    # Add the new paper
                    ss.post_add_new_paper(
                        title=title,
                        abstract=abstract,
                        author_name=author_name,
                        author_img_url=author_img_url,
                        category=category,
                        created_year=created_year,
                        keywords=keywords,
                        file_url=file_url
                    )
                
                # Show success message
                st.toast("Paper published successfully!", icon="✅")
                time.sleep(1)  # Brief pause to show the toast
                st.rerun()  # Refresh the page
                
            except Exception as e:
                message_container.error(f"Error publishing paper: {str(e)}")

# Admin actions section
st.subheader("Admin Actions")
st.caption("Upload new papers to the research database")

admin_cols = st.columns(2)
with admin_cols[0]:
    # Upload button to trigger the dialog
    if st.button("📄 Upload New Paper", type="primary", use_container_width=True):
        upload_paper_dialog()

with admin_cols[1]:
    # Refresh data button
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# Initialize session state for filters
if 'filtered_data' not in st.session_state:
    st.session_state.filtered_data = research_data
if 'page_num' not in st.session_state:
    st.session_state.page_num = 0

# Get min and max years from data for the slider
years = [int(item['created_year']) for item in research_data 
         if (isinstance(item.get('created_year', ''), str) and item['created_year'].isdigit()) 
         or isinstance(item.get('created_year', ''), int)]
min_year = min(years) if years else 2000
max_year = max(years) if years else 2023

# Initialize year range in session state if not present
if 'year_range' not in st.session_state:
    st.session_state.year_range = (min_year, max_year)

# Function to apply filters
def apply_filters(search_text, categories, keywords, year_range):
    """Filter research data based on user-selected criteria"""
    filtered = research_data.copy()
    
    # Apply search filter
    if search_text:
        filtered = [item for item in filtered if search_text.lower() in item['title'].lower() 
                   or search_text.lower() in item['abstract'].lower() 
                   or search_text.lower() in item['author_name'].lower()]
    
    # Apply category filter
    if categories:
        filtered = [item for item in filtered if item['category'] in categories]
    
    # Apply keywords filter
    if keywords:
        keyword_list = [k.strip().lower() for k in keywords.split(',')]
        filtered = [item for item in filtered if any(k in item.get('keywords', '').lower() for k in keyword_list)]
    
    # Apply year range filter
    year_min, year_max = year_range
    filtered = [item for item in filtered if (
        # Check if it's a string and contains digits
        isinstance(item.get('created_year', ''), str) and item['created_year'].isdigit() and 
        year_min <= int(item['created_year']) <= year_max
    ) or (
        # Or if it's already an integer
        isinstance(item.get('created_year', 0), int) and 
        year_min <= item['created_year'] <= year_max
    )]
        
    return filtered

# Sidebar for filters
with st.sidebar:
    st.header("Filter Research Papers")
    st.caption("Use these filters to find specific papers in the database")
    
    with st.form(key="filter_form"):
        # Search bar
        input_search_bar = st.text_input(
            label="Search", 
            placeholder="Enter title, author, or keywords"
        )
        
        # Get unique categories
        categories = sorted(list(set(item['category'] for item in research_data if 'category' in item)))
        input_category_bar = st.multiselect(
            label="Categories", 
            options=categories,
            placeholder="Select categories"
        )
        
        input_keywords_bar = st.text_input(
            label="Keywords", 
            placeholder="Enter comma separated keywords"
        )
        
        # Add year range slider
        year_range = st.slider(
            "Publication Year Range",
            min_value=min_year,
            max_value=max_year,
            value=(min_year, max_year),
            step=1
        )
        
        # Apply filters button
        filter_button = st.form_submit_button(
            label="Apply Filters", 
            type="primary",
            use_container_width=True
        )
        
        if filter_button:
            st.session_state.filtered_data = apply_filters(
                input_search_bar, 
                input_category_bar, 
                input_keywords_bar, 
                year_range
            )
            st.session_state.page_num = 0  # Reset to first page
        
        st.caption("Filters apply to all papers in the database")
    
    # Admin help section
    with st.expander("Admin Help"):
        st.markdown("""
        **Quick Tips:**
        - Use the search to find papers by title, author, or content
        - Filter by category to organize your view
        - Upload new papers using the button at the top
        - Use the refresh button to update the database view
        """)
    
    # Add logout button to sidebar bottom
    st.sidebar.markdown("---")
    st.sidebar.button("Log out", key="logout", on_click=st.logout, use_container_width=True)

# Research papers section
st.subheader("Research Papers Database")
st.caption("View all papers in the database")

# Main content area
filtered_data = st.session_state.filtered_data

# Pagination setup
items_per_page = 10
total_items = len(filtered_data)
total_pages = max(1, (total_items + items_per_page - 1) // items_per_page)  # Ceiling division

# Ensure page_num is valid
st.session_state.page_num = min(st.session_state.page_num, total_pages - 1)
st.session_state.page_num = max(0, st.session_state.page_num)

# Calculate start and end indices for current page
start_idx = st.session_state.page_num * items_per_page
end_idx = min(start_idx + items_per_page, total_items)

# Show results count
st.write(f"Showing {total_items} papers in the database")

if total_items == 0:
    st.info("No papers found.")

# Display research items in cards
for i in range(start_idx, end_idx):
    if i < len(filtered_data):
        research = filtered_data[i]
        with st.container(border=True):
            # Paper header with title
            st.markdown(f"##### {research['title']}")
            st.caption(f"**Category:** {research.get('category', 'Uncategorized')}")
            
            # Paper details in two columns
            info_col, preview_col = st.columns([1, 2])
            
            with info_col:
                st.markdown(f"**Author:** {research.get('author_name', 'Unknown')}")
                st.markdown(f"**Year:** {research.get('created_year', 'Unknown')}")
                st.markdown(f"**Keywords:** {research.get('keywords', 'None')}")
                
                # View PDF button
                if 'file_url' in research:
                    st.link_button("📄 View PDF", url=research['file_url'], use_container_width=True)
            
            with preview_col:
                # Abstract preview with expandable full view
                abstract = research.get('abstract', 'No abstract available')
                preview_length = min(200, len(abstract))
                
                st.markdown("**Abstract Preview:**")
                st.markdown(f"{abstract[:preview_length]}{'...' if len(abstract) > preview_length else ''}")
                
                with st.expander("View Full Abstract"):
                    st.write(abstract)

# Pagination controls with better styling
if total_pages > 1:
    st.markdown("---")
    pagination_cols = st.columns([1, 1, 3, 1, 1])

    with pagination_cols[0]:
        if st.session_state.page_num > 0:
            if st.button("First", use_container_width=True, type="primary"):
                st.session_state.page_num = 0
                st.rerun()

    with pagination_cols[1]:
        if st.session_state.page_num > 0:
            if st.button("Previous", use_container_width=True, type="primary"):
                st.session_state.page_num -= 1
                st.rerun()

    with pagination_cols[2]:
        st.markdown(f"<div style='text-align: center'>Page {st.session_state.page_num + 1} of {total_pages}</div>", unsafe_allow_html=True)

    with pagination_cols[3]:
        if st.session_state.page_num < total_pages - 1:
            if st.button("Next", use_container_width=True, type="primary"):
                st.session_state.page_num += 1
                st.rerun()

    with pagination_cols[4]:
        if st.session_state.page_num < total_pages - 1:
            if st.button("Last", use_container_width=True, type="primary"):
                st.session_state.page_num = total_pages - 1
                st.rerun()

# Footer with admin information
st.markdown("---")
st.caption("Admin Dashboard | Research Database Management System")