# HOBO Sensor
import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime, timedelta
import plotly.io as pio
from PIL import Image
import base64

# --- Configuration ---
HOBO_PATH = "/Volumes/AMBITION/S4W/hydro_link/processed/hobo"
SENSOR_METADATA_PATH = "/Volumes/AMBITION/S4W/hydro_link/processed/sensor_metadata/sensor_metadata.csv"
LOGO_PATH = "/Volumes/AMBITION/S4W/hydro_link/assets/logo_1.png"

# --- Page setup ---
st.set_page_config(page_title="HOBO Sensor Viewer", layout="wide")

# Encode and display logo
@st.cache_data
def encode_img_to_base64(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

logo_base64 = encode_img_to_base64(LOGO_PATH)
st.markdown(f"""
    <div style='display: flex; justify-content: space-between; align-items: center; padding: 20px 10px 10px 10px;'>
        <div>
            <h1 style='margin-bottom: 0;'>📊 S4W Sensor Dashboard</h1>
            <p style='margin-top: 5px; color: gray;font-size: 18px; font-weight: 500;'>From small sensors to big insights — monitor what matters ❤️</p>
        </div>
        <div>
            <img src='data:image/png;base64,{logo_base64}' style='height:100px;'/>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- Utility Functions ---
@st.cache_data
def load_csv(file_path):
    df = pd.read_csv(file_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df.dropna(subset=['timestamp'], inplace=True)
    df.set_index('timestamp', inplace=True)
    df.sort_index(inplace=True)
    return df

@st.cache_data
def load_metadata():
    return pd.read_csv(SENSOR_METADATA_PATH)

# --- Load available files ---
sites = [d for d in os.listdir(HOBO_PATH) if os.path.isdir(os.path.join(HOBO_PATH, d)) and not d.startswith('.')]
selected_site = st.sidebar.selectbox("🌍 Select HOBO Site", sites)

site_path = os.path.join(HOBO_PATH, selected_site)
csv_files = [f for f in os.listdir(site_path) if f.endswith('.csv') and not f.startswith('.')]
selected_file = st.sidebar.selectbox("📂 Select data file", csv_files)

if selected_file:
    df = load_csv(os.path.join(site_path, selected_file))
    metadata_df = load_metadata()

    sensor_id = selected_file.split(".")[0]
    metadata_df['sensor_id'] = metadata_df['sensor_id'].astype(str)
    sensor_row = metadata_df[metadata_df['sensor_id'].str.contains(sensor_id)]
    sensor_height = sensor_row['sensor_height_m'].values[0] if not sensor_row.empty else 0.0

    param_display = {
        'pressure_psi': 'Pressure (psi)',
        'water_level_m': 'Water Level (m)',
        'water_temp_c': 'Water Temperature (°C)'
    }

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
    
    st.markdown(f"<h4 style='font-weight: 600;'>📈 Sensor: {selected_file.replace('.csv', '')}</h4>", unsafe_allow_html=True)
    #st.markdown(f"📉 Sensor: <span style='color:#0366d6; font-weight:bold'>{selected_file.replace('.csv', '')}</span>", unsafe_allow_html=True)

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

            if st.button(f"⬇️ Download {param_display[param]} Plot as PNG", key=param):
                filename = f"{sensor_id}_{view_mode}_{param}.png"
                pio.write_image(fig, filename, format="png")
                with open(filename, "rb") as file:
                    st.download_button(
                        label="Download", data=file, file_name=filename, mime="image/png"
                    )

# ---- ✅ Batch download of plots by time period ----
import zipfile
import zipfile
import tempfile

def get_time_bins(view_mode):
    if view_mode == "Daily":
        bins = df.resample('D').mean().index
        delta = timedelta(days=1)
        fmt = "%Y-%m-%d"
        label_prefix = "Day"
    elif view_mode == "Weekly":
        bins = df.resample('W-MON').mean().index
        delta = timedelta(weeks=1)
        fmt = "Week of %B %d, %Y"
        label_prefix = "Week"
    elif view_mode == "Monthly":
        bins = df.resample('MS').mean().index
        delta = pd.DateOffset(months=1)
        fmt = "%B %Y"
        label_prefix = "Month"
    else:
        return [], None, None, None
    return bins, delta, fmt, label_prefix

if view_mode in ["Daily", "Weekly", "Monthly"] and st.sidebar.button(f"⬇️ Download All {view_mode} Plots"):
    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = os.path.join(tmpdir, f"{sensor_id}_{view_mode.lower()}_plots.zip")

        with zipfile.ZipFile(zip_path, 'w') as zipf:
            bins, delta, fmt, label_prefix = get_time_bins(view_mode)

            for param in selected_params:
                for start_time in bins:
                    end_time = start_time + delta
                    sub_df = df[(df.index >= start_time) & (df.index < end_time)]

                    if sub_df.empty:
                        continue

                    title = f"{param_display[param]} ({start_time.strftime(fmt)})"
                    file_name = f"{sensor_id}_{param}_{start_time.strftime('%Y-%m-%d')}.png"

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
                file_name=f"{sensor_id}_{view_mode.lower()}_plots.zip",
                mime="application/zip"
            )
    st.markdown("---")
    st.caption("Built with ❤️ using Streamlit and Plotly")