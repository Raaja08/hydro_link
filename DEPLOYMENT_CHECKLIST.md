# 🚀 Deployment Checklist for Hydro Link Dashboard

## ✅ **Pre-Deployment Setup**

### **1. Google Cloud Setup (5 minutes)**
- [ ] Create Google Cloud project: `hydro-link-dashboard`
- [ ] Enable Google Drive API
- [ ] Create Service Account: `hydro-link-app-service`
- [ ] Download `service_account.json` key file
- [ ] Add service account email to Google Drive folder sharing (Viewer access)

### **2. Local Testing**
- [ ] Place `service_account.json` in project root
- [ ] Test locally: `streamlit run pages/3_TB_Sensor_G.py`
- [ ] Verify Google Drive toggle works without login
- [ ] Test all three dashboards (TB, HOBO, OBS)

### **3. GitHub Repository**
- [ ] Ensure `service_account.json` is in `.gitignore`
- [ ] Push code to GitHub repository
- [ ] Verify no sensitive files are committed

## 🌐 **Streamlit Cloud Deployment**

### **4. Deploy to Streamlit Cloud**
- [ ] Go to [share.streamlit.io](https://share.streamlit.io)
- [ ] Connect GitHub repository
- [ ] Set main file: `pages/3_TB_Sensor_G.py` (or choose which dashboard)
- [ ] Deploy app

### **5. Configure Secrets**
- [ ] In Streamlit Cloud dashboard → Settings → Secrets
- [ ] Copy entire `service_account.json` content
- [ ] Add as secrets in TOML format:
```toml
[service_account]
type = "service_account"
project_id = "your_project_id"
private_key_id = "your_key_id"
private_key = "-----BEGIN PRIVATE KEY-----\nYOUR_KEY\n-----END PRIVATE KEY-----\n"
client_email = "your_service_account@project.iam.gserviceaccount.com"
client_id = "your_client_id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "your_cert_url"
```

## 🧪 **Testing & Launch**

### **6. Post-Deployment Testing**
- [ ] Test Google Drive data loading
- [ ] Test all sensor types (TB, HOBO, OBS)
- [ ] Test different time ranges and data types
- [ ] Test plot downloads
- [ ] Test with different browsers/devices

### **7. User Access**
- [ ] Share public Streamlit URL with users
- [ ] Verify users can access without login
- [ ] Create user documentation/guide

## 📋 **Multiple Dashboard Deployment**

If you want to deploy all three dashboards separately:

### **TB Sensor Dashboard**
- Main file: `pages/3_TB_Sensor_G.py`
- URL: `your-app-tb.streamlit.app`

### **HOBO Sensor Dashboard**  
- Main file: `pages/2_HOBO_Sensor_G.py`
- URL: `your-app-hobo.streamlit.app`

### **OBS Sensor Dashboard**
- Main file: `OBS_Sensor_G.py`
- URL: `your-app-obs.streamlit.app`

## 🔧 **Alternative: Single Multi-Page App**

Create a main dashboard with navigation:

```python
# main_dashboard.py
import streamlit as st

st.set_page_config(page_title="S4W Sensor Dashboard", layout="wide")

st.sidebar.title("🌊 S4W Sensor Dashboard")
dashboard = st.sidebar.selectbox("Select Dashboard:", [
    "TB Sensor (Rainfall & Temperature)",
    "HOBO Sensor (Water Level)", 
    "OBS Sensor (Multi-parameter)"
])

if dashboard == "TB Sensor (Rainfall & Temperature)":
    exec(open('pages/3_TB_Sensor_G.py').read())
elif dashboard == "HOBO Sensor (Water Level)":
    exec(open('pages/2_HOBO_Sensor_G.py').read())
elif dashboard == "OBS Sensor (Multi-parameter)":
    exec(open('OBS_Sensor_G.py').read())
```

## 🎯 **Success Criteria**

Your deployment is successful when:
- [ ] ✅ Users can access the dashboard without any login
- [ ] ✅ Google Drive data loads automatically  
- [ ] ✅ All visualizations work correctly
- [ ] ✅ Plot downloads function properly
- [ ] ✅ App is responsive on mobile devices
- [ ] ✅ Multiple users can access simultaneously

## 🆘 **Support & Troubleshooting**

If you encounter issues:
1. Check `SERVICE_ACCOUNT_SETUP.md` for detailed instructions
2. Verify Google Drive folder sharing permissions
3. Test locally first before cloud deployment
4. Check Streamlit Cloud logs for error messages

## 🎉 **Go Live!**

Once all checkboxes are complete:
1. **Share the public URL** with your users
2. **Announce the launch** to your team/community
3. **Monitor usage** through Streamlit Cloud analytics
4. **Collect feedback** for future improvements

---

**🚀 Ready to deploy? Follow this checklist step by step, and you'll have a professional, public-facing sensor dashboard in under 30 minutes!**
