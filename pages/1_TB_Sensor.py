# TB Sensor - Converted from Google Drive backup to GitHub storage
# Retains all original sophisticated features: dual y-axis, bar charts, advanced statistics
# Missing data handling: continuous time indices, gap visualization, smart aggregation
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from datetime import datetime, timedelta
import base64
import calendar

# ---------------------------
# CONFIGURATION
# ---------------------------
st.set_page_config(page_title="🌧️ TB Sensor", page_icon="🌧️", layout="wide")

# GitHub storage paths
TB_BASE_PATH = "processed/tb"
SENSOR_METADATA_PATH = "processed/sensor_metadata/sensor_metadata.csv"
LOGO_PATH = "assets/logo_1.png"

# ---------------------------
# UTILITY FUNCTIONS
# ---------------------------
@st.cache_data
def load_csv(file_path):
    """Load CSV with proper data type handling"""
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
    """Encode image to base64 for display"""
    try:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        return ""

def get_summary_stats(df, view_mode, plot_df, agg_type=None):
    """
    Calculate comprehensive summary statistics for the given data.
    Returns None if there's missing data in the plot data, otherwise returns stats dict.
    ORIGINAL SOPHISTICATED APPROACH - Only calculate stats when data is complete.
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
            rainfall_series = plot_df['rainfall_mm'].fillna(0)
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
                stats["Wettest month"] = f"{wettest.strftime('%B')} ({round(plot_df['rainfall_mm'].max(), 2)} mm)"
            else:
                stats["Wettest month"] = "N/A"
                
            stats["Dry months"] = (plot_df['rainfall_mm'] == 0).sum() + plot_df['rainfall_mm'].isna().sum()
            stats["Wet months"] = (plot_df['rainfall_mm'] > 0).sum()
            
            # Longest dry spell in days (convert from monthly data)
            # For yearly view, we need to estimate days from months
            rainfall_series = plot_df['rainfall_mm'].fillna(0)
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
# FILE SELECTION (GitHub storage)
# ---------------------------
try:
    sites = [d for d in os.listdir(TB_BASE_PATH) if os.path.isdir(os.path.join(TB_BASE_PATH, d)) and not d.startswith('.')]
    
    if not sites:
        st.error("No TB sensor folders found. Please check the folder structure.")
        st.stop()
    
    selected_site = st.sidebar.selectbox("🌍 Select TB Site", sites)
    
    # Get CSV files in selected site
    site_path = os.path.join(TB_BASE_PATH, selected_site)
    csv_files = [f for f in os.listdir(site_path) if f.endswith('.csv') and not f.startswith('.')]
    
    if not csv_files:
        st.error(f"No CSV files found in {selected_site}")
        st.stop()
    
    selected_file = st.sidebar.selectbox("📂 Select data file", csv_files)
    
except Exception as e:
    st.error(f"Error accessing TB sensor files: {e}")
    st.stop()

# ---------------------------
# MAIN CONTENT
# ---------------------------
if selected_file:
    # Load data from GitHub storage
    file_path = os.path.join(site_path, selected_file)
    df = load_csv(file_path)
    
    sensor_id = selected_file.replace(".csv", "")

    # ORIGINAL DESIGN: Parameters section (to match OBS and HOBO pattern)
    st.sidebar.markdown("### 📌 Parameters")
    data_type = st.sidebar.radio("Select data type:", ["Rainfall", "Temperature"])
    
    # ORIGINAL DESIGN: Time Range section
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

    if view_mode == "Custom":
        start = st.sidebar.date_input("Start Date", min_value=min_date.date(), value=min_date.date())
        end = st.sidebar.date_input("End Date", min_value=min_date.date(), value=max_date.date())
        mask = (df.index.date >= start) & (df.index.date <= end)
        filtered_df = df[mask]
        
        # ORIGINAL FEATURE: Determine aggregation based on date range
        date_diff = (end - start).days
        if date_diff <= 7:
            # Create continuous hourly index and reindex with NaN for missing periods
            full_range = pd.date_range(start=pd.Timestamp(start), end=pd.Timestamp(end) + pd.Timedelta(days=1), freq='H', inclusive='left')
            # Only sum if we have actual non-NaN values
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
            # ORIGINAL FEATURE: Calendar view for daily selection
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
            # ORIGINAL FEATURE: Show all months that have timestamps (including those with missing rainfall data)
            monthly_groups = df.groupby(pd.Grouper(freq='MS')).size()
            bins = monthly_groups[monthly_groups > 0].index
            # Format bins for better display
            bin_options = [f"{bin.strftime('%Y %B')}" for bin in bins]
            selected_bin_str = st.sidebar.selectbox("📆 Select month:", bin_options)
            # Convert back to timestamp
            selected_bin = bins[bin_options.index(selected_bin_str)]
            delta = pd.DateOffset(months=1)
            
        else:  # Yearly - ORIGINAL UNIQUE TB FEATURE
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
            # ORIGINAL FEATURE: Create continuous hourly index for the selected day with aggregation choice
            agg = st.sidebar.radio("Aggregation:", ["15-min", "Hourly"])
            freq = "15min" if agg == "15-min" else "H"
            
            full_range = pd.date_range(start=selected_bin, end=selected_bin + pd.Timedelta(days=1), freq=freq, inclusive='left')
            # Aggregate and reindex to show missing periods as NaN
            hourly_data = filtered_df.resample(freq).agg({
                data_column: agg_func
            })
            plot_df = hourly_data.reindex(full_range)
            
            # Create title
            interval_text = "15 min interval" if agg == "15-min" else "one hour interval"
            unit = "(mm)" if data_type == "Rainfall" else "(°C)"
            time_title = f"{data_type} {unit} (Daily: {selected_bin.strftime('%B %d, %Y')} - {interval_text})"
        elif view_mode == "Monthly":
            # ORIGINAL FEATURE: Create continuous daily index for the selected month
            month_end = selected_bin + pd.offsets.MonthEnd(1)
            full_range = pd.date_range(start=selected_bin, end=month_end, freq='D')
            # Aggregate and reindex to show missing periods as NaN
            daily_data = filtered_df.resample('D').agg({
                data_column: agg_func
            })
            plot_df = daily_data.reindex(full_range)
            unit = "(mm)" if data_type == "Rainfall" else "(°C)"
            time_title = f"{data_type} {unit} (Monthly: {selected_bin.strftime('%B %Y')})"
        else:  # Yearly
            # ORIGINAL FEATURE: Create continuous monthly index for the selected year
            year_end = selected_bin.replace(month=12, day=31)
            full_range = pd.date_range(start=selected_bin, end=year_end, freq='MS')
            # Aggregate and reindex to show missing periods as NaN
            monthly_data = filtered_df.resample('MS').agg({
                data_column: agg_func
            })
            plot_df = monthly_data.reindex(full_range)
            unit = "(mm)" if data_type == "Rainfall" else "(°C)"
            time_title = f"{data_type} {unit} (Yearly: {selected_bin.strftime('%Y')})"

    # ---------------------------
    # PLOTS (ORIGINAL SOPHISTICATED VISUALIZATION)
    # ---------------------------
    st.markdown(f"<h4 style='font-weight: 600;'>📈 Sensor: {sensor_id}</h4>", unsafe_allow_html=True)

    if plot_df.empty:
        st.warning("No data available for the selected time period.")
    else:
        # ORIGINAL FEATURE: Check for missing data and show warning if found
        has_missing_data = plot_df.isna().any().any()
        if has_missing_data:
            if data_type == "Rainfall":
                st.warning("⚠️ Some data points are missing for this period. Gaps will be visible in the plot.")
            else:
                st.warning("⚠️ Some data points are missing for this period. Gaps will be visible in the plot.")

        # ORIGINAL FEATURE: For rainfall, create cumulative; for temperature, don't
        if data_type == "Rainfall":
            # Calculate cumulative rainfall for dual y-axis
            plot_df['cumulative_rainfall'] = plot_df[data_column].cumsum()
            show_cumulative = True
        else:
            show_cumulative = False
        
        # ORIGINAL FEATURE: Create the appropriate plot type
        if data_type == "Rainfall":
            # ORIGINAL DESIGN: Bar chart for rainfall - gaps will show as missing bars
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            
            # Bar chart for rainfall
            fig.add_trace(
                go.Bar(x=plot_df.index, y=plot_df[data_column], name="Rainfall", marker_color="blue"),
                secondary_y=False,
            )
            
            # Cumulative line on secondary y-axis
            if show_cumulative:
                fig.add_trace(
                    go.Scatter(x=plot_df.index, y=plot_df['cumulative_rainfall'], 
                              mode='lines', name='Cumulative', line=dict(color='red')),
                    secondary_y=True,
                )
        else:
            # ORIGINAL DESIGN: Line chart for temperature
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=plot_df.index, y=plot_df[data_column], 
                                   mode='lines+markers', name='Temperature', 
                                   line=dict(color='orange')))
        
        # Calculate y-axis max (higher than highest value)
        max_data = plot_df[data_column].max()
        
        if pd.isna(max_data):
            y_max = 10
            st.warning("⚠️ No valid data found for the selected period.")
            
        # ORIGINAL FEATURE: For temperature, calculate proper y-axis range
        if data_type == "Temperature":
            min_temp = plot_df[data_column].min()
            max_temp = plot_df[data_column].max()
            if not (pd.isna(min_temp) or pd.isna(max_temp)):
                temp_range = max_temp - min_temp
                y_min = min_temp - (temp_range * 0.1)
                y_max = max_temp + (temp_range * 0.1)
            else:
                y_min, y_max = 0, 40
        else:
            y_max = max_data * 1.2 if not pd.isna(max_data) else 10
        
        # ORIGINAL FEATURE: Update layout - dual y-axis for rainfall, single for temperature
        if show_cumulative:
            fig.update_layout(
                title=time_title,
                xaxis_title="Time",
                height=500,
                template="plotly_white"
            )
            fig.update_yaxes(title_text="Rainfall (mm)", secondary_y=False, range=[0, y_max])
            fig.update_yaxes(title_text="Cumulative Rainfall (mm)", secondary_y=True)
        else:
            fig.update_layout(
                title=time_title,
                xaxis_title="Time",
                yaxis_title=f"{data_type} ({'mm' if data_type == 'Rainfall' else '°C'})",
                height=500,
                template="plotly_white"
            )
            if data_type == "Temperature":
                fig.update_yaxes(range=[y_min, y_max])
        
        # ORIGINAL FEATURE: Special x-axis formatting for different view modes
        if view_mode == "Monthly":
            fig.update_xaxes(tickformat="%d", title_text="Day of Month")
        elif view_mode == "Yearly":
            fig.update_xaxes(tickformat="%b", title_text="Month")

        st.plotly_chart(fig, use_container_width=True)

        # ---------------------------
        # ORIGINAL FEATURE: SUMMARY STATS (Only for Rainfall)
        # ---------------------------
        if data_type == "Rainfall":
            # ORIGINAL SOPHISTICATED STATISTICS
            agg_type = agg if view_mode == "Daily" else None
            stats = get_summary_stats(df, view_mode, plot_df, agg_type)
            
            if stats:
                st.markdown("### 📊 Summary Statistics")
                cols = st.columns(len(stats))
                for i, (key, value) in enumerate(stats.items()):
                    with cols[i % len(cols)]:
                        st.metric(key, value)
            else:
                st.info("📊 **Statistics unavailable** - Some data points are missing in the selected period.")

        # ---------------------------
        # ORIGINAL FEATURE: DOWNLOAD OPTIONS
        # ---------------------------
        st.markdown("### 📥 Download Plot")
        
        # HTML Download only
        html_filename = f"{sensor_id}_{view_mode}_{time_title.replace(' ', '_').replace(',', '').replace(':', '_').replace('(', '').replace(')', '')}.html"
        
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
st.caption("Built with ❤️ using Streamlit • GitHub Version - Retains all original Google Drive features")
