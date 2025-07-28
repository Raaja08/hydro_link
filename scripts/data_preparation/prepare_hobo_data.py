import pandas as pd



################merging data from same year same site ##########################

# --- File paths ---
file_a = "/Volumes/AMBITION/S4W/hydro_link/raw_data/hobo/hobo_site1/hobo_s1_2023_raw_a.csv"
file_b = "/Volumes/AMBITION/S4W/hydro_link/raw_data/hobo/hobo_site1/hobo_s1_2023_raw_b.csv"
output_file = "/Volumes/AMBITION/S4W/hydro_link/processed/hobo/hobo_site1/hobo_s1_2023.csv"

# --- Read CSVs (skip metadata row, header is in second row) ---
df_a = pd.read_csv(file_a, header=1)
df_b = pd.read_csv(file_b, header=1)

# --- Merge and clean ---
df = pd.concat([df_a, df_b], ignore_index=True).drop_duplicates()
df.columns = df.columns.str.strip()  # Remove trailing spaces

# --- Identify relevant columns ---
timestamp_col = [col for col in df.columns if 'date time' in col.lower()][0]
pressure_col = [col for col in df.columns if 'psi' in col.lower()][0]
temp_f_col = [col for col in df.columns if 'temp' in col.lower() and 'f' in col.lower()][0]

# --- Drop rows where both pressure and temp are missing ---
df = df[~(df[pressure_col].isna() & df[temp_f_col].isna())]

# --- Parse datetime ---
df[timestamp_col] = pd.to_datetime(df[timestamp_col], errors='coerce')
df = df.dropna(subset=[timestamp_col])  # Drop invalid timestamps

# --- Convert text columns to numeric ---
df[pressure_col] = pd.to_numeric(df[pressure_col], errors='coerce')
df[temp_f_col] = pd.to_numeric(df[temp_f_col], errors='coerce')  # Ensure temp is numeric

# --- Convert °F to °C ---
df['water_temp_c'] = (df[temp_f_col] - 32) * 5.0 / 9.0

# --- Final DataFrame ---
df_clean = df[[timestamp_col, pressure_col, 'water_temp_c']].copy()
df_clean.columns = ['timestamp', 'pressure_psi', 'water_temp_c']
df_clean = df_clean.sort_values('timestamp').reset_index(drop=True)

# --- Save output ---
df_clean.to_csv(output_file, index=False)
print(f"✅ Saved merged and converted file to {output_file}")
print(f"🧾 Final columns: {list(df_clean.columns)}")




################ reformattting data ##########################
import pandas as pd

# --- File paths ---
input_file = "/Volumes/AMBITION/S4W/hydro_link/raw_data/hobo/hobo_site2/hobo_s2_2023_raw.csv"
output_file = "/Volumes/AMBITION/S4W/hydro_link/processed/hobo/hobo_site2/hobo_s2_2023.csv"

# --- Read CSV (skip metadata, use second row as header) ---
df = pd.read_csv(input_file, header=1)
df.columns = df.columns.str.strip()  # Clean column names

# --- Detect relevant columns ---
timestamp_col = [col for col in df.columns if 'date time' in col.lower()][0]
pressure_col = [col for col in df.columns if 'psi' in col.lower()][0]
temp_f_col = [col for col in df.columns if 'temp' in col.lower() and 'f' in col.lower()][0]

# --- Clean rows ---
df = df[~(df[pressure_col].isna() & df[temp_f_col].isna())]  # Remove empty rows
df[timestamp_col] = pd.to_datetime(df[timestamp_col], errors='coerce')
df = df.dropna(subset=[timestamp_col])

df[pressure_col] = pd.to_numeric(df[pressure_col], errors='coerce')
df[temp_f_col] = pd.to_numeric(df[temp_f_col], errors='coerce')
df['water_temp_c'] = (df[temp_f_col] - 32) * 5.0 / 9.0

# --- Final dataframe ---
df_clean = df[[timestamp_col, pressure_col, 'water_temp_c']].copy()
df_clean.columns = ['timestamp', 'pressure_psi', 'water_temp_c']
df_clean = df_clean.sort_values('timestamp').reset_index(drop=True)

# --- Save output ---
df_clean.to_csv(output_file, index=False)
print(f"✅ Saved formatted file to {output_file}")
print(f"🧾 Columns: {list(df_clean.columns)}")