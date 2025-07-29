import streamlit as st
import pandas as pd
import plotly.express as px
import os
import gc
from datetime import datetime, timedelta
import plotly.io as pio
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

if USE_GOOGLE_DRIVE and GOOGLE_DRIVE_ENABLED:
    # Google Drive configuration
    LOGO_PATH = "assets/logo_1.png"  # Relative path for deployment
else:
    # Local configuration
    TB_PATH = "/Volumes/AMBITION/S4W/hydro_link/processed/tb"
    LOGO_PATH = "assets/logo_1.png"  # Relative path for deployment

st.set_page_config(page_title="🌧️ TB Sensor", page_icon="🌧️", layout="wide")

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
        
        # Convert empty strings in rainfall_mm to NaN
        df['rainfall_mm'] = pd.to_numeric(df['rainfall_mm'], errors='coerce')
        
        # Convert temperature_c to numeric if it exists
        if 'temperature_c' in df.columns:
            df['temperature_c'] = pd.to_numeric(df['temperature_c'], errors='coerce')
    
    return df

@st.cache_data
def load_csv(file_path):
    df = pd.read_csv(file_path)
    # All timestamps now standardized to YYYY-MM-DD HH:MM:SS format
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df.dropna(subset=['timestamp'], inplace=True)
    df.set_index('timestamp', inplace=True)
    df.sort_index(inplace=True)
    
    # Convert empty strings in rainfall_mm to NaN
    df['rainfall_mm'] = pd.to_numeric(df['rainfall_mm'], errors='coerce')
    
    # Convert temperature_c to numeric if it exists
    if 'temperature_c' in df.columns:
        df['temperature_c'] = pd.to_numeric(df['temperature_c'], errors='coerce')
    
    return df

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

def get_summary_stats(df, view_mode, plot_df, agg_type=None):
    """
    Calculate comprehensive summary statistics for the given data.
    Returns None if there's missing data in the plot data, otherwise returns stats dict.
    """
    # Check if there are any missing values in the plot data (following original guide)
    if plot_df[plot_df.columns[0]].isna().any():
        return None
    
    stats = {}
    
    if view_mode == "Daily":
        # Daily: Total, Maximum (with dynamic label based on aggregation)
        if 'rainfall_mm' in plot_df.columns:
            stats["Total rainfall (mm)"] = round(plot_df['rainfall_mm'].sum(), 2)
            
            # Dynamic maximum label based on aggregation type
            if agg_type == "15-min":
                stats["Maximum 15-min rainfall (mm)"] = round(plot_df['rainfall_mm'].max(), 2)
            else:
                stats["Maximum hourly rainfall (mm)"] = round(plot_df['rainfall_mm'].max(), 2)
        
    elif view_mode == "Monthly":
        # Monthly: Total, Max daily, Wet-dry days, Dry spell, Average
        if 'rainfall_mm' in plot_df.columns:
            stats["Total rainfall (mm)"] = round(plot_df['rainfall_mm'].sum(), 2)
            stats["Max daily rainfall (mm)"] = round(plot_df['rainfall_mm'].max(), 2)
            stats["Wet days"] = (plot_df['rainfall_mm'] > 0).sum()
            stats["Dry days"] = (plot_df['rainfall_mm'] == 0).sum()
            
            # Calculate longest dry spell (consecutive days with no rain)
            rainfall_series = plot_df['rainfall_mm']
            max_dry_spell = 0
            current_dry = 0
            for val in rainfall_series:
                if val == 0:
                    current_dry += 1
                    max_dry_spell = max(max_dry_spell, current_dry)
                else:
                    current_dry = 0
            stats["Longest dry spell (days)"] = max_dry_spell
            
            # Average from non-zero values only
            non_zero_vals = plot_df['rainfall_mm'][plot_df['rainfall_mm'] > 0]
            avg_rainfall = non_zero_vals.mean() if len(non_zero_vals) > 0 else 0
            stats["Average daily rainfall (mm)"] = round(avg_rainfall, 2) if avg_rainfall > 0 else 0
        
    elif view_mode == "Yearly":
        # Yearly: Annual total, Wettest month, Dry months, Wet-dry days, Longest dry spell
        if 'rainfall_mm' in plot_df.columns:
            stats["Annual total (mm)"] = round(plot_df['rainfall_mm'].sum(), 2)
            
            # Wettest month
            if plot_df['rainfall_mm'].max() > 0:
                wettest = plot_df['rainfall_mm'].idxmax()
                wettest_value = round(plot_df['rainfall_mm'].max(), 2)
                stats["Wettest month"] = f"{wettest.strftime('%B')} ({wettest_value} mm)"
            else:
                stats["Wettest month"] = "N/A"
                
            stats["Dry months"] = (plot_df['rainfall_mm'] == 0).sum()
            stats["Wet months"] = (plot_df['rainfall_mm'] > 0).sum()
            
            # Longest dry spell in days (convert from monthly data)
            # For yearly view, we need to estimate days from months
            rainfall_series = plot_df['rainfall_mm']
            max_dry_spell_months = 0
            current_dry = 0
            for val in rainfall_series:
                if val == 0:
                    current_dry += 1
                    max_dry_spell_months = max(max_dry_spell_months, current_dry)
                else:
                    current_dry = 0
            # Convert months to approximate days (30 days per month)
            stats["Longest dry spell (days)"] = max_dry_spell_months * 30
        
    elif view_mode == "Custom":
        # For custom view, follow original guide - check for any missing data
        if plot_df[plot_df.columns[0]].isna().any():
            return None
            
        if 'rainfall_mm' in plot_df.columns:
            stats["Total rainfall (mm)"] = round(plot_df['rainfall_mm'].sum(), 2)
            stats["Max rainfall (mm)"] = round(plot_df['rainfall_mm'].max(), 2)
            stats["Intervals with rainfall"] = (plot_df['rainfall_mm'] > 0).sum()
            stats["Average rainfall per interval (mm)"] = round(plot_df['rainfall_mm'].mean(), 2)
    
    return stats

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
    
    # Find TB folders (processed/tb structure or virtual structure)
    tb_folders = {}
    
    # Handle both normal processed structure and virtual structure
    if 'tb' in folder_structure:
        if folder_structure['tb'].get('subfolders'):
            # Virtual structure - folders are directly accessible
            tb_folders = folder_structure['tb']['subfolders']
        elif folder_structure['tb']['type'] == 'folder':
            # Normal structure
            tb_contents = drive_manager.get_folder_structure(folder_structure['tb']['id'])
            tb_folders = {name: content for name, content in tb_contents.items() 
                         if content['type'] == 'folder'}
    elif 'processed' in folder_structure and folder_structure['processed']['type'] == 'folder':
        # Legacy processed structure
        processed_contents = drive_manager.get_folder_structure(folder_structure['processed']['id'])
        if 'tb' in processed_contents and processed_contents['tb']['type'] == 'folder':
            tb_contents = drive_manager.get_folder_structure(processed_contents['tb']['id'])
            tb_folders = {name: content for name, content in tb_contents.items() 
                         if content['type'] == 'folder'}
    
    if not tb_folders:
        st.error("No TB sensor folders found in Google Drive. Please check the folder structure.")
        st.stop()
    
    # Site selection
    sites = list(tb_folders.keys())
    selected_site = st.sidebar.selectbox("🌍 Select TB Site", sites)
    
    # Get CSV files in selected site
    site_contents = drive_manager.get_folder_structure(tb_folders[selected_site]['id'])
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
    sites = [d for d in os.listdir(TB_PATH) if os.path.isdir(os.path.join(TB_PATH, d)) and not d.startswith('.')]
    selected_site = st.sidebar.selectbox("🌍 Select TB Site", sites)

    site_path = os.path.join(TB_PATH, selected_site)
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
        if df is None:
            st.error("Failed to load data from Google Drive")
            st.stop()
    else:
        df = load_csv(os.path.join(site_path, selected_file))
    
    sensor_id = selected_file.replace(".csv", "")

    st.sidebar.markdown("### 🗓️ Time Range")
    
    # Data type selector
    data_type = st.sidebar.radio("📊 Data Type:", ["Rainfall", "Temperature"])
    
    view_mode = st.sidebar.radio("View by:", ["Daily", "Monthly", "Yearly", "Custom"])

    min_date = df.index.min()
    max_date = df.index.max()
    
    # Set column name and aggregation function based on data type
    if data_type == "Rainfall":
        data_column = 'rainfall_mm'
        agg_func = lambda x: x.sum() if (len(x) > 0 and x.notna().any()) else None
    else:  # Temperature
        data_column = 'temperature_c'
        agg_func = lambda x: x.mean() if (len(x) > 0 and x.notna().any()) else None

    if view_mode == "Custom":
        start = st.sidebar.date_input("Start Date", min_value=min_date.date(), value=min_date.date())
        end = st.sidebar.date_input("End Date", min_value=min_date.date(), value=max_date.date())
        mask = (df.index.date >= start) & (df.index.date <= end)
        filtered_df = df[mask]
        
        # Determine aggregation based on date range
        date_diff = (end - start).days
        if date_diff <= 7:
            # Create continuous hourly index and reindex with NaN for missing periods
            full_range = pd.date_range(start=pd.Timestamp(start), end=pd.Timestamp(end) + pd.Timedelta(days=1), freq='h', inclusive='left')
            hourly_data = filtered_df.resample('H').agg({
                data_column: agg_func
            })
            plot_df = hourly_data.reindex(full_range)
            freq_text = "Hourly"
        elif date_diff <= 90:
            # Create continuous daily index
            full_range = pd.date_range(start=start, end=end, freq='D')
            daily_data = filtered_df.resample('D').agg({
                data_column: agg_func
            })
            plot_df = daily_data.reindex(full_range)
            freq_text = "Daily"
        else:
            # Create continuous monthly index
            full_range = pd.date_range(start=pd.Timestamp(start).replace(day=1), end=pd.Timestamp(end), freq='MS')
            monthly_data = filtered_df.resample('MS').agg({
                data_column: agg_func
            })
            plot_df = monthly_data.reindex(full_range)
            freq_text = "Monthly"
        
        time_title = f"{start.strftime('%b %d, %Y')} to {end.strftime('%b %d, %Y')} ({freq_text})"
        unit = "(mm)" if data_type == "Rainfall" else "(°C)"
        time_title = f"{data_type} {unit} - {time_title}"
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
        elif view_mode == "Monthly":
            # Show all months that have timestamps (including those with missing rainfall data)
            monthly_groups = df.groupby(pd.Grouper(freq='MS')).size()
            bins = monthly_groups[monthly_groups > 0].index
            # Format bins for better display
            bin_options = [f"{bin.strftime('%Y %B')}" for bin in bins]
            selected_bin_str = st.sidebar.selectbox("📆 Select month:", bin_options)
            # Convert back to timestamp
            selected_bin = bins[bin_options.index(selected_bin_str)]
            delta = pd.DateOffset(months=1)
        else:  # Yearly
            # Show all years that have timestamps (show year only)
            yearly_groups = df.groupby(pd.Grouper(freq='YS')).size()
            bins = yearly_groups[yearly_groups > 0].index
            # Format bins to show year only
            year_options = [bin.strftime('%Y') for bin in bins]
            selected_year_str = st.sidebar.selectbox("📆 Select year:", year_options)
            # Convert back to timestamp
            selected_bin = bins[year_options.index(selected_year_str)]
            delta = pd.DateOffset(years=1)

        selected_end = selected_bin + delta
        filtered_df = df[(df.index >= selected_bin) & (df.index < selected_end)]

        if view_mode == "Daily":
            # Create continuous time index for the selected day
            agg = st.sidebar.radio("Aggregation:", ["15-min", "Hourly"])
            freq = "15min" if agg == "15-min" else "h"
            
            # Create full continuous range for the selected day
            start_time = selected_bin
            end_time = selected_bin + timedelta(days=1)
            full_range = pd.date_range(start=start_time, end=end_time, freq=freq, inclusive='left')
            
            # Aggregate and reindex to show missing periods as NaN
            aggregated_data = filtered_df.resample(freq).agg({
                data_column: agg_func
            })
            plot_df = aggregated_data.reindex(full_range)
            
            # Create title
            interval_text = "15 min interval" if agg == "15-min" else "one hour interval"
            unit = "(mm)" if data_type == "Rainfall" else "(°C)"
            time_title = f"{data_type} {unit} (Daily: {selected_bin.strftime('%B %d, %Y')} - {interval_text})"
        elif view_mode == "Monthly":
            # Create continuous daily index for the selected month
            start_date = selected_bin
            if selected_bin.month == 12:
                end_date = selected_bin.replace(year=selected_bin.year+1, month=1, day=1)
            else:
                end_date = selected_bin.replace(month=selected_bin.month+1, day=1)
            
            full_range = pd.date_range(start=start_date, end=end_date, freq='D', inclusive='left')
            
            # Aggregate and reindex to show missing periods as NaN
            aggregated_data = filtered_df.resample('D').agg({
                data_column: agg_func
            })
            plot_df = aggregated_data.reindex(full_range)
            unit = "(mm)" if data_type == "Rainfall" else "(°C)"
            time_title = f"{data_type} {unit} (Monthly: {selected_bin.strftime('%B %Y')})"
        else:  # Yearly
            # Create continuous monthly index for the selected year
            start_date = selected_bin
            end_date = selected_bin.replace(year=selected_bin.year+1)
            
            full_range = pd.date_range(start=start_date, end=end_date, freq='MS', inclusive='left')
            
            # Aggregate and reindex to show missing periods as NaN
            aggregated_data = filtered_df.resample('MS').agg({
                data_column: agg_func
            })
            plot_df = aggregated_data.reindex(full_range)
            unit = "(mm)" if data_type == "Rainfall" else "(°C)"
            time_title = f"{data_type} {unit} (Yearly: {selected_bin.strftime('%Y')})"

    # ---------------------------
    # PLOTS
    # ---------------------------
    st.markdown(f"<h4 style='font-weight: 600;'>📈 Sensor: {sensor_id}</h4>", unsafe_allow_html=True)

    if plot_df.empty:
        st.warning("No data available for the selected time period.")
    else:
        # Check for missing data and show warning if found
        has_missing_data = plot_df.isna().any().any()
        if has_missing_data:
            if data_type == "Temperature":
                st.warning("⚠️ Some data points are missing for this period. Gaps will be visible in the plot.")
            else:
                st.warning("⚠️ Some data points are missing for this period. Gaps will be visible in the plot.")

        # For rainfall, create cumulative; for temperature, don't
        if data_type == "Rainfall":
            # Calculate cumulative rainfall - cumsum() naturally handles NaN values
            plot_df['cumulative_rainfall'] = plot_df[data_column].cumsum()
            show_cumulative = True
        else:
            show_cumulative = False
        
        # Create the appropriate plot type
        if data_type == "Rainfall":
            # Bar chart for rainfall - gaps will show as missing bars
            fig = px.bar(
                plot_df, y=data_column,
                title=time_title,
                labels={data_column: f"{data_type} ({'mm' if data_type == 'Rainfall' else '°C'})", "index": "Time"},
                template="plotly_white",
                color_discrete_sequence=["#1f77b4"]
            )
        else:
            # Line chart for temperature - gaps will show as disconnected lines
            fig = px.line(
                plot_df, y=data_column,
                title=time_title,
                labels={data_column: f"{data_type} ({'mm' if data_type == 'Rainfall' else '°C'})", "index": "Time"},
                template="plotly_white",
                color_discrete_sequence=["#1f77b4"]  # Same blue as rainfall
            )
            # Add markers to the line and ensure gaps are not connected
            fig.update_traces(mode='lines+markers', connectgaps=False)
        
        # Calculate y-axis max (higher than highest value)
        max_data = plot_df[data_column].max()
        
        if pd.isna(max_data):
            max_data = 1
            
        # For temperature, calculate proper y-axis range
        if data_type == "Temperature":
            min_data = plot_df[data_column].min()
            if not pd.isna(min_data):
                # If all temperatures are positive, start from 0
                if min_data >= 0:
                    y_min = 0
                    y_max = max_data * 1.2  # 20% padding above max
                else:
                    # If there are negative temperatures, add padding below min
                    y_min = min_data * 1.2  # 20% padding below min (makes it more negative)
                    y_max = max_data * 1.2  # 20% padding above max
            else:
                y_min = 0
                y_max = 1
        else:
            # For rainfall, keep existing logic
            if max_data == 0:
                max_data = 1
            y_min = 0
            y_max = max_data * 1.2  # 20% padding above max value
        
        # Add cumulative rainfall line only for rainfall data
        if show_cumulative:
            max_cumulative = plot_df['cumulative_rainfall'].max()
            if pd.isna(max_cumulative) or max_cumulative == 0:
                max_cumulative = 1
            y2_max = max_cumulative * 1.2
            
            fig.add_scatter(
                x=plot_df.index, 
                y=plot_df['cumulative_rainfall'], 
                mode="lines+markers",
                name="Cumulative Rainfall", 
                line=dict(color="#00509E"),
                yaxis="y2",
                connectgaps=False  # This ensures gaps are visible in the cumulative line
            )
        
        # Update layout - dual y-axis for rainfall, single for temperature
        if show_cumulative:
            # Dual y-axis layout for rainfall
            fig.update_layout(
                yaxis=dict(
                    title=f"{data_type} ({'mm' if data_type == 'Rainfall' else '°C'})",
                    side="left",
                    showgrid=True,
                    gridwidth=1,
                    gridcolor='lightgray',
                    range=[y_min, y_max]
                ),
                yaxis2=dict(
                    title="Cumulative Rainfall (mm)",
                    side="right",
                    overlaying="y",
                    showgrid=False,
                    range=[0, y2_max]
                ),
                xaxis_title="Date" if view_mode in ["Monthly", "Yearly"] else "Time",
                height=400,
                hovermode='x unified',
                legend=dict(
                    x=1.08,  # Move legend further right to avoid secondary y-axis
                    y=0.5,   # Center vertically
                    xanchor='left',
                    yanchor='middle'
                )
            )
        else:
            # Single y-axis layout for temperature
            fig.update_layout(
                yaxis=dict(
                    title=f"{data_type} ({'mm' if data_type == 'Rainfall' else '°C'})",
                    showgrid=True,
                    gridwidth=1,
                    gridcolor='lightgray',
                    range=[y_min, y_max]
                ),
                xaxis_title="Date" if view_mode in ["Monthly", "Yearly"] else "Time",
                height=400,
                hovermode='x unified'
            )
        
        # Special x-axis formatting for different view modes
        if view_mode == "Monthly":
            # Show all dates from first to last day of month
            fig.update_xaxes(
                dtick="D1",  # Show every day
                tickformat="%d",  # Show day numbers
                tickmode="linear",
                range=[plot_df.index.min(), plot_df.index.max()]  # Limit to actual month range
            )
        elif view_mode == "Yearly":
            # Show all months
            fig.update_xaxes(
                dtick="M1",  # Show every month
                tickformat="%b",  # Show month abbreviations
                tickmode="linear",
                range=[plot_df.index.min(), plot_df.index.max()]  # Limit to actual year range
            )

        st.plotly_chart(fig, use_container_width=True)

        # ---------------------------
        # SUMMARY STATS (Only for Rainfall)
        # ---------------------------
        if data_type == "Rainfall":
            # Pass aggregation type for daily view
            agg_type = None
            if view_mode == "Daily" and 'agg' in locals():
                agg_type = agg
            stats = get_summary_stats(filtered_df, view_mode, plot_df, agg_type)
            
            if stats is None:
                # Show warning for incomplete data
                st.warning("⚠️ Data is incomplete for this period. Summary statistics are not available.")
            else:
                st.markdown("### 📊 Summary Statistics")
                # Create DataFrame with explicit string dtype to avoid Arrow issues
                stats_df = pd.DataFrame(stats, index=["Value"]).T
                stats_df = stats_df.astype(str)  # Ensure all values are strings
                st.dataframe(stats_df, use_container_width=True)

        # ---------------------------
        # DOWNLOAD OPTIONS
        # ---------------------------
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🖼️ Download as PNG"):
                filename = f"{sensor_id}_{view_mode}_{time_title.replace(' ', '_').replace(',', '').replace(':', '_').replace('(', '').replace(')', '')}.png"
                
                # Use kaleido engine only (future-proof)
                try:
                    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                        # Reduced scale to prevent memory issues
                        pio.write_image(fig, tmp_file.name, scale=1.5, width=800, height=400)
                        with open(tmp_file.name, "rb") as f:
                            file_data = f.read()
                        os.unlink(tmp_file.name)
                        gc.collect()
                        st.download_button("📥 Download PNG", file_data, file_name=filename, mime="image/png")
                        st.success("✅ PNG downloaded successfully!")
                except Exception as e:
                    st.error("PNG download failed.")
                    st.info("💡 Try HTML download or manual methods: Right-click plot → 'Save image as...'")
                    # Clear any potential memory issues
                    gc.collect()
        
        with col2:
            if st.button("📄 Download as HTML"):
                html_filename = f"{sensor_id}_{view_mode}_{time_title.replace(' ', '_').replace(',', '').replace(':', '_').replace('(', '').replace(')', '')}.html"
                
                try:
                    html_string = fig.to_html(include_plotlyjs='cdn')
                    st.download_button(
                        "📄 Download Interactive HTML", 
                        html_string.encode(), 
                        file_name=html_filename, 
                        mime="text/html"
                    )
                    st.success("✅ Interactive HTML downloaded!")
                    st.info("💡 Open HTML file in browser, then screenshot or save as PNG.")
                except Exception as e:
                    st.error(f"HTML download failed: {str(e)}")

        # Note: Batch download feature disabled for Google Drive version to avoid complexity

        # Note: Batch download feature disabled for Google Drive version to avoid complexity
        st.info("💡 **Note**: Batch download feature is not available in Google Drive mode. Use individual plot downloads instead.")
