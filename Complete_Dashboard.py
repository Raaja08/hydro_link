import streamlit as st

st.set_page_config(
    page_title="S4W Sensor Dashboard - Complete",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1f77b4, #00509E);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
    }
    .sensor-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #1f77b4;
    }
    .stSelectbox > div > div {
        background-color: #1f77b4;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown("""
<div class="main-header">
    <h1>🌊 S4W Sensor Dashboard Suite</h1>
    <p>Complete hydrological monitoring system - From small sensors to big insights</p>
</div>
""", unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.markdown("## 📊 Dashboard Selection")
st.sidebar.markdown("Choose which sensor dashboard to view:")

dashboard_options = {
    "🌧️ TB Sensor Dashboard": {
        "description": "Rainfall & Temperature Monitoring",
        "features": ["Rainfall visualization", "Temperature plotting", "Missing data gaps", "Summary statistics", "Dual y-axis charts"],
        "file": "pages/3_TB_Sensor_G.py"
    },
    "💧 HOBO Sensor Dashboard": {
        "description": "Water Level & Environmental Monitoring", 
        "features": ["Water level calculation", "Pressure monitoring", "Temperature tracking", "Multi-parameter analysis"],
        "file": "pages/2_HOBO_Sensor_G.py"
    },
    "🔬 OBS Sensor Dashboard": {
        "description": "Multi-Parameter Water Quality Monitoring",
        "features": ["Ambient light analysis", "Backscatter measurements", "Pressure compensation", "Water quality indicators"],
        "file": "OBS_Sensor_G.py"
    }
}

selected_dashboard = st.sidebar.selectbox(
    "Select Dashboard:",
    list(dashboard_options.keys()),
    index=0
)

# Display dashboard information
dashboard_info = dashboard_options[selected_dashboard]

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown(f"""
    <div class="sensor-card">
        <h3>{selected_dashboard}</h3>
        <p><strong>{dashboard_info['description']}</strong></p>
        <h4>Key Features:</h4>
        <ul>
    """, unsafe_allow_html=True)
    
    for feature in dashboard_info['features']:
        st.markdown(f"<li>{feature}</li>", unsafe_allow_html=True)
    
    st.markdown("</ul></div>", unsafe_allow_html=True)

with col2:
    st.markdown("""
    ### 🚀 Quick Start
    1. Select a dashboard from the sidebar
    2. Click "Launch Dashboard" below
    3. Toggle Google Drive data source
    4. Explore your sensor data!
    
    ### 📁 Data Sources
    - **Google Drive**: Cloud-based data access
    - **Local Files**: Fallback for local development
    """)

# Launch button
if st.button(f"🚀 Launch {selected_dashboard}", type="primary", use_container_width=True):
    st.markdown("---")
    st.markdown(f"## {selected_dashboard}")
    
    # Import and execute the selected dashboard
    try:
        if selected_dashboard == "🌧️ TB Sensor Dashboard":
            # Execute TB Sensor dashboard
            exec(open('pages/3_TB_Sensor_G.py').read())
        elif selected_dashboard == "💧 HOBO Sensor Dashboard":
            # Execute HOBO Sensor dashboard  
            exec(open('pages/2_HOBO_Sensor_G.py').read())
        elif selected_dashboard == "🔬 OBS Sensor Dashboard":
            # Execute OBS Sensor dashboard
            exec(open('OBS_Sensor_G.py').read())
    except FileNotFoundError as e:
        st.error(f"❌ Dashboard file not found: {e}")
        st.info("Please ensure all dashboard files are in the correct locations.")
    except Exception as e:
        st.error(f"❌ Error loading dashboard: {e}")
        st.info("Please check the dashboard file for any issues.")

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    ### 📈 Data Coverage
    - **TB Sensors**: 2018-2023
    - **HOBO Sensors**: 2023 data
    - **OBS Sensors**: 2023 data
    """)

with col2:
    st.markdown("""
    ### 🔧 Features
    - Interactive visualizations
    - Real-time data loading
    - Professional plot exports
    - Mobile-responsive design
    """)

with col3:
    st.markdown("""
    ### 💡 Support
    - Google Drive integration
    - Service account authentication
    - Multi-site data support
    - Automated data processing
    """)

st.markdown("""
<div style='text-align: center; padding: 2rem; color: #666;'>
    <p>🌊 Built with ❤️ using Streamlit & Plotly | S4W Hydrological Monitoring System</p>
</div>
""", unsafe_allow_html=True)
