import streamlit as st
import pandas as pd
import io
import json
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError

class GoogleDriveManager:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
        self.service = None
        
    def authenticate(self):
        """Authenticate with Google Drive API using Service Account"""
        try:
            # Try to get credentials from Streamlit secrets (for cloud deployment)
            if hasattr(st, 'secrets') and 'google_drive' in st.secrets:
                creds_dict = dict(st.secrets["google_drive"])
                creds = service_account.Credentials.from_service_account_info(creds_dict, scopes=self.SCOPES)
            # Fallback to service_account key (alternative naming)
            elif hasattr(st, 'secrets') and 'service_account' in st.secrets:
                creds_dict = dict(st.secrets["service_account"])
                creds = service_account.Credentials.from_service_account_info(creds_dict, scopes=self.SCOPES)
            # Fallback to local service account file (for local development)
            elif os.path.exists('service_account.json'):
                creds = service_account.Credentials.from_service_account_file('service_account.json', scopes=self.SCOPES)
            else:
                st.error(
                    "🔑 **Service Account credentials not found**\n\n"
                    "For local development: Add `service_account.json` file to project root.\n\n"
                    "For deployment: Configure `google_drive` in Streamlit secrets."
                )
                return False
            
            self.service = build('drive', 'v3', credentials=creds)
            return True
            
        except Exception as e:
            st.error(f"❌ Authentication failed: {e}")
            return False
    
    def list_files_in_folder(self, folder_id):
        """List all files in a specific Google Drive folder"""
        if not self.service:
            return []
            
        try:
            # Get all files in the folder
            results = self.service.files().list(
                q=f"'{folder_id}' in parents and trashed=false",
                fields="files(id, name, mimeType, parents)",
                pageSize=1000  # Increase page size for better performance
            ).execute()
            
            return results.get('files', [])
        except HttpError as e:
            st.error(f"❌ Error accessing Google Drive folder: {e}")
            return []
        except Exception as e:
            st.error(f"❌ Unexpected error: {e}")
            return []
    
    def download_file(self, file_id):
        """Download a file from Google Drive and return as pandas DataFrame"""
        if not self.service:
            return None
            
        try:
            # Download file content
            request = self.service.files().get_media(fileId=file_id)
            file_content = io.BytesIO()
            downloader = MediaIoBaseDownload(file_content, request)
            
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                
            file_content.seek(0)
            
            # Convert to pandas DataFrame
            df = pd.read_csv(file_content)
            return df
            
        except HttpError as e:
            st.error(f"❌ Error downloading file from Google Drive: {e}")
            return None
    
    def download_image_file(self, file_id):
        """Download an image file from Google Drive and return as bytes"""
        if not self.service:
            return None
            
        try:
            # Download file content
            request = self.service.files().get_media(fileId=file_id)
            file_content = io.BytesIO()
            downloader = MediaIoBaseDownload(file_content, request)
            
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                
            file_content.seek(0)
            return file_content.read()
            
        except HttpError as e:
            st.error(f"❌ Error downloading image from Google Drive: {e}")
            return None
        except Exception as e:
            st.error(f"❌ Error processing file: {e}")
            return None
    
    def find_folder_by_name(self, folder_name, parent_folder_id=None):
        """Find a folder by name, optionally within a parent folder"""
        try:
            query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            if parent_folder_id:
                query += f" and '{parent_folder_id}' in parents"
            
            results = self.service.files().list(
                q=query,
                fields="files(id, name)",
                pageSize=10
            ).execute()
            
            files = results.get('files', [])
            return files[0]['id'] if files else None
            
        except Exception as e:
            st.error(f"❌ Error finding folder '{folder_name}': {e}")
            return None
    
    def find_file_by_name(self, file_name, folder_id=None):
        """Find a file by name, optionally in a specific folder"""
        if not self.service:
            return None
            
        try:
            query = f"name='{file_name}' and trashed=false"
            if folder_id:
                query += f" and '{folder_id}' in parents"
            
            results = self.service.files().list(
                q=query,
                fields="files(id, name)",
                pageSize=10
            ).execute()
            
            files = results.get('files', [])
            return files[0]['id'] if files else None
            
        except Exception as e:
            st.error(f"❌ Error finding file '{file_name}': {e}")
            return None
    
    def get_folder_structure(self, folder_id=None):
        """Get the folder structure recursively"""
        if not folder_id:
            # Find the root 'processed' folder
            folder_id = self.find_folder_by_name('processed')
            if not folder_id:
                st.error("❌ 'processed' folder not found in Google Drive. Please check folder sharing and structure.")
                return {}
        
        structure = {}
        files = self.list_files_in_folder(folder_id)
        
        for file in files:
            if file['mimeType'] == 'application/vnd.google-apps.folder':
                # It's a folder
                structure[file['name']] = {
                    'type': 'folder',
                    'id': file['id']
                }
            else:
                # It's a file
                structure[file['name']] = {
                    'type': 'file',
                    'id': file['id'],
                    'mimeType': file['mimeType']
                }
        
        return structure
    
    def load_logo_from_drive(self, folder_id, logo_filename="logo_1.png"):
        """Load logo from Google Drive folder with GitHub fallback"""
        if not self.service:
            return self._load_logo_from_github(logo_filename)
            
        try:
            # Try to find the logo file in the specified Google Drive folder
            file_id = self.find_file_by_name(logo_filename, folder_id)
            if not file_id:
                st.info(f"ℹ️ Logo file '{logo_filename}' not found in Google Drive, using GitHub fallback")
                return self._load_logo_from_github(logo_filename)
            
            # Download the image file from Google Drive
            image_bytes = self.download_image_file(file_id)
            if not image_bytes:
                st.info(f"ℹ️ Could not download '{logo_filename}' from Google Drive, using GitHub fallback")
                return self._load_logo_from_github(logo_filename)
            
            # Convert to base64
            import base64
            return base64.b64encode(image_bytes).decode()
            
        except Exception as e:
            st.info(f"ℹ️ Error loading logo from Google Drive ({e}), using GitHub fallback")
            return self._load_logo_from_github(logo_filename)
    
    def _load_logo_from_github(self, logo_filename="logo_1.png"):
        """Load logo from GitHub repository as fallback"""
        try:
            import base64
            import requests
            
            # GitHub raw URL for the logo file
            github_url = f"https://raw.githubusercontent.com/Raaja08/hydro_link/main/assets/{logo_filename}"
            
            response = requests.get(github_url)
            if response.status_code == 200:
                return base64.b64encode(response.content).decode()
            else:
                st.warning(f"⚠️ Could not load logo from GitHub: {response.status_code}")
                return ""
                
        except Exception as e:
            st.warning(f"⚠️ Error loading logo from GitHub: {e}")
            return ""

# Singleton instance
@st.cache_resource
def get_drive_manager():
    return GoogleDriveManager()
