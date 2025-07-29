# OBS Sensor - Google Drive Version
# Updated: 2025-07-29 Emergency Fix - Memory corruption resolution
# Version: 2.3 - Emergency cache clearing and memory management
import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import date, timedelta
import base64
import gc

# Import Google Drive utilities
try:
    from google_drive_utils import get_drive_manager
    GOOGLE_DRIVE_ENABLED = True
except ImportError as e:
    GOOGLE_DRIVE_ENABLED = False
    st.error(f"Google Drive integration not available. Error: {e}")
    st.info("Install required packages: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
except Exception as e:
    GOOGLE_DRIVE_ENABLED = False
    st.error(f"Unexpected error loading Google Drive utilities: {e}")
    st.info("Please check your configuration and try again.")

# ---------------------------
# CONFIGURATION
# ---------------------------
# Emergency cache clearing - clear all caches on startup
try:
    st.cache_data.clear()
    if hasattr(st.cache_resource, 'clear'):
        st.cache_resource.clear()
    gc.collect()  # Force garbage collection
except Exception as e:
    pass  # Silently handle any cache clearing errors

# Clear cache button in sidebar
if st.sidebar.button("🗑️ Clear Cache"):
    try:
        st.cache_data.clear()
        if hasattr(st.cache_resource, 'clear'):
            st.cache_resource.clear()
        gc.collect()
        st.rerun()
    except Exception as e:
        st.error(f"Cache clearing failed: {e}")
        st.rerun()

# Always use Google Drive for data sources
USE_GOOGLE_DRIVE = GOOGLE_DRIVE_ENABLED

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

st.set_page_config(page_title="OBS Sensor", layout="wide")

# ---------------------------
# UTILITY FUNCTIONS
# ---------------------------
@st.cache_data
def load_csv_from_drive(file_id):
    """Load CSV from Google Drive with memory management"""
    if not GOOGLE_DRIVE_ENABLED:
        return None
    
    try:
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
            
            # Memory optimization
            for col in df.select_dtypes(include=['float64']).columns:
                df[col] = pd.to_numeric(df[col], downcast='float')
        
        return df
    except Exception as e:
        st.error(f"Error loading data from Google Drive: {e}")
        return None

@st.cache_data
def load_csv(file_path):
    try:
        df = pd.read_csv(file_path)
        # All timestamps now standardized to YYYY-MM-DD HH:MM:SS format
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        df.dropna(subset=['timestamp'], inplace=True)
        df.set_index('timestamp', inplace=True)
        df.sort_index(inplace=True)
        
        # Memory optimization
        for col in df.select_dtypes(include=['float64']).columns:
            df[col] = pd.to_numeric(df[col], downcast='float')
        
        return df
    except Exception as e:
        st.error(f"Error loading CSV file: {e}")
        return None

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
        # All timestamps now standardized to YYYY-MM-DD HH:MM:SS format
        df['Timestamps'] = pd.to_datetime(df['Timestamps'], errors='coerce')
        df.rename(columns={' kPa Atmospheric Pressure': 'atm_pressure'}, inplace=True)
        df.dropna(subset=['Timestamps', 'atm_pressure'], inplace=True)
        df = df.set_index('Timestamps').sort_index()
    
    return df

@st.cache_data
def load_atmos():
    df = pd.read_csv(ATMOS_PATH)
    # All timestamps now standardized to YYYY-MM-DD HH:MM:SS format
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
    """, unsafe_allow_html=True)

# ---------------------------
# FILE SELECTION
# ---------------------------
if USE_GOOGLE_DRIVE and GOOGLE_DRIVE_ENABLED:
    # Google Drive file selection
    
    drive_manager = get_drive_manager()
    
    # Authenticate and test connection
    with st.spinner("Connecting to Google Drive..."):
        if not drive_manager.authenticate():
            st.error("❌ Failed to connect to Google Drive")
            st.stop()
        
        # Test basic access
        success, message = drive_manager.test_drive_access()
        if success:
            st.sidebar.success("🔗 Google Drive: Connected")
        else:
            st.error(f"🔗 **Google Drive Connection Failed**: {message}")
            st.stop()
    
    # Get folder structure (clear cache)
    with st.spinner("Loading Google Drive folder structure..."):
        folder_structure = drive_manager.get_folder_structure()
    
    # Clear any cached debugging output
    st.empty()
    
    # Clear cache to force fresh deployment
    obs_folders = {}
    metadata_file_id = None
    atmos_file_id = None
    
    # Handle both normal processed structure and virtual structure
    if 'obs' in folder_structure:
        if folder_structure['obs'].get('subfolders'):
            # Virtual structure - folders are directly accessible
            obs_folders = folder_structure['obs']['subfolders']
        elif folder_structure['obs']['type'] == 'folder':
            # Normal structure
            obs_contents = drive_manager.get_folder_structure(folder_structure['obs']['id'])
            obs_folders = {name: content for name, content in obs_contents.items() 
                          if content['type'] == 'folder'}
    elif 'processed' in folder_structure and folder_structure['processed']['type'] == 'folder':
        # Legacy processed structure
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
    
    # Handle virtual structure for atmos data
    if not atmos_file_id and 'atmos' in folder_structure:
        if folder_structure['atmos'].get('subfolders'):
            # Virtual structure - check for atm_site1 directly
            atm_folders = folder_structure['atmos']['subfolders']
            if 'atm_site1' in atm_folders:
                atm_site1_contents = drive_manager.get_folder_structure(atm_folders['atm_site1']['id'])
                if 'atm_s1_2023.csv' in atm_site1_contents:
                    atmos_file_id = atm_site1_contents['atm_s1_2023.csv']['id']
        else:
            # Try direct folder access as fallback
            try:
                atmos_direct = drive_manager.get_folder_structure(folder_structure['atmos']['id'])
                if 'atm_site1' in atmos_direct:
                    atm_site1_contents = drive_manager.get_folder_structure(atmos_direct['atm_site1']['id'])
                    if 'atm_s1_2023.csv' in atm_site1_contents:
                        atmos_file_id = atm_site1_contents['atm_s1_2023.csv']['id']
            except Exception:
                pass  # Silently handle access errors
    
    if not obs_folders:
        st.error("🔍 No OBS sensor folders found in Google Drive. Please check your folder structure and permissions.")
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
    try:
        # Load data based on source
        if USE_GOOGLE_DRIVE and GOOGLE_DRIVE_ENABLED:
            with st.spinner("Loading data from Google Drive..."):
                df = load_csv_from_drive(selected_file_id)
                
                # Load atmospheric data
                if atmos_file_id:
                    atmos_df = load_atmos_from_drive(atmos_file_id)
                else:
                    st.info("ℹ️ **Atmospheric data unavailable** - Water level will be displayed as absolute pressure readings")
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
            if df is None:
                st.error("Failed to load local data")
                st.stop()
            atmos_df = load_atmos()
            metadata_df = load_metadata()
            
    except Exception as e:
        st.error(f"Critical error loading data: {e}")
        st.info("Try clearing the cache using the button in the sidebar, or refresh the page.")
        st.stop()

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
            # Calendar view for daily selection (like TB Sensor)
            st.sidebar.markdown("📅 Select Date:")
            selected_date = st.sidebar.date_input(
                "Choose date:", 
                value=start_of_bins.date(),
                min_value=start_of_bins.date(),
                max_value=max_date.date()
            )
            selected_bin = pd.Timestamp(selected_date)
            delta = timedelta(days=1)
        elif view_mode == "Weekly":
            bins = df[start_of_bins:].resample('W-MON').mean().index
            if len(bins) == 0:
                st.warning("No data available after filtering or outlier cleaning. Please adjust your filters or select a different sensor.")
                st.stop()
            selected_bin = st.sidebar.selectbox("📆 Select week:", bins)
            delta = timedelta(weeks=1)
        else:  # Monthly
            bins = df[start_of_bins:].resample('MS').mean().index
            if len(bins) == 0:
                st.warning("No data available after filtering or outlier cleaning. Please adjust your filters or select a different sensor.")
                st.stop()
            selected_bin = st.sidebar.selectbox("📆 Select month:", bins)
            delta = pd.DateOffset(months=1)

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

            # HTML Download only
            html_filename = f"{sensor_name}_{view_mode}_{param}.html"
            try:
                html_string = fig.to_html(include_plotlyjs='cdn')
                st.download_button(
                    f"📄 Download {param_display[param]} as HTML",
                    html_string.encode(), 
                    file_name=html_filename, 
                    mime="text/html",
                    key=param,
                    help="Download interactive HTML plot file."
                )
            except Exception as e:
                st.error(f"Download failed: {str(e)}")

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

        # Note: Batch download feature disabled to avoid complexity and memory issues
        st.info("💡 **Note**: Download individual plots as interactive HTML files.")

st.markdown("---")
st.caption("Built with ❤️ using Streamlit and Plotly")
