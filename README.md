# HydroLink - Multi-Sensor Environmental Monitoring Dashboard

A comprehensive Streamlit multipage application for monitoring environmental sensors including rainfall, water levels, and atmospheric conditions. Data is sourced from Google Drive using Service Account authentication for seamless public access.

## 🌟 Features

### Multi-Sensor Monitoring
- **🌧️ TB Sensor**: Rainfall and temperature monitoring with missing data gap visualization
- **💧 HOBO Sensor**: Water level calculations with environmental parameter tracking
- **📊 OBS Sensor**: Multi-parameter water quality monitoring with atmospheric pressure compensation

### Advanced Visualizations
- Interactive Plotly charts with dual y-axis support
- Professional formatting with proper titles and axis labels
- Missing data gap preservation for accurate trend analysis
- Calendar views and comprehensive summary statistics
- Batch data downloads for further analysis

### Google Drive Integration
- Service Account authentication for public access without user login
- Automatic data synchronization from Google Drive folders
- Support for multiple data formats (CSV, TXT)
- Robust error handling and connection management

## 🚀 Live Application

Visit the live dashboard: [HydroLink Dashboard](https://your-app-url.streamlit.app)

## 📁 Project Structure

```
hydro_link/
├── OBS_Sensor_G.py              # Main application file
├── pages/
│   ├── 1_🌧️_TB_Sensor.py        # TB Sensor monitoring page
│   └── 2_💧_HOBO_Sensor.py       # HOBO Sensor monitoring page
├── google_drive_utils.py         # Google Drive Service Account integration
├── requirements.txt              # Python dependencies
├── .streamlit/
│   └── config.toml              # Streamlit configuration
└── assets/                      # Logo and static assets
```

## 🛠️ Technology Stack

- **Frontend**: Streamlit with multipage support
- **Visualization**: Plotly Express for interactive charts
- **Data Processing**: Pandas with smart aggregation
- **Cloud Storage**: Google Drive API v3
- **Authentication**: Service Account (no OAuth required)
- **Deployment**: Streamlit Cloud

## 📊 Data Processing Features

### TB Sensor
- Dual parameter support (Rainfall/Temperature)
- Smart aggregation: sum for rainfall, mean for temperature
- Missing data gap preservation
- Automatic y-axis scaling based on parameter type

### HOBO Sensor
- Pressure to water level conversion
- Sensor metadata integration
- Multi-parameter environmental tracking
- Quality control and outlier detection

### OBS Sensor
- Atmospheric pressure compensation
- Multi-parameter water quality analysis
- Advanced outlier filtering
- Real-time data processing

## 🔧 Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/hydro_link.git
   cd hydro_link
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Google Drive Service Account**
   - Follow instructions in `SERVICE_ACCOUNT_SETUP.md`
   - Place `service_account.json` in project root

4. **Run locally**
   ```bash
   streamlit run OBS_Sensor_G.py
   ```

## 🚀 Deployment

The application is designed for easy deployment on Streamlit Cloud:

1. **GitHub Repository**: Code is version controlled and ready for deployment
2. **Service Account Secrets**: Configure Google Drive credentials in Streamlit secrets
3. **Automatic Updates**: Connected to GitHub for continuous deployment

For detailed deployment instructions, see `DEPLOYMENT_CHECKLIST.md`.

## 📋 Configuration

### Streamlit Secrets
```toml
[google_drive]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account@your-project.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com"
```

## 📈 Data Sources

The application expects Google Drive folders with the following structure:
- `processed/tb/` - TB sensor rainfall and temperature data
- `processed/hobo/` - HOBO sensor water level and environmental data  
- `processed/obs/` - OBS sensor multi-parameter water quality data
- `processed/sensor_metadata/` - Sensor configuration and metadata

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 📞 Support

For questions or support, please open an issue in the GitHub repository.

---

**HydroLink** - Professional environmental monitoring made accessible 🌊
