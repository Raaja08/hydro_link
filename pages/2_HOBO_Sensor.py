# HOBO Sensor - Simplified GitHub Version
# Updated: 2025-07-29 - Fast, reliable file-based storage
# Version: 3.1 - Clean deployment, no backup pages
import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import date, timedelta
import base64

# ---------------------------
# CONFIGURATION
# ---------------------------
st.set_page_config(page_title="HOBO Sensor", layout="wide")

# HOBO Sensor parameters - updated to match actual CSV columns
AVAILABLE_PARAMS = {
    'pressure_psi': 'Pressure (psi)',
    'water_temp_c': 'Water Temperature (°C)'
}

# Data paths - pointing to your uploaded processed folder
HOBO_BASE_PATH = "processed/hobo"
SENSOR_METADATA_PATH = "processed/sensor_metadata/sensor_metadata.csv"
LOGO_PATH = "assets/logo_1.png"

# ---------------------------
# UTILITY FUNCTIONS
# ---------------------------
@st.cache_data
def load_sensor_data(file_path):
    """Load CSV data with optimized processing"""
    try:
        df = pd.read_csv(file_path)
        # Standardize timestamps
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        df.dropna(subset=['timestamp'], inplace=True)
        df.set_index('timestamp', inplace=True)
        df.sort_index(inplace=True)
        
        # Memory optimization
        for col in df.select_dtypes(include=['float64']).columns:
            df[col] = pd.to_numeric(df[col], downcast='float')
        
        return df
    except Exception as e:
        st.error(f"Error loading {file_path}: {e}")
        return None

@st.cache_data
def load_metadata():
    """Load sensor metadata"""
    try:
        return pd.read_csv(SENSOR_METADATA_PATH)
    except Exception as e:
        st.warning(f"Could not load metadata: {e}")
        return pd.DataFrame()

def encode_img_to_base64(image_path):
    """Encode image to base64 for display"""
    try:
        with open(image_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        return ""

# ---------------------------
# HEADER
# ---------------------------
logo_base64 = encode_img_to_base64(LOGO_PATH)

if logo_base64:
    st.markdown(f"""
        <div style='display: flex; justify-content: space-between; align-items: center; padding: 20px 10px 10px 10px;'>
            <div>
                <h1 style='margin-bottom: 0;'>🌊 S4W Sensor Dashboard - HOBO Sensor</h1>
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
            <h1 style='margin-bottom: 0;'>🌊 S4W Sensor Dashboard - HOBO Sensor</h1>
            <p style='margin-top: 5px; color: gray;font-size: 18px; font-weight: 500;'>From small sensors to big insights — monitor what matters ❤️</p>
        </div>
    """, unsafe_allow_html=True)

# ---------------------------
# SITE & FILE SELECTION
# ---------------------------

# Get available sites
try:
    sites = [d for d in os.listdir(HOBO_BASE_PATH) if os.path.isdir(os.path.join(HOBO_BASE_PATH, d)) and not d.startswith('.')]
    
    if not sites:
        st.error("🔍 No sensor sites found in the processed/hobo folder.")
        st.stop()
        
    selected_site = st.sidebar.selectbox("🌍 Select Site", sites)
    
    # Get CSV files in selected site
    site_path = os.path.join(HOBO_BASE_PATH, selected_site)
    csv_files = [f for f in os.listdir(site_path) if f.endswith('.csv') and not f.startswith('.')]
    
    if not csv_files:
        st.error(f"📁 No CSV files found in {selected_site}")
        st.stop()
        
    selected_file = st.sidebar.selectbox("📂 Select a sensor data file", csv_files)
    
except Exception as e:
    st.error(f"Error accessing data files: {e}")
    st.info("Please check that the processed folder is properly uploaded to your GitHub repository.")
    st.stop()

# ---------------------------
# DATA LOADING & PROCESSING  
# ---------------------------

if selected_file:
    # Load main sensor data
    file_path = os.path.join(HOBO_BASE_PATH, selected_site, selected_file)
    df = load_sensor_data(file_path)
    
    if df is None:
        st.error("Failed to load sensor data")
        st.stop()
    
    # Load supporting data
    metadata_df = load_metadata()
    
    # Get sensor metadata
    sensor_id = selected_file.split(".")[0]  # e.g., hobo_s1_2023
    sensor_name = sensor_id
    
    # ---------------------------
    # PARAMETER & TIME SELECTION
    # ---------------------------
    
    # Sidebar parameter selection
    st.sidebar.markdown("### 📌 Parameters")
    selected_params = [p for p in AVAILABLE_PARAMS.keys() if p in df.columns and st.sidebar.checkbox(AVAILABLE_PARAMS[p], p == 'pressure_psi')]

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
    else:
        if view_mode == "Daily":
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
                st.warning("No data available after filtering. Please adjust your selection.")
                st.stop()
            selected_bin = st.sidebar.selectbox("📆 Select week:", bins)
            delta = timedelta(weeks=1)
        else:  # Monthly
            bins = df[start_of_bins:].resample('MS').mean().index
            if len(bins) == 0:
                st.warning("No data available after filtering. Please adjust your selection.")
                st.stop()
            selected_bin = st.sidebar.selectbox("📆 Select month:", bins)
            delta = pd.DateOffset(months=1)

        selected_end = selected_bin + delta
        filtered_df = df[(df.index >= selected_bin) & (df.index < selected_end)]

    # ---------------------------
    # PLOTTING & VISUALIZATION
    # ---------------------------
    
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
                title=f"{AVAILABLE_PARAMS[param]} ({time_title})",
                labels={"value": AVAILABLE_PARAMS[param]},
                template="plotly_white"
            )
            fig.update_layout(xaxis_title="Time", yaxis_title=AVAILABLE_PARAMS[param], height=400)
            st.plotly_chart(fig, use_container_width=True)

            # HTML Download
            html_filename = f"{sensor_name}_{view_mode}_{param}.html"
            try:
                html_string = fig.to_html(include_plotlyjs='cdn')
                st.download_button(
                    f"📄 Download {AVAILABLE_PARAMS[param]} as HTML",
                    html_string.encode(), 
                    file_name=html_filename, 
                    mime="text/html",
                    key=param,
                    help="Download interactive HTML plot file."
                )
            except Exception as e:
                st.error(f"Download failed: {str(e)}")

st.markdown("---")
st.caption("Built with ❤️ using Streamlit • GitHub Version - Fast & Reliable")
