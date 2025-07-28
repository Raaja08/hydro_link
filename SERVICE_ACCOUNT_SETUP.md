# 🔐 Service Account Setup Guide for Google Drive Integration

This guide shows you how to set up **Service Account authentication** for your Streamlit app, which is the **correct approach** for production deployment.

## 🎯 **Why Service Account vs OAuth?**

| Feature | Service Account ✅ | OAuth ❌ |
|---------|-------------------|----------|
| **User Experience** | No login required | Users must login every time |
| **Data Privacy** | Private, controlled access | Exposes raw data to users |
| **Deployment** | Works on any server | Complex server setup |
| **Maintenance** | Set once, works forever | Tokens expire, needs refresh |
| **Multi-user** | All users see same data | Each user sees their own data |

## 📋 **Step-by-Step Setup**

### **Step 1: Create Google Cloud Project**

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **"Select a project"** → **"New Project"**
3. Name your project: `hydro-link-dashboard`
4. Click **"Create"**

### **Step 2: Enable Google Drive API**

1. In your project, go to **"APIs & Services"** → **"Library"**
2. Search for **"Google Drive API"**
3. Click on it and press **"Enable"**

### **Step 3: Create Service Account**

1. Go to **"APIs & Services"** → **"Credentials"**
2. Click **"Create Credentials"** → **"Service Account"**
3. Fill in details:
   - **Service account name**: `hydro-link-app-service`
   - **Service account ID**: (auto-generated)
   - **Description**: `Service account for Hydro Link Dashboard`
4. Click **"Create and Continue"**
5. Skip the optional steps and click **"Done"**

### **Step 4: Create Service Account Key**

1. Find your service account in the **"Credentials"** page
2. Click on the service account email
3. Go to **"Keys"** tab
4. Click **"Add Key"** → **"Create new key"**
5. Select **"JSON"** format
6. Click **"Create"**
7. **Save the downloaded JSON file as `service_account.json`** in your project root

⚠️ **IMPORTANT**: This JSON file contains sensitive credentials. Never commit it to GitHub!

### **Step 5: Share Google Drive Folder**

1. Go to your Google Drive
2. Find your `processed` folder (containing tb/, hobo/, obs/, etc.)
3. Right-click the folder → **"Share"**
4. Add the service account email (from the JSON file, looks like: `hydro-link-app-service@hydro-link-dashboard.iam.gserviceaccount.com`)
5. Set permission to **"Viewer"**
6. Click **"Send"**

### **Step 6: Test Locally**

1. Place `service_account.json` in your project root:
   ```
   hydro_link/
   ├── service_account.json    ← Add this file
   ├── pages/
   ├── google_drive_utils.py
   └── ...
   ```

2. Test the app:
   ```bash
   streamlit run pages/3_TB_Sensor_G.py
   ```

3. Check the Google Drive toggle - it should work without login!

## 🚀 **Deployment Options**

### **Option 1: Streamlit Cloud (Recommended)**

1. **Prepare GitHub Repository**:
   ```bash
   # Make sure service_account.json is in .gitignore
   echo "service_account.json" >> .gitignore
   
   # Commit and push to GitHub
   git add .
   git commit -m "Add service account support"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository
   - Set **Main file path**: `pages/3_TB_Sensor_G.py`

3. **Add Service Account to Secrets**:
   - In Streamlit Cloud dashboard, go to **"Settings"** → **"Secrets"**
   - Copy the **entire content** of your `service_account.json` file
   - Add it as:
   ```toml
   [service_account]
   type = "service_account"
   project_id = "hydro-link-dashboard"
   private_key_id = "your_key_id"
   private_key = "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY\n-----END PRIVATE KEY-----\n"
   client_email = "hydro-link-app-service@hydro-link-dashboard.iam.gserviceaccount.com"
   client_id = "your_client_id"
   auth_uri = "https://accounts.google.com/o/oauth2/auth"
   token_uri = "https://oauth2.googleapis.com/token"
   auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
   client_x509_cert_url = "your_cert_url"
   ```

### **Option 2: Other Cloud Platforms**

For **Heroku**, **Railway**, **Render**, etc.:

1. Set the service account JSON as an environment variable:
   ```bash
   # For Heroku
   heroku config:set GOOGLE_SERVICE_ACCOUNT='{"type":"service_account",...}'
   ```

2. Update `google_drive_utils.py` to read from environment:
   ```python
   import os
   
   # In authenticate() method
   if 'GOOGLE_SERVICE_ACCOUNT' in os.environ:
       creds_dict = json.loads(os.environ['GOOGLE_SERVICE_ACCOUNT'])
       creds = service_account.Credentials.from_service_account_info(creds_dict, scopes=self.SCOPES)
   ```

## 🔒 **Security Best Practices**

1. **Never commit service account JSON to version control**
2. **Use environment variables or secrets management in production**
3. **Grant minimum required permissions (Viewer only)**
4. **Monitor service account usage in Google Cloud Console**
5. **Rotate service account keys periodically**

## 🛠️ **Troubleshooting**

### **"Service account credentials not found"**
- Check if `service_account.json` exists locally
- For cloud deployment, verify secrets are configured correctly

### **"Error accessing Google Drive folder"**
- Verify the service account email has access to your Google Drive folder
- Check if the folder structure matches: `processed/tb/`, `processed/hobo/`, etc.

### **"Authentication failed"**
- Ensure Google Drive API is enabled in your Google Cloud project
- Check that the service account key is valid (not expired)

### **"No data found"**
- Verify your Google Drive folder structure matches the expected format
- Check if CSV files are in the correct folders

## 📁 **Required Google Drive Structure**

Your Google Drive should have this structure:
```
processed/
├── tb/
│   ├── tb_site1/
│   │   ├── tb_s1_2018.csv
│   │   ├── tb_s1_2019.csv
│   │   └── ...
│   └── tb_site7/
│       ├── tb_s7_2018.csv
│       └── ...
├── hobo/
│   ├── hobo_site1/
│   │   └── hobo_s1_2023.csv
│   └── hobo_site2/
│       └── hobo_s2_2023.csv
├── obs/
│   ├── obs_site1/
│   │   └── obs_s1_2023.csv
│   └── obs_site2/
│       └── obs_s2_2023.csv
├── atmos/
│   └── atm_site1/
│       └── atm_s1_2023.csv
└── sensor_metadata/
    └── sensor_metadata.csv
```

## 🎉 **Final Steps**

1. **Test locally** with `service_account.json`
2. **Deploy to Streamlit Cloud** with secrets configuration
3. **Share the public URL** with your users
4. **Users can access the dashboard without any login!**

---

**🔥 Pro Tip**: With Service Account setup, your app will work seamlessly for all users, and your data stays completely private and controlled by you!
