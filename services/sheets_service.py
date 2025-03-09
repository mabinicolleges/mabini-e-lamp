import gspread
import os
import pandas as pd
import streamlit as st

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

print(credentials)

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
    