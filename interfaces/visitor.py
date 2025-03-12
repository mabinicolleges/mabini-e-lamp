import streamlit as st
from services import sheets_service as ss
from services import drive_service as ds

# App title with description
st.title("Research Database")
st.caption("Browse, filter, and access research papers from our collection")
st.markdown("---")

# Load data from Google Sheets
@st.cache_data
def load_research_data():
    """Load and cache research data to improve performance"""
    return ss.get_data_ls_dict("research_data")

research_data = load_research_data()

# Initialize session state variables
if 'filtered_data' not in st.session_state:
    st.session_state.filtered_data = research_data
if 'page_num' not in st.session_state:
    st.session_state.page_num = 0

# Extract year data for filtering
years = [int(item['created_year']) for item in research_data 
         if (isinstance(item.get('created_year', ''), str) and item['created_year'].isdigit()) 
         or isinstance(item.get('created_year', ''), int)]
min_year = min(years) if years else 2000
max_year = max(years) if years else 2023

# Initialize year range in session state
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
    st.header("Search & Filters")
    st.caption("Narrow down research results using the options below")
    
    with st.form(key="filter_form"):
        # Search bar
        input_search_bar = st.text_input(
            label="Search", 
            placeholder="Enter keywords, title, or author name"
        )
        st.caption("Search across titles, abstracts, and author names")
        
        # Category selection
        categories = sorted(list(set(item['category'] for item in research_data if 'category' in item)))
        input_category_bar = st.multiselect(
            label="Categories", 
            options=categories,
            placeholder="Select one or more categories"
        )
        
        # Keywords input
        input_keywords_bar = st.text_input(
            label="Keywords", 
            placeholder="e.g., machine learning, climate, healthcare"
        )
        st.caption("Enter comma-separated keywords")
        
        # Year range slider
        year_range = st.slider(
            "Publication Year",
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
    
    # Help information
    with st.expander("How to use filters"):
        st.markdown("""
        - **Search**: Find papers by title, abstract content, or author name
        - **Categories**: Select specific research categories
        - **Keywords**: Enter comma-separated keywords to match paper topics
        - **Year Range**: Limit results to specific publication years
        """)
    
    # Logout button at bottom of sidebar
    st.sidebar.markdown("---")
    st.sidebar.button("Log out", key="logout", on_click=st.logout, use_container_width=True)

# Main content area
filtered_data = st.session_state.filtered_data

# Pagination setup
items_per_page = 10
total_items = len(filtered_data)
total_pages = max(1, (total_items + items_per_page - 1) // items_per_page)

# Ensure page_num is valid
st.session_state.page_num = min(st.session_state.page_num, total_pages - 1)
st.session_state.page_num = max(0, st.session_state.page_num)

# Calculate start and end indices for current page
start_idx = st.session_state.page_num * items_per_page
end_idx = min(start_idx + items_per_page, total_items)

# Results summary
st.write(f"Showing {total_items} results")
if total_items == 0:
    st.info("No research papers match your current filters. Try adjusting your search criteria.")

# Display research items in cards
for i in range(start_idx, end_idx):
    if i < len(filtered_data):
        research = filtered_data[i]
        with st.container(border=True):
            # Paper title and category
            st.markdown(f"##### {research['title']}")
            st.caption(f"**Category:** {research.get('category', 'Uncategorized')}")
            
            # Create columns for metadata and actions
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                st.markdown(f"**Author:** {research.get('author_name', 'Unknown')}")
                st.markdown(f"**Year:** {research.get('created_year', 'Unknown')}")
            
            with col2:
                # Abstract preview (first 100 characters)
                abstract_preview = research.get('abstract', 'No abstract available')
                if len(abstract_preview) > 100:
                    abstract_preview = abstract_preview[:100] + "..."
                st.markdown(f"**Abstract:** {abstract_preview}")
            
            with col3:
                # Action buttons
                st.link_button("View PDF", url=research['file_url'], use_container_width=True)
                
                with st.popover("Cite", use_container_width=True):
                    tab1, tab2 = st.tabs(["APA", "MLA"])
                    with tab1:
                        citation = f"{research.get('author_name', 'Author, A.')} ({research.get('created_year', 'n.d.')}). {research['title']}."
                        st.code(citation, language=None)
                        st.button("Copy", key=f"copy_apa_{i}", use_container_width=True)
                    with tab2:
                        citation = f"{research.get('author_name', 'Author, A.')}. \"{research['title']}.\" {research.get('created_year', 'n.d.')}."
                        st.code(citation, language=None)
                        st.button("Copy", key=f"copy_mla_{i}", use_container_width=True)
            
            # Full abstract in an expander
            with st.expander("View full abstract"):
                st.write(research.get('abstract', 'No abstract available'))

# Pagination controls
if total_pages > 1:
    st.markdown("---")
    
    # Create pagination layout
    pagination_cols = st.columns([1, 1, 3, 1, 1])
    
    with pagination_cols[0]:
        if st.session_state.page_num > 0:
            if st.button("First", use_container_width=True):
                st.session_state.page_num = 0
                st.rerun()
    
    with pagination_cols[1]:
        if st.session_state.page_num > 0:
            if st.button("Previous", use_container_width=True):
                st.session_state.page_num -= 1
                st.rerun()
    
    with pagination_cols[2]:
        st.markdown(f"<div style='text-align: center'>Page {st.session_state.page_num + 1} of {total_pages}</div>", unsafe_allow_html=True)
    
    with pagination_cols[3]:
        if st.session_state.page_num < total_pages - 1:
            if st.button("Next", use_container_width=True):
                st.session_state.page_num += 1
                st.rerun()
    
    with pagination_cols[4]:
        if st.session_state.page_num < total_pages - 1:
            if st.button("Last", use_container_width=True):
                st.session_state.page_num = total_pages - 1
                st.rerun()