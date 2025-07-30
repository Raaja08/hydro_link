# TB Sensor - GitHub Version (Converted from Google Drive backup)
# Unique Design: Radio button selection between Rainfall and Temperature
# Time options: Daily, Monthly, Yearly (with aggregation), Custom
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from datetime import datetime, timedelta, date
import base64
import calendar

# ---------------------------
# CONFIGURATION
# ---------------------------
st.set_page_config(page_title="🌧️ TB Sensor", page_icon="🌧️", layout="wide")

# Data paths - GitHub storage
TB_BASE_PATH = "processed/tb"
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
                stats["Max 15-min rainfall (mm)"] = round(plot_df['rainfall_mm'].max(), 2)
            else:
                stats["Max hourly rainfall (mm)"] = round(plot_df['rainfall_mm'].max(), 2)
        
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
                wettest_month_idx = plot_df['rainfall_mm'].idxmax()
                stats["Wettest month"] = f"{calendar.month_name[wettest_month_idx.month]} ({round(plot_df['rainfall_mm'].max(), 2)} mm)"
            else:
                stats["Wettest month"] = "No rainfall recorded"
                
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
    sites = [d for d in os.listdir(TB_BASE_PATH) if os.path.isdir(os.path.join(TB_BASE_PATH, d)) and not d.startswith('.')]
    
    if not sites:
        st.error("🔍 No TB sensor sites found in the processed/tb folder.")
        st.stop()
        
    selected_site = st.sidebar.selectbox("🌍 Select TB Site", sites)
    
    # Get CSV files in selected site
    site_path = os.path.join(TB_BASE_PATH, selected_site)
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
    file_path = os.path.join(TB_BASE_PATH, selected_site, selected_file)
    df = load_csv(file_path)
    
    if df is None:
        st.error("Failed to load sensor data")
        st.stop()
    
    sensor_id = selected_file.replace(".csv", "")

    # UNIQUE TB DESIGN: Radio button selection for parameters
    st.sidebar.markdown("### 📌 Parameters")
    data_type = st.sidebar.radio("Select data type:", ["Rainfall", "Temperature"])
    
    # UNIQUE TB DESIGN: Time Range with Yearly option
    st.sidebar.markdown("### 🗓️ Time Range")
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

    # Initialize aggregation option
    agg_option = None

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
            bins = df.resample('MS').mean().index
            selected_bin = st.sidebar.selectbox("📆 Select month:", bins)
            delta = pd.DateOffset(months=1)
            
        else:  # Yearly - UNIQUE TB FEATURE
            bins = df.resample('YS').mean().index
            selected_bin = st.sidebar.selectbox("📆 Select year:", bins)
            delta = pd.DateOffset(years=1)
            
            # UNIQUE YEARLY AGGREGATION OPTIONS
            if data_type == "Rainfall":
                agg_option = st.sidebar.radio("Aggregation:", ["15-min", "Hourly"])

        selected_end = selected_bin + delta
        filtered_df = df[(df.index >= selected_bin) & (df.index < selected_end)]

        if view_mode == "Daily":
            # For daily view, show hourly or 15-min data
            if data_type == "Rainfall":
                plot_df = filtered_df.resample('H').agg({data_column: agg_func})
            else:
                plot_df = filtered_df.resample('H').agg({data_column: agg_func})
            time_title = selected_bin.strftime("%B %d, %Y")
            
        elif view_mode == "Monthly":
            # For monthly view, show daily aggregation
            plot_df = filtered_df.resample('D').agg({data_column: agg_func})
            time_title = selected_bin.strftime("%B %Y")
            
        else:  # Yearly
            # For yearly view, show monthly aggregation
            plot_df = filtered_df.resample('MS').agg({data_column: agg_func})
            time_title = selected_bin.strftime("%Y")

    # ---------------------------
    # PLOTS (UNIQUE TB DESIGN)
    # ---------------------------
    st.markdown(f"<h4 style='font-weight: 600;'>📈 Sensor: {sensor_id}</h4>", unsafe_allow_html=True)

    if plot_df.empty:
        st.warning("No data available for the selected time period.")
    else:
        # Check for missing data and show warning if found
        has_missing_data = plot_df.isna().any().any()
        if has_missing_data:
            st.warning("⚠️ Some data points are missing in the selected time period. Statistics may be incomplete.")

        # Create the appropriate plot type based on data type
        if data_type == "Rainfall":
            # RAINFALL: Bar chart (light blue) with cumulative line
            fig = go.Figure()
            
            # Add bar chart for rainfall
            fig.add_trace(go.Bar(
                x=plot_df.index,
                y=plot_df[data_column],
                name="Rainfall",
                marker_color='lightblue',
                opacity=0.7
            ))
            
            # Add cumulative rainfall line
            cumulative_rainfall = plot_df[data_column].fillna(0).cumsum()
            fig.add_trace(go.Scatter(
                x=plot_df.index,
                y=cumulative_rainfall,
                mode='lines',
                name='Cumulative',
                line=dict(color='darkblue', width=2),
                yaxis='y2'
            ))
            
            # Dual y-axis layout
            fig.update_layout(
                title=f"Rainfall ({time_title})",
                xaxis_title="Time",
                yaxis=dict(title="Rainfall (mm)", side='left'),
                yaxis2=dict(title="Cumulative Rainfall (mm)", side='right', overlaying='y'),
                template="plotly_white",
                height=500
            )
        else:
            # TEMPERATURE: Line chart (orange)
            fig = px.line(
                plot_df,
                y=data_column,
                title=f"Temperature ({time_title})",
                template="plotly_white"
            )
            fig.update_traces(line_color='orange', line_width=2)
            fig.update_layout(
                xaxis_title="Time",
                yaxis_title="Temperature (°C)",
                height=500
            )

        # Special x-axis formatting for different view modes
        if view_mode == "Monthly":
            fig.update_layout(xaxis=dict(tickformat='%d %b'))
        elif view_mode == "Yearly":
            fig.update_layout(xaxis=dict(tickformat='%b %Y'))

        st.plotly_chart(fig, use_container_width=True)

        # ---------------------------
        # SUMMARY STATS (UNIQUE TB FEATURE - Only for Rainfall)
        # ---------------------------
        if data_type == "Rainfall":
            stats = get_summary_stats(df, view_mode, plot_df, agg_option)
            
            if stats:
                st.markdown("### 📊 Summary Statistics")
                cols = st.columns(len(stats))
                for i, (key, value) in enumerate(stats.items()):
                    with cols[i]:
                        st.metric(key, value)

        # ---------------------------
        # DOWNLOAD OPTIONS
        # ---------------------------
        st.markdown("### 📥 Download Plot")
        
        html_filename = f"{sensor_id}_{view_mode}_{data_type}_{time_title.replace(' ', '_').replace(',', '').replace(':', '_').replace('(', '').replace(')', '')}.html"
        
        try:
            html_string = fig.to_html(include_plotlyjs='cdn')
            st.download_button(
                f"📄 Download {data_type} Plot as HTML",
                html_string.encode(), 
                file_name=html_filename, 
                mime="text/html",
                help="Download interactive HTML plot file."
            )
        except Exception as e:
            st.error(f"Download failed: {str(e)}")

        st.info("💡 **Note**: Download individual plots as interactive HTML files.")

st.markdown("---")
st.caption("Built with ❤️ using Streamlit • GitHub Version - Fast & Reliable")
