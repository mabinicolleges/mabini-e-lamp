import streamlit as st
from services import sheets_service as ss
from services import drive_service as ds
from fuzzywuzzy import fuzz
import pandas as pd
import requests
import re

# Load and cache data with preprocessing
@st.cache_data
def load_research_data():
    """Load and cache research data with preprocessing for faster searching"""
    data = ss.get_data_ls_dict("research_data")
    df = pd.DataFrame(data)
    
    def preprocess_text(text):
        return str(text).lower().strip()
    
    df['search_field'] = (
        df['title'].apply(preprocess_text) + ' ' +
        df['author_name'].apply(preprocess_text) + ' ' +
        df['keywords'].apply(preprocess_text)
    )
    
    df['created_year'] = pd.to_numeric(df['created_year'], errors='coerce')
    return df

# Function to fetch image from Google Drive link
@st.cache_data
def fetch_image_from_gdrive(gdrive_url):
    try:
        match = re.search(r"/d/([a-zA-Z0-9_-]+)", gdrive_url)
        if not match:
            return None
        file_id = match.group(1)
        direct_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        response = requests.get(direct_url, stream=True)
        if response.status_code == 200:
            return response.content
        return None
    except Exception as e:
        st.warning(f"Error fetching image: {e}")
        return None

# Define the author details dialog
@st.dialog("Author Details", width="large")
def show_author_details(author_name, author_img_url, created_research):
    col1, col2 = st.columns([1, 2])
    with col1:
        if author_img_url and "drive.google.com" in author_img_url:
            image_data = fetch_image_from_gdrive(author_img_url)
            if image_data:
                st.image(image_data, width=200)
            else:
                st.image("https://via.placeholder.com/200", caption="Image not available", width=200)
        else:
            st.image("https://via.placeholder.com/200", caption="No image provided", width=200)
    with col2:
        st.subheader(author_name)
        st.write("### Research Papers")
        for research in created_research:
            st.write(f"- {research}")

# Sorting function
def sort_data(df, sort_option):
    """Sort the DataFrame based on selected option"""
    if sort_option == "Alphabetical (A-Z)":
        return df.sort_values('title')
    elif sort_option == "Alphabetical (Z-A)":
        return df.sort_values('title', ascending=False)
    elif sort_option == "Year (Newest First)":
        return df.sort_values('created_year', ascending=False, na_position='last')
    elif sort_option == "Year (Oldest First)":
        return df.sort_values('created_year', na_position='last')
    return df  # Default case returns unsorted

# Initialize data
research_df = load_research_data()

# Initialize session state
if 'filtered_data' not in st.session_state:
    st.session_state.filtered_data = research_df
if 'page_num' not in st.session_state:
    st.session_state.page_num = 0
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""
if 'sort_option' not in st.session_state:
    st.session_state.sort_option = "Relevance"  # Default sort

# Extract year data for filtering
years = research_df['created_year'].dropna()
min_year = int(years.min()) if not years.empty else 2000
max_year = int(years.max()) if not years.empty else 2023
if min_year == max_year:
    max_year = min_year + 1
if 'year_range' not in st.session_state:
    st.session_state.year_range = (min_year, max_year)

# Optimized filtering function
def apply_filters(df, categories, keywords, year_range):
    """Filter research data using pandas for better performance"""
    filtered_df = df.copy()
    if categories:
        filtered_df = filtered_df[filtered_df['category'].isin(categories)]
    if keywords:
        keyword_list = [k.strip().lower() for k in keywords.split(',')]
        mask = filtered_df['keywords'].str.lower().apply(
            lambda x: any(k in x for k in keyword_list)
        )
        filtered_df = filtered_df[mask]
    year_min, year_max = year_range
    filtered_df = filtered_df[
        (filtered_df['created_year'] >= year_min) & 
        (filtered_df['created_year'] <= year_max)
    ]
    return filtered_df

# Optimized search function
def search_data(df, query, threshold=70):
    if not query:
        return df
    query = query.lower().strip()
    exact_mask = df['search_field'].str.contains(query, na=False)
    exact_matches = df[exact_mask]
    if len(exact_matches) >= 10:
        return exact_matches
    df['match_score'] = df['search_field'].apply(
        lambda x: fuzz.partial_ratio(query, x)
    )
    fuzzy_matches = df[df['match_score'] >= threshold].sort_values(
        'match_score', ascending=False
    )
    return fuzzy_matches.drop(columns=['match_score'])

def update_search():
    st.session_state.filtered_data = search_data(
        apply_filters(
            research_df,
            input_category_bar, 
            input_keywords_bar, 
            year_range
        ), 
        st.session_state.search_input
    )
    st.session_state.search_query = st.session_state.search_input
    st.session_state.page_num = 0

# Sidebar for filters
with st.sidebar:
    st.header("Search & Filters")
    st.caption("Narrow down research results using the options below")
    
    with st.form(key="filter_form"):
        categories = sorted(research_df['category'].dropna().unique())
        input_category_bar = st.multiselect(
            label="Categories", 
            options=categories,
            placeholder="Select one or more categories"
        )
        input_keywords_bar = st.text_input(
            label="Keywords", 
            placeholder="e.g., machine learning, climate, healthcare"
        )
        st.caption("Enter comma-separated keywords")
        year_range = st.slider(
            "Publication Year",
            min_value=min_year,
            max_value=max_year,
            value=(min_year, max_year),
            step=2,
            key="year_range"
        )
        filter_button = st.form_submit_button(
            label="Apply Filters", 
            type="primary",
            use_container_width=True
        )
        if filter_button:
            st.session_state.filtered_data = apply_filters(
                research_df,
                input_category_bar, 
                input_keywords_bar, 
                year_range
            )
            st.session_state.page_num = 0

    with st.expander("How to use filters"):
        st.markdown("""
        - **Search**: Find papers by title, abstract content, or author name
        - **Categories**: Select specific research categories
        - **Keywords**: Enter comma-separated keywords to match paper topics
        - **Year Range**: Limit results to specific publication years
        """)
    
    st.sidebar.markdown("---")
    st.sidebar.button("Log out", key="logout", on_click=st.logout, use_container_width=True)

# Main content area
_, feed_col, _ = st.columns([1, 8, 1])
with feed_col:
    st.image(r"static/images/visitor-header.svg", use_container_width=True)
    st.markdown("""
    <style>
    [data-testid="stTextInput"] {
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    search_bar_col, sort_col = st.columns([10, 1], vertical_alignment='center')
    search_query = search_bar_col.text_input(
        "Search", 
        placeholder="Enter keywords, title, or author name",
        key="search_input",
        value=st.session_state.search_query,
        on_change=update_search,
    )
    with sort_col.popover("Sort"):
        sort_options = [
            "Relevance",
            "Alphabetical (A-Z)",
            "Alphabetical (Z-A)",
            "Year (Newest First)",
            "Year (Oldest First)"
        ]
        selected_sort = st.radio(
            "Sort by:",
            sort_options,
            index=sort_options.index(st.session_state.sort_option),
            key="sort_radio"
        )
        if selected_sort != st.session_state.sort_option:
            st.session_state.sort_option = selected_sort
            st.rerun()

    # Apply search when query changes
    if search_query != st.session_state.search_query:
        st.session_state.search_query = search_query
        filtered_by_criteria = apply_filters(
            research_df,
            input_category_bar, 
            input_keywords_bar, 
            year_range
        )
        st.session_state.filtered_data = search_data(filtered_by_criteria, search_query)
        st.session_state.page_num = 0

    # Apply sorting to filtered data
    filtered_data = sort_data(st.session_state.filtered_data, st.session_state.sort_option)
    
    # Pagination setup
    items_per_page = 10
    total_items = len(filtered_data)
    total_pages = max(1, (total_items + items_per_page - 1) // items_per_page)
    st.session_state.page_num = min(st.session_state.page_num, total_pages - 1)
    st.session_state.page_num = max(0, st.session_state.page_num)
    start_idx = st.session_state.page_num * items_per_page
    end_idx = min(start_idx + items_per_page, total_items)

    # Results summary
    st.write(f"Showing {total_items} results")
    if total_items == 0:
        st.info("No papers found.")

    # Display research items
    for i in range(start_idx, end_idx):
        if i < len(filtered_data):
            research = filtered_data.iloc[i]
            with st.container(key=f"feed_container_{i}"):
                st.markdown(f"##### {research['title']}")
                st.caption(f"**Category:** {research.get('category', 'Uncategorized')}")
                
                col1, col2, col3 = st.columns([2, 2, 1])
                
                with col1:
                    author_name = research.get('author_name', 'Unknown')
                    if st.button(f"**Author:** {author_name}", key=f"author_btn_{i}"):
                        author_img_url = research.get('author_img_url', '')
                        author_research = research_df[research_df['author_name'] == author_name]['title'].tolist()
                        show_author_details(author_name, author_img_url, author_research)
                    st.markdown(f"**Year:** {int(research.get('created_year', 'Unknown')) if pd.notnull(research.get('created_year')) else 'Unknown'}")
                
                with col2:
                    abstract_preview = research.get('abstract', 'No abstract available')
                    if len(abstract_preview) > 100:
                        abstract_preview = abstract_preview[:100] + "..."
                    st.markdown(f"**Abstract:** {abstract_preview}")
                
                with col3:
                    st.link_button("Download", url=f"https://drive.google.com/uc?export=download&id={research['file_url'].split('/')[-2]}", use_container_width=True)
                    
                    with st.popover("Cite", use_container_width=True):
                        tab1, tab2 = st.tabs(["APA", "MLA"])
                        with tab1:
                            citation = f"{research.get('author_name', 'Author, A.')} ({int(research.get('created_year', 'n.d.')) if pd.notnull(research.get('created_year')) else 'n.d.'}). {research['title']}."
                            st.code(citation, language=None)
                            st.button("Copy", key=f"copy_apa_{i}", use_container_width=True)
                        with tab2:
                            citation = f"{research.get('author_name', 'Author, A.')}. \"{research['title']}.\" {int(research.get('created_year', 'n.d.')) if pd.notnull(research.get('created_year')) else 'n.d.'}."
                            st.code(citation, language=None)
                            st.button("Copy", key=f"copy_mla_{i}", use_container_width=True)
                
                with st.expander("View full abstract"):
                    st.write(research.get('abstract', 'No abstract available'))

    # Pagination controls
    if total_pages > 1:
        st.markdown("---")
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