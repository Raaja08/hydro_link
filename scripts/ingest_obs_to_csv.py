#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 18 14:23:04 2025

@author: livaraja08

ingest_obs_to_csv.py

Description:
    This script loads raw OBS sensor .TXT files from:
        /Volumes/AMBITION/S4W/hydro_link/raw_data/obs/{sensor_id}/
    It parses, cleans, and combines them into a single CSV per sensor:
        /Volumes/AMBITION/S4W/hydro_link/processed/obs/obs{sensor_id}_clean.csv

Usage:
    Run in Spyder or Terminal:
        python3 ingest_obs_to_csv.py
"""

import pandas as pd
from pathlib import Path
from io import StringIO

# Use full paths
RAW_BASE = Path("/Volumes/AMBITION/S4W/hydro_link/raw_data/obs")
PROCESSED_BASE = Path("/Volumes/AMBITION/S4W/hydro_link/processed/obs")

# Ensure output folder exists
PROCESSED_BASE.mkdir(parents=True, exist_ok=True)

def load_obs_file(file_path, sensor_id):
    with open(file_path, 'r') as f:
        lines = f.readlines()

    # Skip lines until header is found
    header_line_index = next(i for i, line in enumerate(lines) if line.startswith("time"))
    header = lines[header_line_index].strip().split(',')
    data_lines = lines[header_line_index + 1:]

    # Create DataFrame
    df = pd.read_csv(StringIO(''.join(data_lines)), names=header)

    # Convert 'time' to datetime
    df['timestamp'] = pd.to_datetime(df['time'], unit='s')
    df.drop(columns=['time'], inplace=True)

    # Add sensor ID
    df['sensor'] = sensor_id

    # Reorder columns
    cols = ['timestamp'] + [col for col in df.columns if col not in ['timestamp', 'sensor']] + ['sensor']
    return df[cols]

def process_sensor_folder(sensor_id):
    folder = RAW_BASE / sensor_id
    all_txts = sorted(f for f in folder.glob("*.TXT") if not f.name.startswith("._"))
    all_dfs = []

    for file in all_txts:
        try:
            df = load_obs_file(file, sensor_id)
            all_dfs.append(df)
        except Exception as e:
            print(f"Failed to load {file.name}: {e}")

    if all_dfs:
        combined = pd.concat(all_dfs, ignore_index=True)
        output_path = PROCESSED_BASE / f"obs{sensor_id}_clean.csv"
        combined.to_csv(output_path, index=False)
        print(f"✅ Saved: {output_path}")
    else:
        print(f"⚠️ No valid data for sensor {sensor_id}")

if __name__ == "__main__":
    for folder in RAW_BASE.iterdir():
        if folder.is_dir():
            sensor_id = folder.name
            process_sensor_folder(sensor_id)