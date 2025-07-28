import streamlit as st
from PIL import Image
import base64
import os

# Page configuration
st.set_page_config(
    page_title="S4W Sensor Dashboard Suite",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Helper function for encoding images
@st.cache_data
def encode_img_to_base64(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# Main page header
def main():
    # Logo and header
    logo_path = "assets/logo_1.png"
    if os.path.exists(logo_path):
        logo_base64 = encode_img_to_base64(logo_path)
        st.markdown(f"""
            <div style='display: flex; justify-content: space-between; align-items: center; padding: 20px 10px 10px 10px;'>
                <div>
                    <h1 style='margin-bottom: 0;'>🌊 S4W Sensor Dashboard Suite</h1>
                    <p style='margin-top: 5px; color: gray; font-size: 18px; font-weight: 500;'>Complete hydrological monitoring system</p>
                </div>
                <div>
                    <img src='data:image/png;base64,{logo_base64}' style='height:100px;'/>
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div style='text-align: center; padding: 20px;'>
                <h1>🌊 S4W Sensor Dashboard Suite</h1>
                <p style='color: gray; font-size: 18px;'>Complete hydrological monitoring system</p>
            </div>
        """, unsafe_allow_html=True)

    # Welcome message
    st.markdown("""
    ## Welcome to the S4W Sensor Dashboard Suite!
    
    This comprehensive dashboard provides access to all your hydrological sensor data through an intuitive interface. 
    Choose from the navigation menu to explore different sensor types and their data.
    """)

    # Dashboard overview cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 🌧️ TB Sensor Dashboard
        **Rainfall & Temperature Monitoring**
        
        - High-resolution rainfall data
        - Temperature measurements
        - Missing data gap visualization
        - Comprehensive summary statistics
        - Professional plot exports
        
        *Access multi-year rainfall and temperature data with advanced visualization features.*
        """)
    
    with col2:
        st.markdown("""
        ### 💧 HOBO Sensor Dashboard
        **Water Level & Environmental Monitoring**
        
        - Automated water level calculations
        - Pressure sensor data
        - Temperature tracking
        - Multi-parameter analysis
        - Time-series visualization
        
        *Monitor water levels and environmental conditions with precision sensors.*
        """)
    
    with col3:
        st.markdown("""
        ### 🔬 OBS Sensor Dashboard
        **Multi-Parameter Water Quality**
        
        - Optical backscatter measurements
        - Ambient light analysis
        - Atmospheric pressure compensation
        - Water quality indicators
        - Advanced data filtering
        
        *Comprehensive water quality monitoring with optical sensors.*
        """)

    # Data source information
    st.markdown("---")
    st.markdown("## 📊 Data Sources & Features")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 📁 Data Access Options
        - **Google Drive Integration**: Cloud-based data access with service account authentication
        - **Local File Support**: Fallback for local development and testing
        - **Real-time Loading**: Data is loaded dynamically from your selected source
        - **Automatic Caching**: Improved performance with intelligent data caching
        """)
    
    with col2:
        st.markdown("""
        ### 🎯 Key Features
        - **Interactive Visualizations**: Built with Plotly for professional charts
        - **Mobile Responsive**: Works on desktop, tablet, and mobile devices
        - **Export Capabilities**: Download plots as high-quality PNG images
        - **Missing Data Handling**: Intelligent gap visualization and statistics
        """)

    # Getting started
    st.markdown("---")
    st.markdown("## 🚀 Getting Started")
    
    st.markdown("""
    1. **Select a Dashboard**: Use the navigation menu on the left to choose your sensor type
    2. **Choose Data Source**: Toggle between Google Drive and local data sources
    3. **Select Your Data**: Pick the site and time period you want to analyze
    4. **Explore**: Use the interactive controls to visualize your data
    5. **Export**: Download professional plots for reports and presentations
    """)

    # Technical specifications
    with st.expander("🔧 Technical Specifications"):
        st.markdown("""
        ### Data Coverage
        - **TB Sensors**: 2018-2023 rainfall and temperature data
        - **HOBO Sensors**: 2023 water level and environmental data  
        - **OBS Sensors**: 2023 water quality and optical measurements
        
        ### Supported Formats
        - **Input**: CSV files with timestamp indexing
        - **Output**: High-resolution PNG plots (1200x600px)
        - **Data Processing**: Pandas-based with automatic type conversion
        
        ### Cloud Integration
        - **Authentication**: Google Service Account (no user login required)
        - **Storage**: Google Drive with folder-based organization
        - **Deployment**: Streamlit Cloud compatible with secrets management
        """)

    # Footer
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; padding: 20px; color: #666;'>
            <p>🌊 Built with ❤️ using Streamlit & Plotly | S4W Hydrological Monitoring System</p>
            <p>From small sensors to big insights — monitor what matters</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
