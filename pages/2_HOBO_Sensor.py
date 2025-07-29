# HOBO Sensor - Google Drive Version
import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime, timedelta
import base64

# Import Google Drive utilities
try:
    from google_drive_utils import get_drive_manager
    GOOGLE_DRIVE_ENABLED = True
except ImportError:
    GOOGLE_DRIVE_ENABLED = False
    st.warning("Google Drive integration not available. Install required packages: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")

# ---------------------------
# CONFIGURATION
# ---------------------------
# Toggle between local and Google Drive data sources
USE_GOOGLE_DRIVE = st.sidebar.checkbox("📁 Use Google Drive Data", value=True, help="Check to load data from Google Drive instead of local storage")

# Google Drive folder IDs
LOGO_FOLDER_ID = "1IQcw6pn4x9VFIRkafzLbfChbRzfQPz7K"  # Logo assets folder

if USE_GOOGLE_DRIVE and GOOGLE_DRIVE_ENABLED:
    # Google Drive configuration
    LOGO_PATH = "assets/logo_1.png"  # Relative path for deployment
else:
    # Local configuration
    HOBO_PATH = "/Volumes/AMBITION/S4W/hydro_link/processed/hobo"
    SENSOR_METADATA_PATH = "/Volumes/AMBITION/S4W/hydro_link/processed/sensor_metadata/sensor_metadata.csv"
    LOGO_PATH = "assets/logo_1.png"  # Relative path for deployment

st.set_page_config(page_title="🌡️ HOBO Sensor", page_icon="🌡️", layout="wide")

# ---------------------------
# UTILITY FUNCTIONS
# ---------------------------
@st.cache_data
def load_csv_from_drive(file_id):
    """Load CSV from Google Drive"""
    if not GOOGLE_DRIVE_ENABLED:
        return None
        
    drive_manager = get_drive_manager()
    if not drive_manager.service:
        drive_manager.authenticate()
    
    df = drive_manager.download_file(file_id)
    if df is not None:
        # All timestamps now standardized to YYYY-MM-DD HH:MM:SS format
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        df.dropna(subset=['timestamp'], inplace=True)
        df.set_index('timestamp', inplace=True)
        df.sort_index(inplace=True)
    
    return df

@st.cache_data
def load_csv(file_path):
    df = pd.read_csv(file_path)
    # All timestamps now standardized to YYYY-MM-DD HH:MM:SS format
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df.dropna(subset=['timestamp'], inplace=True)
    df.set_index('timestamp', inplace=True)
    df.sort_index(inplace=True)
    return df

@st.cache_data
def load_metadata_from_drive(file_id):
    """Load metadata CSV from Google Drive"""
    if not GOOGLE_DRIVE_ENABLED:
        return None
        
    drive_manager = get_drive_manager()
    if not drive_manager.service:
        drive_manager.authenticate()
    
    return drive_manager.download_file(file_id)

@st.cache_data
def load_metadata():
    return pd.read_csv(SENSOR_METADATA_PATH)

@st.cache_data
def encode_img_to_base64(image_path):
    try:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        # Return empty string if logo not found
        return ""

def load_logo_from_google_drive(gd_manager, logo_folder_id, logo_filename="logo_1.png"):
    """Load logo from Google Drive using folder ID"""
    try:
        return gd_manager.load_logo_from_drive(logo_folder_id, logo_filename)
    except Exception as e:
        st.warning(f"⚠️ Could not load logo from Google Drive: {e}")
        return ""
    try:
        # Find the assets folder
        assets_folder_id = gd_manager.find_folder_by_name(logo_folder_path)
        if not assets_folder_id:
            return ""
        
        # Find the logo file in assets folder
        logo_file_id = gd_manager.find_file_by_name(logo_filename, assets_folder_id)
        if not logo_file_id:
            return ""
        
        # Download logo file
        logo_bytes = gd_manager.download_image_file(logo_file_id)
        if logo_bytes:
            return base64.b64encode(logo_bytes).decode()
        
    except Exception as e:
        st.warning(f"⚠️ Could not load logo from Google Drive: {e}")
    
    return ""

# ---------------------------
# LOGO HEADER
# ---------------------------
logo_base64 = ""

# Try to load logo from Google Drive first, then fallback to local
if USE_GOOGLE_DRIVE and GOOGLE_DRIVE_ENABLED:
    try:
        drive_manager = get_drive_manager()
        if drive_manager.authenticate():
            logo_base64 = load_logo_from_google_drive(drive_manager, LOGO_FOLDER_ID)
    except Exception as e:
        st.warning(f"⚠️ Could not load logo from Google Drive: {e}")

# Fallback to local logo if Google Drive fails
if not logo_base64:
    logo_base64 = encode_img_to_base64(LOGO_PATH)

if logo_base64:
    st.markdown(f"""
        <div style='display: flex; justify-content: space-between; align-items: center; padding: 20px 10px 10px 10px;'>
            <div>
                <h1 style='margin-bottom: 0;'>🌊 S4W Sensor Dashboard</h1>
                <p style='margin-top: 5px; color: gray;font-size: 18px; font-weight: 500;'>From small sensors to big insights — monitor what matters ❤️</p>
            </div>
            <div>
                <img src='data:image/png;base64,{logo_base64}' style='height:100px;'/>
            </div>
        </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <div style='padding: 20px 10px 10px 10px;'>
            <h1 style='margin-bottom: 0;'>🌊 S4W Sensor Dashboard</h1>
            <p style='margin-top: 5px; color: gray;font-size: 18px; font-weight: 500;'>From small sensors to big insights — monitor what matters ❤️</p>
        </div>
    """, unsafe_allow_html=True)# ---------------------------
# FILE SELECTION
# ---------------------------
if USE_GOOGLE_DRIVE and GOOGLE_DRIVE_ENABLED:
    # Google Drive file selection
    st.sidebar.markdown("### 📁 Google Drive Data Source")
    
    drive_manager = get_drive_manager()
    if not drive_manager.service:
        if drive_manager.authenticate():
            st.sidebar.success("✅ Connected to Google Drive")
        else:
            st.sidebar.error("❌ Failed to connect to Google Drive")
            st.stop()
    
    # Get folder structure
    with st.spinner("Loading Google Drive folder structure..."):
        folder_structure = drive_manager.get_folder_structure()
    
    # Find HOBO folders (processed/hobo structure or virtual structure)
    hobo_folders = {}
    metadata_file_id = None
    
    # Handle both normal processed structure and virtual structure
    if 'hobo' in folder_structure:
        if folder_structure['hobo'].get('subfolders'):
            # Virtual structure - folders are directly accessible
            hobo_folders = folder_structure['hobo']['subfolders']
        elif folder_structure['hobo']['type'] == 'folder':
            # Normal structure
            hobo_contents = drive_manager.get_folder_structure(folder_structure['hobo']['id'])
            hobo_folders = {name: content for name, content in hobo_contents.items() 
                           if content['type'] == 'folder'}
    elif 'processed' in folder_structure and folder_structure['processed']['type'] == 'folder':
        # Legacy processed structure
        processed_contents = drive_manager.get_folder_structure(folder_structure['processed']['id'])
        
        # Find HOBO folders
        if 'hobo' in processed_contents and processed_contents['hobo']['type'] == 'folder':
            hobo_contents = drive_manager.get_folder_structure(processed_contents['hobo']['id'])
            hobo_folders = {name: content for name, content in hobo_contents.items() 
                           if content['type'] == 'folder'}
        
        # Find metadata file
        if 'sensor_metadata' in processed_contents and processed_contents['sensor_metadata']['type'] == 'folder':
            metadata_contents = drive_manager.get_folder_structure(processed_contents['sensor_metadata']['id'])
            if 'sensor_metadata.csv' in metadata_contents:
                metadata_file_id = metadata_contents['sensor_metadata.csv']['id']
    
    if not hobo_folders:
        st.error("No HOBO sensor folders found in Google Drive. Please check the folder structure.")
        st.stop()
    
    # Site selection
    sites = list(hobo_folders.keys())
    selected_site = st.sidebar.selectbox("🌍 Select HOBO Site", sites)
    
    # Get CSV files in selected site
    site_contents = drive_manager.get_folder_structure(hobo_folders[selected_site]['id'])
    csv_files = {name: content for name, content in site_contents.items() 
                if content['type'] == 'file' and name.endswith('.csv')}
    
    if not csv_files:
        st.error(f"No CSV files found in {selected_site}")
        st.stop()
    
    csv_file_names = list(csv_files.keys())
    selected_file = st.sidebar.selectbox("📂 Select data file", csv_file_names)
    selected_file_id = csv_files[selected_file]['id']
    
else:
    # Local file selection (fallback)
    sites = [d for d in os.listdir(HOBO_PATH) if os.path.isdir(os.path.join(HOBO_PATH, d)) and not d.startswith('.')]
    selected_site = st.sidebar.selectbox("🌍 Select HOBO Site", sites)

    site_path = os.path.join(HOBO_PATH, selected_site)
    csv_files = [f for f in os.listdir(site_path) if f.endswith('.csv') and not f.startswith('.')]
    selected_file = st.sidebar.selectbox("📂 Select data file", csv_files)

# ---------------------------
# MAIN CONTENT
# ---------------------------
if selected_file:
    # Load data based on source
    if USE_GOOGLE_DRIVE and GOOGLE_DRIVE_ENABLED:
        with st.spinner("Loading data from Google Drive..."):
            df = load_csv_from_drive(selected_file_id)
            if metadata_file_id:
                metadata_df = load_metadata_from_drive(metadata_file_id)
            else:
                metadata_df = pd.DataFrame()  # Empty dataframe if no metadata
        if df is None:
            st.error("Failed to load data from Google Drive")
            st.stop()
    else:
        df = load_csv(os.path.join(site_path, selected_file))
        metadata_df = load_metadata()

    sensor_id = selected_file.replace(".csv", "")
    
    # Get sensor height from metadata
    sensor_height = 0.0
    if not metadata_df.empty:
        metadata_df['sensor_id'] = metadata_df['sensor_id'].astype(str)
        sensor_row = metadata_df[metadata_df['sensor_id'].str.contains(sensor_id)]
        sensor_height = sensor_row['sensor_height_m'].values[0] if not sensor_row.empty else 0.0

    # Parameter display mapping
    param_display = {
        'pressure_psi': 'Pressure (psi)',
        'water_level_m': 'Water Level (m)',
        'water_temp_c': 'Water Temperature (°C)'
    }

    # Calculate water level from pressure if not available
    if 'water_level_m' not in df.columns and 'pressure_psi' in df.columns:
        df['water_level_m'] = ((df['pressure_psi'] * 6.89476) / 98.0665) + sensor_height

    st.sidebar.markdown("### 📌 Parameters")
    available_params = [p for p in param_display if p in df.columns]
    selected_params = [p for p in available_params if st.sidebar.checkbox(param_display[p], p == 'water_level_m')]

    st.sidebar.markdown("### 🗓️ Time Range")
    view_mode = st.sidebar.radio("View by:", ["Daily", "Weekly", "Monthly", "Custom"])

    min_date = df.index.min()
    max_date = df.index.max()

    if view_mode == "Custom":
        start = st.sidebar.date_input("Start Date", min_value=min_date.date(), value=min_date.date())
        end = st.sidebar.date_input("End Date", min_value=min_date.date(), value=max_date.date())
        mask = (df.index.date >= start) & (df.index.date <= end)
        filtered_df = df[mask]
        time_title = f"{start.strftime('%b %d, %Y')} to {end.strftime('%b %d, %Y')}"
    else:
        if view_mode == "Daily":
            bins = df.resample('D').mean().index
            delta = timedelta(days=1)
        elif view_mode == "Weekly":
            bins = df.resample('W-MON').mean().index
            delta = timedelta(weeks=1)
        else:
            bins = df.resample('MS').mean().index
            delta = pd.DateOffset(months=1)

        selected_bin = st.sidebar.selectbox("📆 Select time bin:", bins)
        selected_end = selected_bin + delta
        filtered_df = df[(df.index >= selected_bin) & (df.index < selected_end)]

        if view_mode == "Monthly":
            time_title = selected_bin.strftime("%B %Y")
        elif view_mode == "Weekly":
            time_title = f"Week of {selected_bin.strftime('%B %d, %Y')}"
        else:
            time_title = selected_bin.strftime("%B %d, %Y")
    
    st.markdown(f"<h4 style='font-weight: 600;'>📈 Sensor: {sensor_id}</h4>", unsafe_allow_html=True)

    if not selected_params:
        st.warning("Please select at least one parameter.")
    else:
        for param in selected_params:
            fig = px.line(
                filtered_df,
                y=param,
                title=f"{param_display[param]} ({time_title})",
                labels={"value": param_display[param]},
                template="plotly_white"
            )
            st.plotly_chart(fig, use_container_width=True)

            # HTML Download only (eliminates PNG memory issues)
            html_filename = f"{sensor_id}_{view_mode}_{param}.html"
            try:
                html_string = fig.to_html(include_plotlyjs='cdn')
                st.download_button(
                    f"📄 Download {param_display[param]} as HTML",
                    html_string.encode(), 
                    file_name=html_filename, 
                    mime="text/html",
                    key=f"html_{param}",
                    help="Download as HTML file. Open in browser to view interactively or save as PNG."
                )
                st.info("💡 **How to get PNG:** Open the downloaded HTML file in your browser, then right-click the plot and select 'Save image as...' to save as PNG.")
            except Exception as e:
                st.error(f"Download failed: {str(e)}")
                st.info("💡 **Alternative:** Right-click the plot above and select 'Save image as...' for direct PNG download.")

        st.info("💡 **Note**: For multiple plots, download each one individually as HTML, then convert to PNG using your browser.")

st.markdown("---")
st.caption("Built with ❤️ using Streamlit and Plotly")
