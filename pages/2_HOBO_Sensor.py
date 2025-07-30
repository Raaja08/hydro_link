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

# Data paths - pointing to your uploaded processed folder
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
# HEADER SECTION
# ---------------------------
logo_base64 = encode_img_to_base64(LOGO_PATH)

if logo_base64:
    st.markdown(f"""
        <div style='display: flex; justify-content: space-between; align-items: center; padding: 20px 10px 10px 10px;'>
            <div>
                <h1 style='margin-bottom: 0;'>🌡️ S4W Sensor Dashboard - HOBO Sensor</h1>
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
            <h1 style='margin-bottom: 0;'>🌡️ S4W Sensor Dashboard - HOBO Sensor</h1>
            <p style='margin-top: 5px; color: gray;font-size: 18px; font-weight: 500;'>From small sensors to big insights — monitor what matters ❤️</p>
        </div>
    """, unsafe_allow_html=True)

# ---------------------------
# SITE & FILE SELECTION
# ---------------------------

try:
    # Get available sites from local processed folder
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
# DATA LOADING & PROCESSING
# ---------------------------

if selected_file:
    file_path = os.path.join(HOBO_BASE_PATH, selected_site, selected_file)
    df = load_csv(file_path)
    
    if df is None or df.empty:
        st.error("Failed to load data or data is empty")
        st.stop()
    
    # Load metadata if available
    metadata_df = load_metadata_csv(SENSOR_METADATA_PATH)
    
    # Extract sensor information
    sensor_id = selected_file.split(".")[0]  # e.g., hobo_s1_2023
    
    # ---------------------------
    # SIDEBAR CONTROLS - UNIQUE HOBO DESIGN
    # ---------------------------
    
    # Define available parameters based on actual data columns
    available_params = []
    param_display = {}
    
    # Check for common HOBO sensor parameters
    if 'pressure_psi' in df.columns:
        available_params.append('pressure_psi')
        param_display['pressure_psi'] = 'Pressure (psi)'
    
    if 'water_temp_c' in df.columns:
        available_params.append('water_temp_c')
        param_display['water_temp_c'] = 'Water Temperature (°C)'
        
    if 'water_level_m' in df.columns:
        available_params.append('water_level_m')
        param_display['water_level_m'] = 'Water Level (m)'
        
    # Add any other numeric columns as potential parameters
    for col in df.columns:
        if col not in available_params and df[col].dtype in ['float64', 'int64']:
            available_params.append(col)
            param_display[col] = col.replace('_', ' ').title()
    
    if not available_params:
        st.error("No numeric parameters found in the data")
        st.stop()
    
    # Parameter selection with checkboxes (HOBO's unique feature)
    st.sidebar.markdown("### 📌 Parameters")
    selected_params = []
    
    # Default to first parameter if pressure_psi or water_level_m exists
    default_param = 'pressure_psi' if 'pressure_psi' in available_params else available_params[0]
    
    for param in available_params:
        if st.sidebar.checkbox(param_display[param], param == default_param):
            selected_params.append(param)
    
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
            # Calendar view for daily selection
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
            # Show all months that have timestamps (TB Sensor format)
            monthly_groups = df.groupby(pd.Grouper(freq='MS')).size()
            bins = monthly_groups[monthly_groups > 0].index
            bin_options = [f"{bin.strftime('%Y %B')}" for bin in bins]
            selected_bin_str = st.sidebar.selectbox("📆 Select month:", bin_options)
            selected_bin = bins[bin_options.index(selected_bin_str)]
            delta = pd.DateOffset(months=1)

        selected_end = selected_bin + delta
        filtered_df = df[(df.index >= selected_bin) & (df.index < selected_end)]

        if view_mode == "Monthly":
            time_title = selected_bin.strftime("%B %Y")
        elif view_mode == "Weekly":
            time_title = f"Week of {selected_bin.strftime('%B %d, %Y')}"
        else:
            time_title = selected_bin.strftime("%B %d, %Y")
    
    # ---------------------------
    # PLOTTING & VISUALIZATION
    # ---------------------------
    
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
            xaxis_title = "Date" if view_mode == "Monthly" else "Time"
            
            # Set y-axis range: start from 0 for water level if no negative values
            yaxis_config = {"title": param_display[param]}
            if param == 'water_level_m' and param in filtered_df.columns:
                min_val = filtered_df[param].min()
                if pd.notna(min_val) and min_val >= 0:
                    max_val = filtered_df[param].max()
                    if pd.notna(max_val):
                        yaxis_config["range"] = [0, max_val * 1.1]  # 10% padding above max
            
            fig.update_layout(xaxis_title=xaxis_title, yaxis=yaxis_config, height=400)
            st.plotly_chart(fig, use_container_width=True)

            # Download options
            col1, col2 = st.columns(2)
            
            # HTML Download functionality
            html_filename = f"{sensor_id}_{view_mode}_{param}.html"
            try:
                html_string = fig.to_html(include_plotlyjs='cdn')
                with col1:
                    st.download_button(
                        f"📄 Download {param_display[param]} as HTML",
                        html_string.encode(), 
                        file_name=html_filename, 
                        mime="text/html",
                        key=f"html_{param}",
                        help="Download interactive HTML plot file."
                    )
            except Exception as e:
                with col1:
                    st.error(f"HTML download failed: {str(e)}")
            
            # PNG Download
            png_filename = f"{sensor_id}_{view_mode}_{param}.png"
            try:
                png_bytes = fig.to_image(format="png", width=1200, height=600)
                with col2:
                    st.download_button(
                        f"🖼️ Download {param_display[param]} as PNG",
                        png_bytes,
                        file_name=png_filename,
                        mime="image/png",
                        key=f"png_{param}",
                        help="Download static PNG image file."
                    )
            except Exception as e:
                with col2:
                    st.error(f"PNG download failed: {str(e)}")

        st.info("💡 **Note**: Download individual plots as HTML (interactive) or PNG (static) files.")

st.markdown("---")
st.caption("Built with ❤️ using Streamlit • GitHub Version - Fast & Reliable")
