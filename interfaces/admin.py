import streamlit as st
from services import sheets_service as ss
from services import drive_service as ds
from fuzzywuzzy import fuzz
import pandas as pd
import requests
import re
import time

# Load and cache data with preprocessing
@st.cache_data
def load_research_data():
    """Load and cache research data with preprocessing for faster searching"""
    data = ss.get_data_ls_dict("research_data")
    df = pd.DataFrame(data)
    
    # Preprocess for searching
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

# Define the upload paper dialog
@st.dialog("Upload New Paper", width="large")
def upload_paper_dialog(research_df):
    st.subheader("Add New Research Paper")
    st.caption("Fill in all fields to publish a new research paper to the database")
    
    col1, col2 = st.columns(2)
    with col1:
        title = st.text_input("Title", placeholder="Enter paper title")
        author_name = st.text_input("Author Name", placeholder="Surname, First Name M.I.")
        category_options = ["Hospital", "Community", "Others"]
        category = st.selectbox("Category", category_options if category_options else ["Uncategorized"])
        created_year = st.number_input("Year Published", min_value=1900, max_value=2100, value=2023)
        keywords = st.text_input("Keywords (comma separated)", placeholder="e.g., machine learning, climate")
    
    with col2:
        abstract = st.text_area("Abstract", placeholder="Enter paper abstract", height=150)
        author_img_file = st.file_uploader("Author Image", type=["jpg", "jpeg", "png"])
        paper_file = st.file_uploader("Paper File (PDF)", type=["pdf"])
    
    st.markdown("---")
    button_col1, button_col2 = st.columns([1, 3])
    with button_col1:
        publish_button = st.button("Publish Paper", type="primary", use_container_width=True)
    
    message_container = st.empty()
    if publish_button:
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
                    author_img_url = ds.upload_img(author_img_file)
                    file_url = ds.upload_pdf(paper_file)
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
                st.toast("Paper published successfully!", icon="✅")
                time.sleep(1)
                st.rerun()
            except Exception as e:
                message_container.error(f"Error publishing paper: {str(e)}")

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
    fuzzy_matches = df[df['match_score'] >= threshold].sort_values('match_score', ascending=False)
    return fuzzy_matches.drop(columns=['match_score'])

# Sorting function
def sort_data(df, sort_option):
    if sort_option == "Alphabetical (A-Z)":
        return df.sort_values('title')
    elif sort_option == "Alphabetical (Z-A)":
        return df.sort_values('title', ascending=False)
    elif sort_option == "Year (Newest First)":
        return df.sort_values('created_year', ascending=False)
    elif sort_option == "Year (Oldest First)":
        return df.sort_values('created_year')
    return df  # Default case returns unsorted (Relevance)

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
    st.header("Filter Research Papers")
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
    
    with st.expander("Admin Help"):
        st.markdown("""
        - **Search**: Find papers by title, abstract, or author
        - **Categories**: Filter by research categories
        - **Keywords**: Use comma-separated keywords
        - **Year Range**: Limit by publication years
        - **Upload**: Add new papers via the top button
        """)
    st.sidebar.markdown("---")
    st.sidebar.button("Log out", key="logout", on_click=st.logout, use_container_width=True)

# Main content area
_, feed_col, _ = st.columns([1, 8, 1])
with feed_col:
    st.title("Admin Dashboard")
    st.caption("Manage research papers and upload new content to the database")
    st.markdown("---")
    
    # Admin actions
    admin_cols = st.columns(2)
    with admin_cols[0]:
        if st.button("📄 Upload New Paper", type="primary", use_container_width=True):
            upload_paper_dialog(research_df)
    with admin_cols[1]:
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    # Search bar and sort options
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

    # Display results
    filtered_data = sort_data(st.session_state.filtered_data, st.session_state.sort_option)
    total_items = len(filtered_data)
    st.write(f"Showing {total_items} results")
    if total_items == 0:
        st.info("No papers found.")

    # Pagination setup
    items_per_page = 10
    total_pages = max(1, (total_items + items_per_page - 1) // items_per_page)
    st.session_state.page_num = min(st.session_state.page_num, total_pages - 1)
    st.session_state.page_num = max(0, st.session_state.page_num)
    start_idx = st.session_state.page_num * items_per_page
    end_idx = min(start_idx + items_per_page, total_items)

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
                    if 'file_url' in research:
                        st.link_button("📄 View PDF", url=research['file_url'], use_container_width=True)
                
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