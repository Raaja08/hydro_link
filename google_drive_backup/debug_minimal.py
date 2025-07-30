import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Debug Test", layout="wide")

st.title("🔧 Debug Test - Minimal App")

# Test 1: Basic Streamlit functionality
st.header("✅ Test 1: Basic Streamlit")
st.write("If you see this, Streamlit is working!")

# Test 2: Pandas functionality
st.header("✅ Test 2: Pandas")
try:
    df = pd.DataFrame({'test': [1, 2, 3], 'timestamp': ['2023-01-01 00:00:00', '2023-01-02 00:00:00', '2023-01-03 00:00:00']})
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    st.write("Pandas DataFrame created successfully:")
    st.dataframe(df)
    st.success("✅ Pandas datetime parsing working!")
except Exception as e:
    st.error(f"❌ Pandas error: {e}")

# Test 3: Google Drive import
st.header("✅ Test 3: Google Drive Utils")
try:
    from google_drive_utils import get_drive_manager
    st.success("✅ Google Drive utils imported successfully!")
    
    drive_manager = get_drive_manager()
    st.write(f"Drive manager created: {drive_manager}")
    
except ImportError as e:
    st.warning(f"⚠️ Google Drive import failed: {e}")
except Exception as e:
    st.error(f"❌ Google Drive error: {e}")

# Test 4: Requirements
st.header("✅ Test 4: Key Libraries")
libraries = ['streamlit', 'pandas', 'plotly', 'google-api-python-client']
for lib in libraries:
    try:
        __import__(lib.replace('-', '_').replace('google_api_python_client', 'googleapiclient'))
        st.success(f"✅ {lib} imported successfully")
    except ImportError:
        st.error(f"❌ {lib} not available")

st.write("---")
st.write(f"🕐 Current time: {datetime.now()}")
st.write("🎯 If all tests pass, the main app should work!")
