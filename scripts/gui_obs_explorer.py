#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 18 14:57:39 2025

@author: livaraja08
"""

# ------------------------------------------------------------------------------
# Streamlit GUI for OBS Sensor Weekly Data Exploration
#
# Description:
# This script provides an interactive web-based dashboard to explore
# processed OBS sensor data on a weekly basis. It allows users to:
#   - Select a sensor ID from the available processed CSVs
#   - Filter data by date range
#   - Select and visualize a specific week of data
#   - Plot variables like Backscatter, Pressure, Ambient Light, etc.
#   - Download weekly-filtered data as CSV
#
# Dependencies:
#   - streamlit
#   - pandas
#   - plotly
#
# To Run:
#   streamlit run /Volumes/AMBITION/S4W/hydro_link/scripts/gui_obs_explorer.py
# ------------------------------------------------------------------------------

import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from pathlib import Path

# --- Configuration ---
PROCESSED_DIR = Path("/Volumes/AMBITION/S4W/hydro_link/processed/obs")

st.set_page_config(page_title="OBS Sensor Explorer", layout="wide")
st.title("OBS Sensor Weekly Explorer")

# --- Sidebar ---
sensor_files = sorted(PROCESSED_DIR.glob("obs*_clean.csv"))
sensor_ids = [f.stem.split('_')[0][3:] for f in sensor_files]

sensor_id = st.sidebar.selectbox("Select Sensor ID", sensor_ids)
df_path = PROCESSED_DIR / f"obs{sensor_id}_clean.csv"

# --- Load Data ---
df = pd.read_csv(df_path, parse_dates=['timestamp'])
df = df.sort_values('timestamp')

start_date = st.sidebar.date_input("Start Date", df['timestamp'].min().date())
end_date = st.sidebar.date_input("End Date", df['timestamp'].max().date())

# --- Filter Data ---
df = df[(df['timestamp'] >= pd.to_datetime(start_date)) & (df['timestamp'] <= pd.to_datetime(end_date))]

# --- Group by Week ---
df['week'] = df['timestamp'].dt.to_period('W').apply(lambda r: r.start_time)
weeks = sorted(df['week'].unique())

selected_week = st.selectbox("Select Week", weeks)
df_week = df[df['week'] == selected_week]

# --- Plotting ---
def plot_timeseries(df, y, title):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df[y], mode='lines', name=y))
    fig.update_layout(title=title, xaxis_title='Time', yaxis_title=y)
    return fig

cols_to_plot = [col for col in df.columns if col not in ['timestamp', 'sensor', 'week']]

for col in cols_to_plot:
    st.plotly_chart(plot_timeseries(df_week, col, f"{col} - Week of {selected_week.date()}"), use_container_width=True)

# --- Export ---
st.download_button("Download This Week's Data", data=df_week.to_csv(index=False), file_name=f"obs{sensor_id}_week_{selected_week.date()}.csv")