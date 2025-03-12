import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.http import MediaIoBaseUpload
import io
from datetime import datetime

# Initialize Google Drive API client
def get_drive_service():
    try:
        # Get credentials from Streamlit secrets
        creds_dict = st.secrets["google"]
        credentials = service_account.Credentials.from_service_account_info(
            creds_dict,
            scopes=['https://www.googleapis.com/auth/drive']
        )
        return build('drive', 'v3', credentials=credentials)
    except Exception as e:
        st.error(f"Error initializing Drive service: {str(e)}")
        raise

# Create or get folder ID
def get_or_create_folder(drive_service, folder_name, parent_folder_id=None):
    try:
        # Search for existing folder
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
        if parent_folder_id:
            query += f" and '{parent_folder_id}' in parents"
        
        response = drive_service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name)'
        ).execute()
        
        folders = response.get('files', [])
        
        if folders:
            return folders[0]['id']
        
        # Create new folder if it doesn't exist
        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_folder_id:
            folder_metadata['parents'] = [parent_folder_id]
            
        folder = drive_service.files().create(
            body=folder_metadata,
            fields='id'
        ).execute()
        return folder.get('id')
    except Exception as e:
        st.error(f"Error managing folder: {str(e)}")
        raise

def upload_img(file_uploaded, parent_folder_id=None):
    try:
        drive_service = get_drive_service()
        
        # Create/get images folder
        images_folder_id = get_or_create_folder(drive_service, "author_images", st.secrets.gdrive.author_images_folder_id)
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_extension = file_uploaded.name.split('.')[-1]
        file_name = f"img_{timestamp}.{file_extension}"
        
        # Read file content
        file_content = file_uploaded.getvalue()  # This is the in-memory content
        
        # Prepare file metadata
        file_metadata = {
            'name': file_name,
            'parents': [images_folder_id]
        }
        
        # Upload file using MediaIoBaseUpload for in-memory content
        media = MediaIoBaseUpload(
            io.BytesIO(file_content),  # Pass the in-memory content as a BytesIO object
            mimetype=f'image/{file_extension}',
            resumable=True
        )
        
        # Create file in Drive
        file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id,webViewLink'
        ).execute()
        
        # Make file publicly accessible
        drive_service.permissions().create(
            fileId=file.get('id'),
            body={'type': 'anyone', 'role': 'reader'}
        ).execute()
        
        return file.get('webViewLink')
    except Exception as e:
        st.error(f"Error uploading image: {str(e)}")
        raise

# Upload PDF file
def upload_pdf(file_uploaded, parent_folder_id=None):
    try:
        drive_service = get_drive_service()
        
        # Create/get PDFs folder
        pdfs_folder_id = get_or_create_folder(drive_service, "papers", st.secrets.gdrive.studies_pdf_folder_id)
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"pdf_{timestamp}.pdf"
        
        # Read file content
        file_content = file_uploaded.getvalue()  # This is the in-memory content
        
        # Prepare file metadata
        file_metadata = {
            'name': file_name,
            'parents': [pdfs_folder_id]
        }
        
        # Upload file using MediaIoBaseUpload for in-memory content
        media = MediaIoBaseUpload(
            io.BytesIO(file_content),  # Pass the in-memory content as a BytesIO object
            mimetype='application/pdf',
            resumable=True
        )
        
        # Create file in Drive
        file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id,webViewLink'
        ).execute()
        
        # Make file publicly accessible
        drive_service.permissions().create(
            fileId=file.get('id'),
            body={'type': 'anyone', 'role': 'reader'}
        ).execute()
        
        return file.get('webViewLink')
    except Exception as e:
        st.error(f"Error uploading PDF: {str(e)}")
        raise

