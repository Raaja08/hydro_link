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
            creds_dict = None
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
                # Also load the dict for email display
                with open('service_account.json', 'r') as f:
                    creds_dict = json.load(f)
            else:
                return False
            
            self.service = build('drive', 'v3', credentials=creds)
            
            # Store credentials for display (after successful authentication)
            if creds_dict and 'client_email' in creds_dict:
                self._service_account_email = creds_dict['client_email']
            
            return True
            
        except Exception as e:
            return False
    
    def get_service_account_email(self):
        """Get the service account email for display purposes"""
        try:
            if hasattr(self, '_service_account_email'):
                return self._service_account_email
            
            # Try to get from secrets if available
            if hasattr(st, 'secrets') and 'google_drive' in st.secrets:
                creds_dict = dict(st.secrets["google_drive"])
                if 'client_email' in creds_dict:
                    return creds_dict['client_email']
            elif hasattr(st, 'secrets') and 'service_account' in st.secrets:
                creds_dict = dict(st.secrets["service_account"])
                if 'client_email' in creds_dict:
                    return creds_dict['client_email']
            elif os.path.exists('service_account.json'):
                with open('service_account.json', 'r') as f:
                    creds_dict = json.load(f)
                    if 'client_email' in creds_dict:
                        return creds_dict['client_email']
            
            return "Not available"
            
        except Exception as e:
            return "Not available"
    
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
    
    def find_folder_recursively(self, folder_name, search_in_folder_id=None):
        """Find a folder by name recursively searching through all accessible folders"""
        try:
            # First, try direct search (all folders with this name)
            query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            results = self.service.files().list(
                q=query,
                fields="files(id, name, parents)",
                pageSize=50
            ).execute()
            
            files = results.get('files', [])
            if files:
                # If we have a specific parent to search in, filter by that
                if search_in_folder_id:
                    for file in files:
                        if file.get('parents') and search_in_folder_id in file['parents']:
                            return file['id']
                else:
                    # Return the first match if no specific parent
                    return files[0]['id']
            
            return None
            
        except Exception as e:
            st.error(f"❌ Error in recursive folder search for '{folder_name}': {e}")
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
    
    def _create_virtual_structure(self, folders):
        """Create a virtual processed folder structure from accessible folders"""
        structure = {}
        
        # Group folders by sensor type
        obs_folders = [f for f in folders if f['name'].startswith('obs_site')]
        hobo_folders = [f for f in folders if f['name'].startswith('hobo_site')]
        tb_folders = [f for f in folders if f['name'].startswith('tb_site')]
        atm_folders = [f for f in folders if f['name'].startswith('atm_site')]
        
        if obs_folders:
            structure['obs'] = {
                'type': 'folder',
                'id': 'virtual_obs',
                'subfolders': {f['name']: {'type': 'folder', 'id': f['id']} for f in obs_folders}
            }
        
        if hobo_folders:
            structure['hobo'] = {
                'type': 'folder', 
                'id': 'virtual_hobo',
                'subfolders': {f['name']: {'type': 'folder', 'id': f['id']} for f in hobo_folders}
            }
        
        if tb_folders:
            structure['tb'] = {
                'type': 'folder',
                'id': 'virtual_tb', 
                'subfolders': {f['name']: {'type': 'folder', 'id': f['id']} for f in tb_folders}
            }
        
        if atm_folders:
            structure['atmos'] = {
                'type': 'folder',
                'id': 'virtual_atmos',
                'subfolders': {f['name']: {'type': 'folder', 'id': f['id']} for f in atm_folders}
            }
        
        return structure
    
    def get_folder_structure(self, folder_id=None):
        """Get the folder structure recursively"""
        if not folder_id:
            # Check for accessible items without verbose debugging
            try:
                # List all accessible folders and files
                all_items = self.service.files().list(
                    q="trashed=false",
                    fields="files(id, name, mimeType, parents)",
                    pageSize=50
                ).execute()
                
                items = all_items.get('files', [])
                if items:
                    folders = [item for item in items if item['mimeType'] == 'application/vnd.google-apps.folder']
                    files = [item for item in items if item['mimeType'] != 'application/vnd.google-apps.folder']
                    
                    if folders:
                        
                        # Look for 'processed' specifically
                        processed_folders = [f for f in folders if 'processed' in f['name'].lower()]
                        if processed_folders:
                            folder_id = processed_folders[0]['id']  # Use the first match
                        else:
                            st.warning("⚠️ **No 'processed' folder found at root level, searching in nested folders...**")
                            # Search recursively in each folder for 'processed'
                            for folder in folders:
                                nested_processed = self.find_folder_by_name('processed', folder['id'])
                                if nested_processed:
                                    folder_id = nested_processed
                                    break
                            
                            if not folder_id:
                                st.warning("⚠️ **No 'processed' folder found even in nested folders**")
                                
                                # SOLUTION: Create virtual structure from accessible folders
                                # st.info("💡 **Creating virtual 'processed' structure from accessible folders**")
                                return self._create_virtual_structure(folders)
                    else:
                        # st.warning("📂 **No folders accessible to Service Account**")
                        pass
                        
                    if files and not folders:
                        # st.info(
                            # "📁 **Accessible files:**\n\n" +
                            # "\n".join([f"• {file['name']}" for file in files[:10]])
                        # )
                        pass
                else:
                    # st.error("❌ **No items accessible to Service Account - folder sharing may not have propagated yet**")
                    pass
                    
            except Exception as e:
                st.error(f"❌ **Debug error:** {e}")
                
            # If we still don't have folder_id, try the original method and then recursive search
            if not folder_id:
                folder_id = self.find_folder_by_name('processed')
                
            # If still not found, try recursive search
            if not folder_id:
                folder_id = self.find_folder_recursively('processed')
                
            if not folder_id:
                st.error(
                    "❌ **'processed' folder still not found**\n\n"
                    "**Possible solutions:**\n"
                    "1. **Wait 5-10 minutes** - Google Drive sharing can take time to propagate\n"
                    "2. **Check folder name** - Make sure it's exactly 'processed'\n"
                    "3. **Re-share folder** - Try sharing again with the Service Account email\n"
                    "4. **Check Service Account** - Verify the email is correct\n"
                    "5. **Check nesting** - The 'processed' folder might be nested deeper than expected"
                )
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
    
    def test_drive_access(self):
        """Simple test to verify Google Drive API access"""
        if not self.service:
            return False, "Service not initialized"
            
        try:
            # Try to list any files (minimal query)
            results = self.service.files().list(pageSize=1).execute()
            files = results.get('files', [])
            return True, f"Success - can access Google Drive ({len(files)} files visible)"
        except Exception as e:
            return False, f"Failed - {str(e)}"
    
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

# Singleton instance - cleaned debugging output v2
@st.cache_resource
def get_drive_manager():
    return GoogleDriveManager()
