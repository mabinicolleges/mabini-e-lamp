import gspread
import os
import pandas as pd
import streamlit as st
import time

credentials = {
    "type": st.secrets.google.type,
    "project_id": st.secrets.google.project_id,
    "private_key_id": st.secrets.google.private_key_id,
    "private_key": st.secrets.google.private_key,
    "client_email": st.secrets.google.client_email,
    "client_id": st.secrets.google.client_id,
    "auth_uri": st.secrets.google.auth_uri,
    "token_uri": st.secrets.google.token_uri,
    "auth_provider_x509_cert_url": st.secrets.google.auth_provider_x509_cert_url,
    "universe_domain": st.secrets.google.universe_domain
}

gc = gspread.service_account_from_dict(credentials)
sh = gc.open_by_key(st.secrets.gsheets.sheets_id)

sheet_names = [
    "research_data",
    "researchers_data",
]

def get_data_ls_dict(sheet_name: str):
    """
    Retrieves data from a specified Google Sheets worksheet and returns it as a list of dictionaries.

    Args:
        sheet_name (str): The name of the worksheet to retrieve data from.

    Returns:
        list: A list of dictionaries containing the worksheet data if the sheet name exists.
        str: An error message if the sheet name does not exist in the predefined sheet names.

    Raises:
        Exception: If there is an error accessing the worksheet or retrieving the data.
    """
    try: 
        if sheet_name.lower() in sheet_names:
            worksheet = sh.worksheet(sheet_name)
            data = worksheet.get_all_records()
            return data
    except Exception as e:
        return f"{sheet_name} must be in {sheet_names}"

def get_data_df(sheet_name: str, columns_to_access: list[str] = None):
    """
    Retrieve data from a Google Sheets worksheet and return it as a pandas DataFrame.
    Args:
        sheet_name (str): The name of the sheet to access.
        columns_to_access (list[str], optional): A list of column names to retrieve from the sheet. 
                                                 If None, all columns will be retrieved. Defaults to None.
    Returns:
        pd.DataFrame or str: A pandas DataFrame containing the requested data if successful, 
                             or an error message string if an error occurs or if specified columns are not found.
    """
    try:
        if sheet_name.lower() in sheet_names:
            worksheet = sh.worksheet(sheet_name)
            data = worksheet.get_all_records()
            df = pd.DataFrame(data)
            if columns_to_access is None:
                return df
            missing_columns = [col for col in columns_to_access if col not in df.columns]
            if missing_columns:
                return f"Columns {missing_columns} not found in the sheet {sheet_name}"
            return df[columns_to_access]
    except Exception as e:
        return f"An error occurred: {str(e)}"
    
def post_add_new_paper(title, abstract, author_name, author_img_url, category, created_year, keywords, file_url, sheet_name="research_data"):
    """
    Adds a new paper entry to the specified Google Sheets worksheet.

    Args:
        title (str): The title of the paper.
        abstract (str): The abstract of the paper.
        author_name (str): The name of the author.
        author_img_url (str): The URL of the author's image.
        category (str): The category of the paper.
        created_year (int): The year the paper was created.
        keywords (str): Keywords associated with the paper.
        file_url (str): The URL of the paper file.
        sheet_name (str, optional): The name of the worksheet to add the entry to. Defaults to "research_data".

    Returns:
        None
    """
    worksheet = sh.worksheet(sheet_name)
    # Get the last row in the worksheet
    last_row = worksheet.get_all_values()[-1] if worksheet.get_all_values()[-1] != "id" else 0
    # Get the ID from the last row
    id = int(last_row[0]) + 1
    created_at = time.strftime("%Y-%m-%d %H:%M:%S")
    body = [id, title, abstract, author_name, author_img_url, category, created_year, keywords, file_url, created_at]  # the values should be a list
    worksheet.append_row(body, table_range=f"A{id}:J{id}")