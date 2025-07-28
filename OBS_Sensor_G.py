# OBS Sensor - Google Drive Version
import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import date, timedelta
import plotly.io as pio
from scipy.stats import zscore
from PIL import Image
import base64
import tempfile
import zipfile

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

# Sensor parameters
AVAILABLE_PARAMS = {
    'ambient_light': 'Ambient Light',
    'backscatter': 'Backscatter',
    'pressure_kpa': 'Pressure (kPa)',
    'water_temp': 'Temperature (°C)'
}

if USE_GOOGLE_DRIVE and GOOGLE_DRIVE_ENABLED:
    # Google Drive configuration
    LOGO_PATH = "assets/logo_1.png"  # Relative path for deployment
else:
    # Local configuration
    OBS_BASE_PATH = "/Volumes/AMBITION/S4W/hydro_link/processed/obs"
    ATMOS_PATH = "/Volumes/AMBITION/S4W/hydro_link/processed/atmos/atm_site1/atm_s1_2023.csv"
    SENSOR_METADATA_PATH = "/Volumes/AMBITION/S4W/hydro_link/processed/sensor_metadata/sensor_metadata.csv"
    LOGO_PATH = "assets/logo_1.png"  # Relative path for deployment

st.set_page_config(page_title="OBS Sensor Data Viewer - Google Drive", layout="wide")

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
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        df.dropna(subset=['timestamp'], inplace=True)
        df.set_index('timestamp', inplace=True)
        df.sort_index(inplace=True)
    
    return df

@st.cache_data
def load_csv(file_path):
    df = pd.read_csv(file_path)
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
def load_atmos_from_drive(file_id):
    """Load atmospheric data from Google Drive"""
    if not GOOGLE_DRIVE_ENABLED:
        return None
        
    drive_manager = get_drive_manager()
    if not drive_manager.service:
        drive_manager.authenticate()
    
    df = drive_manager.download_file(file_id)
    if df is not None:
        df['Timestamps'] = pd.to_datetime(df['Timestamps'], errors='coerce')
        df.rename(columns={' kPa Atmospheric Pressure': 'atm_pressure'}, inplace=True)
        df.dropna(subset=['Timestamps', 'atm_pressure'], inplace=True)
        df = df.set_index('Timestamps').sort_index()
    
    return df

@st.cache_data
def load_atmos():
    df = pd.read_csv(ATMOS_PATH)
    df['Timestamps'] = pd.to_datetime(df['Timestamps'], errors='coerce')
    df.rename(columns={' kPa Atmospheric Pressure': 'atm_pressure'}, inplace=True)
    df.dropna(subset=['Timestamps', 'atm_pressure'], inplace=True)
    df = df.set_index('Timestamps').sort_index()
    return df

def encode_img_to_base64(image_path):
    try:
        with open(image_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
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
                <h1 style='margin-bottom: 0;'>📊 S4W Sensor Dashboard (Google Drive)</h1>
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
            <h1 style='margin-bottom: 0;'>📊 S4W Sensor Dashboard (Google Drive)</h1>
            <p style='margin-top: 5px; color: gray;font-size: 18px; font-weight: 500;'>From small sensors to big insights — monitor what matters ❤️</p>
        </div>
    """, unsafe_allow_html=True)

# ---------------------------
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
    
    # Find OBS folders (processed/obs structure)
    obs_folders = {}
    metadata_file_id = None
    atmos_file_id = None
    
    if 'processed' in folder_structure and folder_structure['processed']['type'] == 'folder':
        processed_contents = drive_manager.get_folder_structure(folder_structure['processed']['id'])
        
        # Find OBS folders
        if 'obs' in processed_contents and processed_contents['obs']['type'] == 'folder':
            obs_contents = drive_manager.get_folder_structure(processed_contents['obs']['id'])
            obs_folders = {name: content for name, content in obs_contents.items() 
                          if content['type'] == 'folder'}
        
        # Find metadata file
        if 'sensor_metadata' in processed_contents and processed_contents['sensor_metadata']['type'] == 'folder':
            metadata_contents = drive_manager.get_folder_structure(processed_contents['sensor_metadata']['id'])
            if 'sensor_metadata.csv' in metadata_contents:
                metadata_file_id = metadata_contents['sensor_metadata.csv']['id']
        
        # Find atmospheric data file
        if 'atmos' in processed_contents and processed_contents['atmos']['type'] == 'folder':
            atmos_contents = drive_manager.get_folder_structure(processed_contents['atmos']['id'])
            if 'atm_site1' in atmos_contents and atmos_contents['atm_site1']['type'] == 'folder':
                atm_site1_contents = drive_manager.get_folder_structure(atmos_contents['atm_site1']['id'])
                if 'atm_s1_2023.csv' in atm_site1_contents:
                    atmos_file_id = atm_site1_contents['atm_s1_2023.csv']['id']
    
    if not obs_folders:
        st.error("No OBS sensor folders found in Google Drive. Please check the folder structure.")
        st.stop()
    
    # Site selection
    sites = list(obs_folders.keys())
    selected_site = st.sidebar.selectbox("🌍 Select Site", sites)
    
    # Get CSV files in selected site
    site_contents = drive_manager.get_folder_structure(obs_folders[selected_site]['id'])
    csv_files = {name: content for name, content in site_contents.items() 
                if content['type'] == 'file' and name.endswith('.csv')}
    
    if not csv_files:
        st.error(f"No CSV files found in {selected_site}")
        st.stop()
    
    csv_file_names = list(csv_files.keys())
    selected_file = st.sidebar.selectbox("📂 Select a sensor data file", csv_file_names)
    selected_file_id = csv_files[selected_file]['id']
    
else:
    # Local file selection (fallback)
    sites = [d for d in os.listdir(OBS_BASE_PATH) if os.path.isdir(os.path.join(OBS_BASE_PATH, d)) and not d.startswith('.')]
    selected_site = st.sidebar.selectbox("🌍 Select Site", sites)
    obs_path = os.path.join(OBS_BASE_PATH, selected_site)
    csv_files = [f for f in os.listdir(obs_path) if f.endswith('.csv') and not f.startswith('.')]
    selected_file = st.sidebar.selectbox("📂 Select a sensor data file", csv_files)

# ---------------------------
# MAIN CONTENT
# ---------------------------
if selected_file:
    # Load data based on source
    if USE_GOOGLE_DRIVE and GOOGLE_DRIVE_ENABLED:
        with st.spinner("Loading data from Google Drive..."):
            df = load_csv_from_drive(selected_file_id)
            
            # Load atmospheric data
            if atmos_file_id:
                atmos_df = load_atmos_from_drive(atmos_file_id)
            else:
                st.warning("Atmospheric data not found. Water level calculations may not be accurate.")
                atmos_df = pd.DataFrame()  # Empty dataframe
            
            # Load metadata
            if metadata_file_id:
                metadata_df = load_metadata_from_drive(metadata_file_id)
            else:
                metadata_df = pd.DataFrame()  # Empty dataframe
                
        if df is None:
            st.error("Failed to load data from Google Drive")
            st.stop()
    else:
        df = load_csv(os.path.join(obs_path, selected_file))
        atmos_df = load_atmos()
        metadata_df = load_metadata()

    # Get sensor metadata (height)
    sensor_id = selected_file.split(".")[0]  # e.g., obs_s1_2023
    sensor_height = 0.0
    sensor_name = sensor_id
    
    if not metadata_df.empty:
        metadata_df['sensor_id'] = metadata_df['sensor_id'].astype(str)
        sensor_row = metadata_df[metadata_df['sensor_id'].str.contains(sensor_id)]
        sensor_height = sensor_row['sensor_height_m'].values[0] if not sensor_row.empty else 0.0

    # Process data for water level calculation
    if not atmos_df.empty:
        # Resample both to 15-min intervals
        df = df.resample("15min").mean()
        df = df.dropna(subset=['pressure'])  # Remove rows where sensor has no pressure
        obs_start, obs_end = df.index.min(), df.index.max()

        atmos_df = atmos_df.resample("15min").mean()
        atmos_df = atmos_df[obs_start:obs_end]  # Trim atmos to only where OBS has data

        # Inner join
        df = df.join(atmos_df, how="inner")

        # Remove obvious outliers in pressure which are below 5000
        df = df[df['pressure'] > 5000]

        # Convert pressure units and compute water level
        df['hydroP_mbar'] = (df['pressure'] / 10) - (df['atm_pressure'] * 10)
        df['water_level'] = ((df['hydroP_mbar']) / 98.0665) + sensor_height

    # Add converted columns for display
    df['pressure_kpa'] = df['pressure'] / 100.0
    df['water_temp'] = df['water_temp'] / 100.0

    # Sidebar parameter selection
    st.sidebar.markdown("### 📌 Parameters")
    all_params = list(AVAILABLE_PARAMS.keys()) + ['water_level']
    param_display = AVAILABLE_PARAMS.copy()
    param_display['water_level'] = 'Water Level (m)'
    selected_params = [p for p in all_params if p in df.columns and st.sidebar.checkbox(param_display[p], p == 'water_level')]

    st.sidebar.markdown("### 🗓️ Time Range")
    view_mode = st.sidebar.radio("View by:", ["Daily", "Weekly", "Monthly", "Custom"])

    min_date = df.index.min()
    max_date = df.index.max()
    start_of_bins = min_date

    if view_mode == "Custom":
        start = st.sidebar.date_input("Start Date", min_value=start_of_bins.date(), value=start_of_bins.date())
        end = st.sidebar.date_input("End Date", min_value=start_of_bins.date(), value=max_date.date())
        mask = (df.index.date >= start) & (df.index.date <= end)
        filtered_df = df[mask]
        bins = [start]
    else:
        if view_mode == "Daily":
            bins = df[start_of_bins:].resample('D').mean().index
            delta = timedelta(days=1)
        elif view_mode == "Weekly":
            bins = df[start_of_bins:].resample('W-MON').mean().index
            delta = timedelta(weeks=1)
        else:
            bins = df[start_of_bins:].resample('MS').mean().index
            delta = pd.DateOffset(months=1)

        if len(bins) == 0:
            st.warning("No data available after filtering or outlier cleaning. Please adjust your filters or select a different sensor.")
            st.stop()
            
        selected_bin = st.sidebar.selectbox("📆 Select time bin:", bins)
        selected_end = selected_bin + delta
        filtered_df = df[(df.index >= selected_bin) & (df.index < selected_end)]

    # Plotting and download
    st.markdown(f"<h4 style='font-weight: 600;'>📈 Sensor: {sensor_name}</h4>", unsafe_allow_html=True)
    
    if not selected_params:
        st.warning("Please select at least one parameter.")
    else:
        for param in selected_params:
            # Determine title based on time view
            if view_mode == "Daily":
                time_title = selected_bin.strftime("%B %d, %Y")
            elif view_mode == "Weekly":
                time_title = f"Week of {selected_bin.strftime('%B %d, %Y')}"
            elif view_mode == "Monthly":
                time_title = selected_bin.strftime("%B %Y")
            else:
                time_title = f"{start.strftime('%B %d, %Y')} – {end.strftime('%B %d, %Y')}"

            # Create plot
            fig = px.line(
                filtered_df,
                y=param,
                title=f"{param_display[param]} ({time_title})",
                labels={"value": param_display[param]},
                template="plotly_white"
            )
            fig.update_layout(xaxis_title="Time", yaxis_title=param_display[param], height=400)
            st.plotly_chart(fig, use_container_width=True)

            # Download button
            if st.button(f"⬇️ Download {param_display[param]} Plot as PNG", key=param):
                filename = f"{sensor_name}_{view_mode}_{param}.png"
                pio.write_image(fig, filename, format="png")
                with open(filename, "rb") as file:
                    st.download_button(
                        label="Download", data=file, file_name=filename, mime="image/png"
                    )

        # Batch download function
        def get_time_bins(view_mode_local):
            if view_mode_local == "Daily":
                bins_local = df.resample('D').mean().index
                delta_local = timedelta(days=1)
                fmt_local = "%Y-%m-%d"
                label_prefix = "Day"
            elif view_mode_local == "Weekly":
                bins_local = df.resample('W-MON').mean().index
                delta_local = timedelta(weeks=1)
                fmt_local = "Week of %B %d, %Y"
                label_prefix = "Week"
            elif view_mode_local == "Monthly":
                bins_local = df.resample('MS').mean().index
                delta_local = pd.DateOffset(months=1)
                fmt_local = "%B %Y"
                label_prefix = "Month"
            else:
                return [], None, None, None
            return bins_local, delta_local, fmt_local, label_prefix

        # Batch download (disabled for Google Drive version to avoid complexity)
        if not USE_GOOGLE_DRIVE and view_mode in ["Daily", "Weekly", "Monthly"] and st.sidebar.button(f"⬇️ Download All {view_mode} Plots"):
            with tempfile.TemporaryDirectory() as tmpdir:
                zip_path = os.path.join(tmpdir, f"{sensor_name}_{view_mode.lower()}_plots.zip")

                with zipfile.ZipFile(zip_path, 'w') as zipf:
                    bins, delta, fmt, label_prefix = get_time_bins(view_mode)

                    for param in selected_params:
                        for start_time in bins:
                            end_time = start_time + delta
                            sub_df = df[(df.index >= start_time) & (df.index < end_time)]

                            if sub_df.empty:
                                continue

                            title = f"{param_display[param]} ({start_time.strftime(fmt)})"
                            file_name = f"{sensor_name}_{param}_{start_time.strftime('%Y-%m-%d')}.png"

                            fig = px.line(
                                sub_df,
                                y=param,
                                title=title,
                                labels={"value": param_display[param]},
                                template="plotly_white"
                            )
                            fig.update_layout(xaxis_title="Time", yaxis_title=param_display[param], height=400)

                            file_path = os.path.join(tmpdir, file_name)
                            pio.write_image(fig, file_path)
                            zipf.write(file_path, arcname=file_name)

                with open(zip_path, "rb") as f:
                    st.download_button(
                        label=f"📦 Download All {view_mode} Plots",
                        data=f,
                        file_name=f"{sensor_name}_{view_mode.lower()}_plots.zip",
                        mime="application/zip"
                    )

        if USE_GOOGLE_DRIVE:
            st.info("💡 **Note**: Batch download feature is not available in Google Drive mode. Use individual plot downloads instead.")

st.markdown("---")
st.caption("Built with ❤️ using Streamlit and Plotly")
