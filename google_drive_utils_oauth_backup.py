import streamlit as st
import pandas as pd
import io
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import pickle
import os

class GoogleDriveManager:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
        self.FOLDER_ID = '1yTSc-xQuUm1VgJWFFul7PSh0uZJnnLPh'  # Your Google Drive folder ID
        self.service = None
        
    def authenticate(self):
        """Authenticate with Google Drive API"""
        creds = None
        
        # Check if token.pickle exists (saved credentials)
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
                
        # If there are no valid credentials, request authorization
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                # You'll need to create credentials.json from Google Cloud Console
                flow = Flow.from_client_secrets_file(
                    'credentials.json', self.SCOPES)
                flow.redirect_uri = 'http://localhost:8501'
                
                # This would need to be handled differently in production
                st.error("Authentication required. Please set up Google Drive credentials.")
                return None
                
            # Save credentials for next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
                
        self.service = build('drive', 'v3', credentials=creds)
        return self.service
    
    def list_files_in_folder(self, folder_id=None):
        """List all files in a specific Google Drive folder"""
        if not self.service:
            return []
            
        if not folder_id:
            folder_id = self.FOLDER_ID
            
        try:
            # Get all files in the folder
            results = self.service.files().list(
                q=f"'{folder_id}' in parents and trashed=false",
                fields="files(id, name, mimeType, parents)"
            ).execute()
            
            return results.get('files', [])
        except Exception as e:
            st.error(f"Error accessing Google Drive: {e}")
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
            
        except Exception as e:
            st.error(f"Error downloading file: {e}")
            return None
    
    def get_folder_structure(self, folder_id=None):
        """Get the folder structure recursively"""
        if not folder_id:
            folder_id = self.FOLDER_ID
            
        structure = {}
        files = self.list_files_in_folder(folder_id)
        
        for file in files:
            if file['mimeType'] == 'application/vnd.google-apps.folder':
                # It's a folder, get its contents recursively
                structure[file['name']] = {
                    'type': 'folder',
                    'id': file['id'],
                    'contents': self.get_folder_structure(file['id'])
                }
            else:
                # It's a file
                structure[file['name']] = {
                    'type': 'file',
                    'id': file['id'],
                    'mimeType': file['mimeType']
                }
        
        return structure

# Singleton instance
@st.cache_resource
def get_drive_manager():
    return GoogleDriveManager()
