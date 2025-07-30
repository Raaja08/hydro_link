import streamlit as st
import sys
import traceback

st.title("🔍 Debug App - Testing Hydro Link Issues")

try:
    st.write("✅ Streamlit imported successfully")
    
    # Test basic imports
    import pandas as pd
    st.write("✅ Pandas imported successfully")
    
    import plotly.express as px
    st.write("✅ Plotly imported successfully")
    
    import plotly.io as pio
    st.write("✅ Plotly.io imported successfully")
    
    # Test datetime parsing
    import pandas as pd
    from datetime import datetime
    
    test_data = pd.DataFrame({
        'timestamp': ['2023-04-21 00:04:22', '2023-04-21 00:09:22'],
        'value': [1, 2]
    })
    
    test_data['timestamp'] = pd.to_datetime(test_data['timestamp'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
    st.write("✅ Datetime parsing works")
    st.dataframe(test_data)
    
    # Test Google Drive utilities
    try:
        from google_drive_utils import get_drive_manager
        st.write("✅ Google Drive utilities imported successfully")
        
        drive_manager = get_drive_manager()
        st.write("✅ Drive manager created successfully")
        
        if drive_manager.authenticate():
            st.write("✅ Google Drive authentication successful")
        else:
            st.write("⚠️ Google Drive authentication failed (expected in some environments)")
            
    except Exception as gd_error:
        st.write(f"⚠️ Google Drive issue: {gd_error}")
        st.write("This might be the source of the problem")
        
    # Test kaleido (for plot exports)
    try:
        import kaleido
        st.write("✅ Kaleido imported successfully")
    except Exception as kal_error:
        st.write(f"❌ Kaleido import failed: {kal_error}")
        st.write("This could cause plot download issues")
    
    st.write("🎉 All tests completed!")
    
except Exception as e:
    st.error(f"❌ Error occurred: {e}")
    st.code(traceback.format_exc())
    st.write("**Python version:** ", sys.version)
    st.write("**Python path:** ", sys.path)
