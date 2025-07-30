# HOBO Sensor - GitHub Version (Converted from Google Drive backup)
# Unique Design: Checkbox selection for multiple parameters
import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime, timedelta
import base64

# ---------------------------
# CONFIGURATION
# ---------------------------
st.set_page_config(page_title="🌡️ HOBO Sensor", page_icon="🌡️", layout="wide")

# Data paths - GitHub storage
HOBO_BASE_PATH = "processed/hobo"
SENSOR_METADATA_PATH = "processed/sensor_metadata/sensor_metadata.csv"
LOGO_PATH = "assets/logo_1.png"

# ---------------------------
# UTILITY FUNCTIONS
# ---------------------------
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
def load_metadata_csv(file_path):
    """Load metadata CSV"""
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        st.warning(f"Could not load metadata: {e}")
        return pd.DataFrame()

@st.cache_data
def encode_img_to_base64(image_path):
    try:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        # Return empty string if logo not found
        return ""

# ---------------------------
# LOGO HEADER
# ---------------------------
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
# FILE SELECTION (GitHub format)
# ---------------------------
try:
    # Get available sites
    sites = [d for d in os.listdir(HOBO_BASE_PATH) if os.path.isdir(os.path.join(HOBO_BASE_PATH, d)) and not d.startswith('.')]
    
    if not sites:
        st.error("🔍 No HOBO sensor sites found in the processed/hobo folder.")
        st.stop()
        
    selected_site = st.sidebar.selectbox("🌍 Select HOBO Site", sites)
    
    # Get CSV files in selected site
    site_path = os.path.join(HOBO_BASE_PATH, selected_site)
    csv_files = [f for f in os.listdir(site_path) if f.endswith('.csv') and not f.startswith('.')]
    
    if not csv_files:
        st.error(f"📁 No CSV files found in {selected_site}")
        st.stop()
        
    selected_file = st.sidebar.selectbox("📂 Select data file", csv_files)
    
except Exception as e:
    st.error(f"Error accessing data files: {e}")
    st.info("Please check that the processed folder is properly uploaded to your GitHub repository.")
    st.stop()

# ---------------------------
# MAIN CONTENT
# ---------------------------
if selected_file:
    # Load data
    file_path = os.path.join(HOBO_BASE_PATH, selected_site, selected_file)
    df = load_csv(file_path)
    
    if df is None:
        st.error("Failed to load sensor data")
        st.stop()
    
    # Load metadata
    metadata_df = load_metadata_csv(SENSOR_METADATA_PATH)
    
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

    # UNIQUE HOBO DESIGN: Checkbox selection for multiple parameters
    st.sidebar.markdown("### 📌 Parameters")
    available_params = [p for p in param_display if p in df.columns]
    selected_params = [p for p in available_params if st.sidebar.checkbox(param_display[p], p == 'water_level_m')]

    # UNIQUE HOBO DESIGN: Time Range options (Daily, Weekly, Monthly, Custom)
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
            # Calendar view for daily selection (like TB Sensor)
            st.sidebar.markdown("📅 Select Date:")
            selected_date = st.sidebar.date_input(
                "Choose date:", 
                value=min_date.date(),
                min_value=min_date.date(),
                max_value=max_date.date()
            )
            selected_bin = pd.Timestamp(selected_date)
            delta = timedelta(days=1)
        elif view_mode == "Weekly":
            bins = df.resample('W-MON').mean().index
            selected_bin = st.sidebar.selectbox("📆 Select week:", bins)
            delta = timedelta(weeks=1)
        else:  # Monthly
            bins = df.resample('MS').mean().index
            selected_bin = st.sidebar.selectbox("📆 Select month:", bins)
            delta = pd.DateOffset(months=1)

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
            fig.update_layout(xaxis_title="Time", yaxis_title=param_display[param], height=400)
            st.plotly_chart(fig, use_container_width=True)

            # HTML Download only
            html_filename = f"{sensor_id}_{view_mode}_{param}.html"
            try:
                html_string = fig.to_html(include_plotlyjs='cdn')
                st.download_button(
                    f"📄 Download {param_display[param]} as HTML",
                    html_string.encode(), 
                    file_name=html_filename, 
                    mime="text/html",
                    key=f"html_{param}",
                    help="Download interactive HTML plot file."
                )
            except Exception as e:
                st.error(f"Download failed: {str(e)}")

        st.info("💡 **Note**: Download individual plots as interactive HTML files.")

st.markdown("---")
st.caption("Built with ❤️ using Streamlit • GitHub Version - Fast & Reliable")
