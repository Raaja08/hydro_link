# Google Drive Sensor Dashboard Versions

This document provides an overview of the Google Drive-enabled sensor dashboard versions created for public access and cloud data integration.

## 📁 Created Files

### 1. **TB Sensor (Rainfall & Temperature) - Google Drive Version**
- **File**: `pages/3_TB_Sensor_G.py`
- **Features**:
  - ✅ Rainfall and Temperature plotting with smart aggregation
  - ✅ Google Drive data source toggle
  - ✅ Missing data gap visualization
  - ✅ Professional plot formatting with dual y-axis
  - ✅ Summary statistics for rainfall data
  - ✅ Individual plot downloads
  - ✅ Custom, Daily, Monthly, and Yearly views

### 2. **HOBO Sensor - Google Drive Version**
- **File**: `pages/2_HOBO_Sensor_G.py`
- **Features**:
  - ✅ Water level, pressure, and temperature monitoring
  - ✅ Google Drive data source toggle
  - ✅ Automatic water level calculation from pressure data
  - ✅ Sensor metadata integration
  - ✅ Multiple time view modes (Daily, Weekly, Monthly, Custom)
  - ✅ Individual plot downloads

### 3. **OBS Sensor - Google Drive Version**
- **File**: `OBS_Sensor_G.py`
- **Features**:
  - ✅ Multi-parameter monitoring (ambient light, backscatter, pressure, temperature)
  - ✅ Google Drive data source toggle
  - ✅ Atmospheric pressure compensation for water level
  - ✅ Outlier filtering and data quality control
  - ✅ Sensor metadata integration
  - ✅ Individual plot downloads

## 🔧 **Key Features Across All Versions**

### **Data Source Flexibility**
- **📁 Google Drive Toggle**: Checkbox in sidebar to switch between local and cloud data
- **🔒 OAuth Authentication**: Secure Google Drive access for public deployment
- **📂 Automatic Folder Discovery**: Finds sensor data in `processed/` folder structure
- **⚠️ Graceful Fallback**: Reverts to local mode if Google Drive unavailable

### **Professional Dashboard Features**
- **🎨 Consistent UI**: Same professional layout and branding across all versions
- **📊 Advanced Plotting**: Plotly-based interactive visualizations
- **📈 Smart Data Processing**: Proper aggregation, missing data handling, outlier filtering
- **💾 Individual Downloads**: PNG export for each plot
- **📱 Responsive Design**: Works on desktop and mobile devices

### **Google Drive Integration**
- **🗂️ Folder Structure Navigation**: Automatically discovers sensor folders
- **📄 Multiple File Support**: Handles CSV data files and metadata
- **🔄 Real-time Loading**: Loads data directly from Google Drive with caching
- **🚫 Batch Download Disabled**: Individual downloads only to avoid complexity

## 🚀 **Deployment Guide**

### **Prerequisites**
1. **Google Drive Setup**: Follow `GOOGLE_DRIVE_SETUP.md` for OAuth credentials
2. **Data Structure**: Ensure folder structure matches:
   ```
   processed/
   ├── tb/
   │   ├── tb_site1/
   │   └── tb_site7/
   ├── hobo/
   │   ├── hobo_site1/
   │   └── hobo_site2/
   ├── obs/
   │   ├── obs_site1/
   │   └── obs_site2/
   ├── atmos/
   │   └── atm_site1/
   └── sensor_metadata/
       └── sensor_metadata.csv
   ```

### **Installation**
```bash
pip install -r requirements.txt
```

### **Run Applications**
```bash
# TB Sensor (Google Drive)
streamlit run pages/3_TB_Sensor_G.py

# HOBO Sensor (Google Drive)  
streamlit run pages/2_HOBO_Sensor_G.py

# OBS Sensor (Google Drive)
streamlit run OBS_Sensor_G.py
```

## 📋 **Version Comparison**

| Feature | Local Versions | Google Drive Versions |
|---------|---------------|----------------------|
| **Data Source** | Local file system | Google Drive + Local fallback |
| **Public Access** | ❌ | ✅ |
| **OAuth Required** | ❌ | ✅ |
| **Batch Downloads** | ✅ | ❌ (Individual only) |
| **Offline Mode** | ✅ | ✅ (Fallback) |
| **Deployment** | Local only | Cloud deployable |

## 🔐 **Security Notes**

- **OAuth Credentials**: Store `credentials.json` securely, never commit to version control
- **Token Management**: `token.json` is auto-generated, include in `.gitignore`
- **Public Deployment**: Use environment variables for sensitive configuration
- **Data Privacy**: Ensure appropriate Google Drive sharing permissions

## 📊 **Usage Tips**

1. **First Run**: Google Drive versions will prompt for authentication
2. **Data Toggle**: Use sidebar checkbox to switch between local/cloud data
3. **Fallback Mode**: If Google Drive fails, application automatically uses local data
4. **Performance**: Google Drive loading may be slower than local files
5. **Caching**: Data is cached to improve performance on repeated access

## 🛠️ **Troubleshooting**

### **Common Issues**
- **Authentication Failed**: Check `credentials.json` and follow setup guide
- **No Data Found**: Verify folder structure in Google Drive matches expected format
- **Import Errors**: Ensure all packages in `requirements.txt` are installed
- **Slow Loading**: First load from Google Drive may take time, subsequent loads are cached

### **Support Files**
- `google_drive_utils.py`: Core Google Drive integration
- `GOOGLE_DRIVE_SETUP.md`: Detailed setup instructions
- `requirements.txt`: All required Python packages
- `.gitignore`: Excludes sensitive files from version control

---

**Built with ❤️ using Streamlit, Plotly, and Google Drive API**

*For technical support or feature requests, please refer to the individual file documentation or the main project README.*
