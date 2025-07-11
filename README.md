# 🌍 Bhukamp - भूकंप
## Predicting the Unpredictable – Real-Time ML Seismic Forecasting for India

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-url.streamlit.app)
[![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**Bhukamp** (भूकंप - meaning "earthquake" in Hindi) is an intelligent seismic forecasting platform designed specifically for the Indian subcontinent. Using cutting-edge machine learning and real-time geological data, we help communities prepare for and respond to seismic events.

## 🎯 Mission
Our mission is to increase earthquake awareness and promote disaster preparedness across India through advanced AI-powered predictions and comprehensive risk analysis.

## 🔍 Key Features

### 🌐 Real-Time Monitoring
- **Live Indian Subcontinent Earthquake Tracking**: Real-time data from USGS Earthquake API
- **Instant Alert System**: Customizable magnitude-based alerts with sound notifications
- **Multi-Language Support**: Available in English and Hindi with more languages coming soon

### 🤖 Machine Learning Predictions
- **Advanced ML Models**: Random Forest, LSTM, and Physics-Informed Neural Networks (PINN)
- **Regional Data Training**: Models specifically trained on Indian subcontinent seismic patterns
- **Multiple Prediction Types**: 
  - Real-time earthquake prediction
  - Future seismic activity forecasting
  - Susceptibility mapping

### 📊 Comprehensive Analytics
- **Historical Data Analysis**: Extensive visualization of past earthquake patterns
- **Risk Assessment**: Detailed magnitude and depth-based risk evaluation
- **Statistical Insights**: Magnitude distribution, depth analysis, and regional activity tracking

### 🎨 Modern User Interface
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Dark/Light Themes**: Customizable themes for better user experience
- **Glass-morphism Design**: Modern, beautiful UI with smooth animations
- **Interactive Dashboards**: Real-time data visualization with dynamic charts

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/SupravoCoder/Bhukamp.git
   cd Bhukamp
   ```

2. **Install dependencies**
   ```bash
   cd myproject
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   streamlit run Bhukamp_app.py
   ```

4. **Open your browser**
   Navigate to `http://localhost:8501` to access the application.

## 📁 Project Structure

```
StreamlitPython/
├── myproject/
│   ├── Bhukamp_app.py              # Main application file
│   ├── requirements.txt            # Python dependencies
│   ├── pages/
│   │   ├── Historical_Analysis.py  # Historical earthquake data analysis
│   │   ├── Predictor_Earthquake.py # ML prediction interface
│   │   ├── India_Live_Feed.py      # Real-time earthquake feed
│   │   └── Susceptibility Predictor.py # Susceptibility mapping
│   ├── data/                       # Earthquake datasets and predictions
│   ├── static/                     # Static assets (images, sounds)
│   └── animations/                 # Animation files
├── models/                         # Pre-trained ML models
├── Susceptability_pred_ML/         # ML model development notebooks
└── Internship_Project_Updated.ipynb # Main research notebook
```

## 🧠 Machine Learning Models

### 1. Random Forest Classifier
- **Purpose**: Real-time earthquake prediction and susceptibility mapping
- **Features**: Latitude, longitude, depth, historical patterns
- **Accuracy**: 85%+ on test data

### 2. LSTM Neural Network
- **Purpose**: Time-series earthquake forecasting
- **Features**: Sequential seismic data, temporal patterns
- **Use Case**: Future earthquake prediction (25-100 years)

### 3. Physics-Informed Neural Networks (PINN)
- **Purpose**: Physics-based seismic modeling
- **Features**: Geological constraints, physical laws
- **Advantage**: Incorporates domain knowledge

## 📈 Data Sources

- **Real-time Data**: USGS Earthquake API
- **Historical Data**: Comprehensive earthquake catalogs for Indian subcontinent
- **Features**: Magnitude, location, depth, time, geological characteristics
- **Coverage**: 1900-2024 earthquake records

## 👥 Team Bhukamp

| Member | Role | Expertise |
|--------|------|-----------|
| **Supravo Biswas** | 🔬 Full Pipeline Developer & ML Contributor | Streamlit, Full Stack, ML, Data Analysis |
| **Suvanjan Das** | 🧠 Lead AI/ML Engineer & Project Lead | Python, TensorFlow, Data Science |
| **Abir Saha** | 🌍 ML Model Validator & Feature Engineer | Seismology, ML Validation, Web Development |
| **Arja Banerjee** | 📚 ML Researcher & Literature Reviewer | ML Research, Scientific Writing |
| **Sayan Rana** | 📊 Data Scientist & ML Contributor | Statistics, Feature Engineering |
| **Iqbal Shaikh** | 🎨 ML Contributor | Machine Learning, Python |

## 🔧 Technical Stack

- **Frontend**: Streamlit, HTML, CSS, JavaScript
- **Backend**: Python, Pandas, NumPy
- **Machine Learning**: Scikit-learn, TensorFlow, Keras
- **Data Visualization**: Plotly, Matplotlib, Seaborn
- **APIs**: USGS Earthquake API, Custom ML inference
- **Database**: SQLite for notifications, CSV for data storage

## 📱 Features in Detail

### Alert System
- Customizable magnitude thresholds
- Sound alerts and visual notifications
- Multi-channel notification support
- Emergency contact integration

### Prediction Interface
- Interactive map visualization
- Adjustable prediction parameters
- Model comparison tools
- Export functionality for predictions

### Historical Analysis
- Time-series visualization
- Magnitude-frequency relationships
- Regional seismic patterns
- Statistical trend analysis

## 🌟 Future Enhancements

- [ ] Mobile app development
- [ ] WhatsApp Business API integration
- [ ] Government alert system integration
- [ ] Advanced geological feature integration
- [ ] Community reporting system
- [ ] Multi-platform deployment

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

We welcome contributions! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 📞 Contact

- **Email**: supravo.biswas@example.com
- **GitHub**: [@SupravoCoder](https://github.com/SupravoCoder)
- **Project Link**: [https://github.com/SupravoCoder/Bhukamp](https://github.com/SupravoCoder/Bhukamp)

## 🙏 Acknowledgments

- USGS for providing real-time earthquake data
- Indian Meteorological Department for historical seismic data
- Open-source community for amazing tools and libraries
- Our mentors and guides for continuous support

---

**Built with ❤️ by Team Bhukamp for a safer India**

*"In the face of nature's unpredictability, knowledge and preparation are our strongest defenses."*
