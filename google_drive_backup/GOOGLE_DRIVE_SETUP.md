# Google Drive Integration Setup Guide

## Prerequisites

1. **Google Cloud Project Setup**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable Google Drive API
   - Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client IDs"
   - Choose "Desktop application"
   - Download the JSON file and rename it to `credentials.json`
   - Place `credentials.json` in your project root directory

2. **Install Required Packages**
   ```bash
   pip install -r requirements.txt
   ```

3. **Google Drive Folder Structure**
   Your Google Drive folder should have this structure:
   ```
   hydro_link/
   ├── processed/
   │   └── tb/
   │       ├── tb_site1/
   │       │   ├── tb_s1_2018.csv
   │       │   ├── tb_s1_2019.csv
   │       │   └── ...
   │       ├── tb_site7/
   │       │   ├── tb_s7_2018.csv
   │       │   └── ...
   │       └── ...
   └── assets/
       └── logo_1.png
   ```

## Deployment Options

### Option 1: Streamlit Cloud (Recommended for Public Access)

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin YOUR_GITHUB_REPO_URL
   git push -u origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository
   - Add secrets in Streamlit Cloud dashboard:
     - Copy content of `credentials.json` to secrets as `GOOGLE_CREDENTIALS`

3. **Update code for Streamlit Cloud**
   ```python
   # In google_drive_utils.py, replace file-based auth with:
   if 'GOOGLE_CREDENTIALS' in st.secrets:
       creds_dict = dict(st.secrets["GOOGLE_CREDENTIALS"])
       creds = Credentials.from_authorized_user_info(creds_dict, SCOPES)
   ```

### Option 2: Local Network Access

1. **Run locally with network access**
   ```bash
   streamlit run pages/3_TB_Sensor.py --server.address 0.0.0.0 --server.port 8501
   ```

2. **Access from other devices on same network**
   - Find your IP address: `ipconfig` (Windows) or `ifconfig` (Mac/Linux)
   - Others can access via: `http://YOUR_IP_ADDRESS:8501`

### Option 3: Heroku Deployment

1. **Create Heroku app**
   ```bash
   heroku create your-app-name
   ```

2. **Add buildpacks**
   ```bash
   heroku buildpacks:add heroku/python
   ```

3. **Set environment variables**
   ```bash
   heroku config:set GOOGLE_CREDENTIALS='{"your": "credentials_json_content"}'
   ```

## Authentication Flow

### First Time Setup
1. User runs the app
2. If no valid credentials, they'll be redirected to Google OAuth
3. After authorization, credentials are saved locally
4. Subsequent runs use saved credentials

### For Production
- Use service account credentials instead of OAuth for better reliability
- Store credentials securely using environment variables or secrets management

## Security Considerations

1. **Never commit credentials.json to git**
   - Add to `.gitignore`
   - Use environment variables in production

2. **Google Drive Permissions**
   - Use read-only scope: `https://www.googleapis.com/auth/drive.readonly`
   - Consider using service account for production

3. **Access Control**
   - Google Drive folder sharing controls who can access data
   - App inherits user's Drive permissions

## Troubleshooting

1. **Authentication Issues**
   - Delete `token.pickle` and re-authenticate
   - Check Google Cloud Console for API quotas

2. **File Access Issues**
   - Verify folder sharing permissions
   - Check folder ID in the Google Drive URL

3. **Performance Issues**
   - Implement caching with `@st.cache_data`
   - Consider downloading and caching frequently accessed files

## Alternative: Public Dataset Hosting

For easier public access, consider:

1. **GitHub LFS** - Store data in Git Large File Storage
2. **AWS S3** - Host files publicly or with signed URLs  
3. **Google Cloud Storage** - Similar to S3 but Google ecosystem
4. **Kaggle Datasets** - Free hosting for public datasets
