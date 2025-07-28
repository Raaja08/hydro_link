# S4W Sensor Dashboard - Home Page
import streamlit as st

# Set page configuration
st.set_page_config(page_title="S4W Sensor Dashboard", layout="wide")

# Import and run the OBS Sensor content
try:
    # Import the main OBS sensor functionality
    import sys
    import os
    
    # Add current directory to path to ensure imports work
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.append(current_dir)
    
    # Now import and execute the OBS sensor code
    exec(open('OBS_Sensor.py').read())
    
except Exception as e:
    st.error(f"❌ Error loading OBS Sensor dashboard: {e}")
    st.info("Please check that OBS_Sensor.py exists and is properly configured.")
