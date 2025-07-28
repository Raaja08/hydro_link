import streamlit as st
import pandas as pd
import io
import json
import os
from google.oauth2 import service_account
from google.cloud import storage
from google.cloud.exceptions import NotFound, Forbidden

class CloudStorageManager:
    def __init__(self):
        self.client = None
        self.bucket_name = "hydro-link-data"  # You'll create this bucket
        self.bucket = None
        
    def authenticate(self):
        """Authenticate with Google Cloud Storage using Service Account"""
        try:
            creds_dict = None
            # Try to get credentials from Streamlit secrets (for cloud deployment)
            if hasattr(st, 'secrets') and 'google_cloud' in st.secrets:
                creds_dict = dict(st.secrets["google_cloud"])
                creds = service_account.Credentials.from_service_account_info(creds_dict)
            # Fallback to google_drive secrets (reuse existing)
            elif hasattr(st, 'secrets') and 'google_drive' in st.secrets:
                creds_dict = dict(st.secrets["google_drive"])
                creds = service_account.Credentials.from_service_account_info(creds_dict)
            # Fallback to local service account file (for local development)
            elif os.path.exists('service_account.json'):
                creds = service_account.Credentials.from_service_account_file('service_account.json')
                # Also load the dict for email display
                with open('service_account.json', 'r') as f:
                    creds_dict = json.load(f)
            else:
                return False
            
            self.client = storage.Client(credentials=creds)
            
            try:
                self.bucket = self.client.bucket(self.bucket_name)
                # Test bucket access
                self.bucket.reload()
                
                # Store credentials for display (after successful authentication)
                if creds_dict and 'client_email' in creds_dict:
                    self._service_account_email = creds_dict['client_email']
                
                return True
            except NotFound:
                st.error(f"❌ Bucket '{self.bucket_name}' not found. Please create it first.")
                return False
            except Forbidden:
                st.error(f"❌ No access to bucket '{self.bucket_name}'. Check permissions.")
                return False
            
        except Exception as e:
            st.error(f"❌ Authentication failed: {str(e)}")
            return False
    
    def get_service_account_email(self):
        """Get the service account email for display purposes"""
        return getattr(self, '_service_account_email', "Not available")
    
    def test_bucket_access(self):
        """Test basic bucket access"""
        try:
            if not self.bucket:
                return False, "Bucket not initialized"
            
            # List a few files to test access
            blobs = list(self.bucket.list_blobs(max_results=5))
            file_count = len(blobs)
            
            return True, f"Successfully connected - found {file_count} files"
        except Exception as e:
            return False, f"Access test failed: {str(e)}"
    
    def list_files(self, prefix=""):
        """List files in bucket with optional prefix"""
        try:
            if not self.bucket:
                return []
            
            blobs = self.bucket.list_blobs(prefix=prefix)
            return [blob.name for blob in blobs]
        except Exception as e:
            st.error(f"Error listing files: {str(e)}")
            return []
    
    def get_folder_structure(self, prefix="processed/"):
        """Get folder structure similar to Google Drive structure"""
        try:
            files = self.list_files(prefix)
            structure = {}
            
            for file_path in files:
                # Remove prefix and split path
                relative_path = file_path.replace(prefix, "").strip("/")
                if not relative_path:
                    continue
                    
                parts = relative_path.split("/")
                
                # Build nested structure
                current_level = structure
                for i, part in enumerate(parts):
                    if i == len(parts) - 1:  # It's a file
                        if part.endswith('.csv'):
                            current_level[part] = {
                                'type': 'file',
                                'path': file_path,
                                'name': part
                            }
                    else:  # It's a folder
                        if part not in current_level:
                            current_level[part] = {
                                'type': 'folder',
                                'subfolders': {},
                                'name': part
                            }
                        current_level = current_level[part]['subfolders']
            
            return structure
        except Exception as e:
            st.error(f"Error getting folder structure: {str(e)}")
            return {}
    
    def download_csv(self, file_path):
        """Download CSV file and return as pandas DataFrame"""
        try:
            if not self.bucket:
                return None
            
            blob = self.bucket.blob(file_path)
            
            # Download as string
            csv_data = blob.download_as_text()
            
            # Convert to DataFrame
            df = pd.read_csv(io.StringIO(csv_data))
            
            return df
        except Exception as e:
            st.error(f"Error downloading file {file_path}: {str(e)}")
            return None
    
    def file_exists(self, file_path):
        """Check if file exists in bucket"""
        try:
            if not self.bucket:
                return False
            
            blob = self.bucket.blob(file_path)
            return blob.exists()
        except Exception as e:
            return False
    
    def upload_file(self, local_path, cloud_path):
        """Upload a local file to cloud storage"""
        try:
            if not self.bucket:
                return False
            
            blob = self.bucket.blob(cloud_path)
            blob.upload_from_filename(local_path)
            return True
        except Exception as e:
            st.error(f"Error uploading file: {str(e)}")
            return False

# Singleton instance
_storage_manager = None

def get_storage_manager():
    """Get the global CloudStorageManager instance"""
    global _storage_manager
    if _storage_manager is None:
        _storage_manager = CloudStorageManager()
    return _storage_manager
