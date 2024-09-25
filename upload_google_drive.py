# Upload folder or file to your google drive
# pip install google-api-python-client
import os
import sys
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload

# Google Drive API Scopes and Service Account
SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'service_account.json'
PARENT_FOLDER_ID = ''  # Parent folder ID in Google Drive

def authenticate():
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return creds

def create_folder(service, folder_name, parent_folder_id):
    """Create a folder on Google Drive."""
    folder_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_folder_id]
    }
    folder = service.files().create(body=folder_metadata, fields='id').execute()
    return folder.get('id')

def upload_file(service, file_path, parent_folder_id):
    """Upload a file to a specific folder on Google Drive."""
    file_name_with_ext = os.path.basename(file_path)
    
    file_metadata = {
        'name': file_name_with_ext,
        'parents': [parent_folder_id]
    }
    media = MediaFileUpload(file_path, resumable=True)
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()
    
    print(f"File uploaded successfully: {file_name_with_ext}, File ID: {file.get('id')}")

def upload_folder(service, folder_path, parent_folder_id):
    """Recursively upload a folder and its contents to Google Drive."""
    folder_name = os.path.basename(folder_path)
    
    # Create the folder on Google Drive
    google_folder_id = create_folder(service, folder_name, parent_folder_id)
    print(f"Created folder '{folder_name}' on Google Drive with ID: {google_folder_id}")

    for root, dirs, files in os.walk(folder_path):
        # Recreate folder structure on Google Drive
        for dir_name in dirs:
            local_folder_path = os.path.join(root, dir_name)
            relative_path = os.path.relpath(local_folder_path, folder_path)
            parent_id = google_folder_id

            # Create the subfolder in the corresponding folder on Google Drive
            google_subfolder_id = create_folder(service, relative_path, parent_id)
            print(f"Created subfolder '{relative_path}' on Google Drive with ID: {google_subfolder_id}")
        
        # Upload files in the current directory
        for file_name in files:
            file_path = os.path.join(root, file_name)
            relative_path = os.path.relpath(file_path, folder_path)
            print(f"Uploading file '{relative_path}'...")
            upload_file(service, file_path, google_folder_id)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: upload.py <file_or_folder_path>")
        sys.exit(1)

    custom_path = sys.argv[1]

    # Initialize Google Drive API service
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)

    # Check if the path is a file or folder
    if os.path.isfile(custom_path):
        upload_file(service, custom_path, PARENT_FOLDER_ID)
    elif os.path.isdir(custom_path):
        upload_folder(service, custom_path, PARENT_FOLDER_ID)
    else:
        print("Error: Provided path is neither a file nor a folder.")
