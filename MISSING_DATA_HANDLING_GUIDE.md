# Missing Data Handling Guide for Time Series Dashboards

## Overview
This document explains the comprehensive approach used in the TB Sensor (Rainfall) dashboard to handle missing data in time series visualizations. This methodology can be applied to any sensor data dashboard with similar requirements.

## Problem Statement
When dealing with sensor data, missing values can occur due to:
- Sensor malfunctions
- Data transmission failures
- Maintenance periods
- Power outages
- Environmental conditions

The challenge is to distinguish between:
- **Real zero values** (measured value = 0)
- **Missing data** (no measurement taken = should show as gaps)

## Solution Architecture

### 1. Data Loading & Preprocessing
```python
@st.cache_data
def load_csv(file_path):
    df = pd.read_csv(file_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df.dropna(subset=['timestamp'], inplace=True)
    df.set_index('timestamp', inplace=True)
    df.sort_index(inplace=True)
    
    # Convert empty strings in rainfall_mm to NaN
    df['rainfall_mm'] = pd.to_numeric(df['rainfall_mm'], errors='coerce')
    
    return df
```

**Key Points:**
- Convert empty strings to `NaN` using `pd.to_numeric(errors='coerce')`
- Preserve `NaN` values (don't fill with zeros)
- Maintain original data integrity

### 2. Time Bin Selection Strategy
```python
# Show ALL time periods with timestamps (including those with missing data)
if view_mode == "Monthly":
    monthly_groups = df.groupby(pd.Grouper(freq='MS')).size()
    bins = monthly_groups[monthly_groups > 0].index
```

**Philosophy:**
- Include ALL time periods in dropdown menus
- Let users see and explore periods with missing data
- Provide visual feedback through gaps and warnings

### 3. Smart Aggregation Logic
```python
# Core aggregation function
lambda x: x.sum() if (len(x) > 0 and x.notna().any()) else None
```

**Logic Breakdown:**
- `len(x) > 0`: Ensures there are values in the time period
- `x.notna().any()`: Ensures at least one value is not NaN
- `x.sum()`: Sum only when valid data exists
- `None`: Return for periods with no valid data (creates gaps)

### 4. Continuous Time Series Creation
```python
# Create continuous time index
full_range = pd.date_range(start=selected_bin, end=month_end, freq='D')

# Resample with gap-preserving logic
daily_data = filtered_df.resample('D').agg({
    'rainfall_mm': lambda x: x.sum() if (len(x) > 0 and x.notna().any()) else None
})

# Reindex to show gaps
plot_df = daily_data.reindex(full_range)
```

**Result:**
- Missing periods become `NaN` in the final DataFrame
- Plotly automatically shows gaps for `NaN` values
- Continuous time axis maintained

### 5. Cumulative Data Handling
```python
# Calculate cumulative while preserving gaps
plot_df['cumulative_rainfall'] = plot_df['rainfall_mm'].cumsum()
```

**Behavior:**
- `cumsum()` naturally handles `NaN` values
- Cumulative line shows breaks during missing periods
- `connectgaps=False` in plot ensures visible gaps

### 6. Summary Statistics Logic
```python
def get_summary_stats(df, view_mode, plot_df):
    # Check if there are any missing values in the plot data
    if plot_df['rainfall_mm'].isna().any():
        return None  # Trigger warning message
    
    # Calculate stats only when data is complete
    stats = {...}
    return stats
```

**User Experience:**
- Missing data = No statistics + Warning message
- Complete data = Full statistics display
- Clear distinction between incomplete and complete periods

## Implementation Patterns

### Pattern 1: View Mode Handling
```python
if view_mode == "Daily":
    freq = 'H'  # Hourly aggregation for daily view
elif view_mode == "Monthly":  
    freq = 'D'  # Daily aggregation for monthly view
elif view_mode == "Yearly":
    freq = 'MS' # Monthly aggregation for yearly view
```

### Pattern 2: Custom Date Range Logic
```python
date_diff = (end - start).days
if date_diff <= 7:
    freq = 'H'  # Hourly
elif date_diff <= 90:
    freq = 'D'  # Daily  
else:
    freq = 'MS' # Monthly
```

### Pattern 3: Gap Visualization
```python
# Bar chart automatically shows gaps for NaN
fig = px.bar(plot_df, y="rainfall_mm")

# Line chart with explicit gap handling
fig.add_scatter(
    connectgaps=False  # Show breaks in line
)
```

## Warning System Implementation

### Warning Conditions
- ANY `NaN` values in the display period
- Applies to ALL view modes
- Consistent across all aggregation levels

### Warning Message
```python
if stats is None:
    st.warning("⚠️ Data is incomplete for this period. Summary statistics are not available.")
else:
    # Show normal statistics
```

## Testing Scenarios Covered

### 1. Complete Missing Periods
- **Example**: July 2022 (entirely missing)
- **Behavior**: Empty plot + Warning message
- **User sees**: Clear gap indication

### 2. Partial Missing Periods  
- **Example**: May 11, 2022 (data until 12:30, then missing)
- **Behavior**: Bars until 12:30, then gaps + Warning
- **User sees**: Transition from data to missing

### 3. Mixed Data/Missing
- **Example**: August 2022 (missing until Aug 11, then data)
- **Behavior**: Gaps + Data + Warning
- **User sees**: Recovery point clearly visible

### 4. Zero vs Missing Distinction
- **Zero rainfall**: Bar at y=0 (blue bar visible)
- **Missing data**: No bar (gap in timeline)
- **Clear visual difference**

## Reusability Guidelines

### For Other Sensor Types
1. Replace `'rainfall_mm'` with your sensor column name
2. Adjust aggregation functions (sum vs mean vs max)
3. Modify summary statistics calculations
4. Keep the core missing data logic unchanged

### For Different Time Scales
1. Adjust frequency parameters (`'H'`, `'D'`, `'MS'`, etc.)
2. Modify time range logic in custom view
3. Update bin selection frequencies
4. Maintain aggregation pattern

### For Multiple Sensors
1. Apply same preprocessing to all sensor columns
2. Use multi-column aggregation functions
3. Check for missing data across all sensors
4. Show warnings when any sensor has gaps

## Key Benefits

1. **Data Integrity**: Never masks missing data as zeros
2. **User Awareness**: Clear visual and textual indicators
3. **Flexibility**: Works across all time scales
4. **Consistency**: Same logic for all view modes
5. **Transparency**: Users can explore all time periods

## Common Pitfalls to Avoid

1. **Don't use `.fillna(0)`** - This masks missing data
2. **Don't use `.resample().sum()`** alone - This creates false zeros
3. **Don't hide missing periods** from dropdowns
4. **Don't show statistics** when data is incomplete
5. **Don't use `connectgaps=True`** for lines - This hides gaps

## Future Enhancements

### Potential Additions
1. **Gap Duration Reporting**: Show length of missing periods
2. **Data Quality Metrics**: Percentage of missing data
3. **Interpolation Options**: Allow users to fill gaps (optional)
4. **Missing Data Summary**: Overview of all gaps in dataset
5. **Export Gap Report**: Download missing data periods

### Advanced Features
1. **Sensor Status Indicators**: Color-code based on data availability
2. **Predictive Gap Filling**: ML-based interpolation options
3. **Multi-Sensor Correlation**: Show how gaps affect related sensors
4. **Real-time Gap Alerts**: Notify when new gaps appear

---

**Created**: July 27, 2025  
**Last Updated**: July 27, 2025  
**Version**: 1.0  
**Author**: GitHub Copilot  
**Tested with**: TB Sensor Rainfall Dashboard (3_TB_Sensor.py)
