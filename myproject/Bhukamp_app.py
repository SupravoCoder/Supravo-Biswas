import streamlit as st
import json
import requests
import pandas as pd
from datetime import timedelta, datetime
import time
import base64
import os

# ------------------ Page Configuration ------------------
st.set_page_config(
    page_title="Bhukamp - भूकंप",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ------------------ Multi-language Support ------------------
LANGUAGES = {
    "en": {"name": "English", "flag": "🇺🇸"},
    "hi": {"name": "हिंदी", "flag": "🇮🇳"},
    "bn": {"name": "বাংলা", "flag": "🇧🇩"},
    "ta": {"name": "தமிழ்", "flag": "🏴"},
    "te": {"name": "తెలుగు", "flag": "🏴"},
    "mr": {"name": "मराठी", "flag": "🏴"}
}

TRANSLATIONS = {
    "en": {
        "title": "🌍 Bhukamp - भूकंप",
        "subtitle": "Predicting the Unpredictable – Real-Time ML Seismic Forecasting for India",
        "description": "A web app powered by machine learning to help detect, forecast, and prepare for seismic activity in the Indian subcontinent.",
        "key_features": "🔍 Key Features",
        "about": "📘 About Bhukamp",
        "mission": "🎯 Mission",
        "team": "👥 Meet Team Bhukamp",
        "live_snapshot": "🇮🇳 Live Indian Subcontinent Earthquake Snapshot",
        "latest_earthquake": "🛰️ Latest Indian Region Earthquake",
        "magnitude": "Magnitude",
        "location": "Location",
        "time_utc": "Time (UTC)",
        "time_ist": "Time (IST)",
        "geographic_details": "📍 Geographic Details",
        "latitude": "Latitude",
        "longitude": "Longitude",
        "depth": "Depth",
        "risk_assessment": "Risk Assessment",
        "alert_settings": "🔔 Alert Settings",
        "enable_sound": "Enable Sound Alerts",
        "alert_threshold": "Alert Threshold (Magnitude)",
        "theme_toggle": "🎨 Theme",
        "light_mode": "☀️ Light Mode",
        "dark_mode": "🌙 Dark Mode"
    },
    "hi": {
        "title": "🌍 भूकंप - Bhukamp",
        "subtitle": "अप्रत्याशित की भविष्यवाणी – भारत के लिए वास्तविक समय ML भूकंप पूर्वानुमान",
        "description": "भारतीय उपमहाद्वीप में भूकंपीय गतिविधि का पता लगाने, पूर्वानुमान और तैयारी में मदद के लिए मशीन लर्निंग द्वारा संचालित एक वेब ऐप।",
        "key_features": "🔍 मुख्य विशेषताएं",
        "about": "📘 भूकंप के बारे में",
        "mission": "🎯 मिशन",
        "team": "👥 टीम भूकंप से मिलें",
        "live_snapshot": "🇮🇳 लाइव भारतीय उपमहाद्वीप भूकंप स्नैपशॉट",
        "latest_earthquake": "🛰️ नवीनतम भारतीय क्षेत्र भूकंप",
        "magnitude": "परिमाण",
        "location": "स्थान",
        "time_utc": "समय (UTC)",
        "time_ist": "समय (IST)",
        "geographic_details": "📍 भौगोलिक विवरण",
        "latitude": "अक्षांश",
        "longitude": "देशांतर",
        "depth": "गहराई",
        "risk_assessment": "जोखिम मूल्यांकन"
    }
}

# Initialize session state for settings
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'
if 'language' not in st.session_state:
    st.session_state.language = 'en'
if 'sound_alerts' not in st.session_state:
    st.session_state.sound_alerts = True
if 'alert_threshold' not in st.session_state:
    st.session_state.alert_threshold = 4.0
if 'last_alert_time' not in st.session_state:
    st.session_state.last_alert_time = None

# ------------------ Theme and Settings Sidebar ------------------
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    
    # Language Selection
    selected_lang = st.selectbox(
        "🌐 Language",
        options=list(LANGUAGES.keys()),
        format_func=lambda x: f"{LANGUAGES[x]['flag']} {LANGUAGES[x]['name']}",
        index=list(LANGUAGES.keys()).index(st.session_state.language),
        key="lang_select"
    )
    if selected_lang != st.session_state.language:
        st.session_state.language = selected_lang
        st.rerun()
    
    # Theme Toggle
    theme_option = st.radio(
        "🎨 Theme",
        ["🌙 Dark Mode", "☀️ Light Mode"],
        index=0 if st.session_state.theme == 'dark' else 1,
        key="theme_radio"
    )
    new_theme = 'dark' if '🌙' in theme_option else 'light'
    if new_theme != st.session_state.theme:
        st.session_state.theme = new_theme
        st.rerun()
    
    # Alert Settings
    st.markdown("---")
    st.markdown("### 🔔 Alert Settings")
    st.session_state.sound_alerts = st.checkbox(
        "🔊 Enable Sound Alerts", 
        value=st.session_state.sound_alerts
    )
    st.session_state.alert_threshold = st.slider(
        "⚡ Alert Threshold (Magnitude)",
        min_value=2.0,
        max_value=8.0,
        value=st.session_state.alert_threshold,
        step=0.1,
        help="Get alerts for earthquakes above this magnitude"
    )

# Get current language translations
t = TRANSLATIONS.get(st.session_state.language, TRANSLATIONS["en"])

# ------------------ Dynamic CSS based on theme ------------------
def get_theme_css():
    if st.session_state.theme == 'light':
        return """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;700&display=swap');
            html, body, .stApp {
                height: 100%;
                font-family: 'Roboto', sans-serif;
                background: linear-gradient(-45deg, #e8f5e8, #f0f8ff, #e6f3ff, #f5f5dc, #fff8dc, #f0fff0, #e0f6ff);
                background-size: 400% 400%;
                animation: smoothGradient 25s ease infinite;
                color: #2c3e50;
            }
            .glass-container {
                background: rgba(255, 255, 255, 0.8);
                backdrop-filter: blur(10px);
                border-radius: 15px;
                padding: 1.5rem;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.9);
            }
            .title { color: #2c3e50; text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); }
            .subtitle { color: #34495e; }
            section[data-testid="stSidebar"] {
                background: linear-gradient(-45deg, #f8f9fa, #e9ecef, #f1f3f4, #ffffff);
                color: #2c3e50;
            }
            section[data-testid="stSidebar"] * { color: #2c3e50 !important; }
        </style>
        """
    else:
        return """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;700&display=swap');
            html, body, .stApp {
                height: 100%;
                font-family: 'Roboto', sans-serif;
                background: linear-gradient(-45deg, #1b4332, #2d6a4f, #1f4e79, #40916c, #2563eb, #52b788, #3b82f6);
                background-size: 400% 400%;
                animation: smoothGradient 25s ease infinite;
                color: #f8f8f8;
            }
            .glass-container {
                background: rgba(255, 255, 255, 0.12);
                backdrop-filter: blur(15px);
                border-radius: 15px;
                padding: 1.5rem;
                box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
                border: 1px solid rgba(255, 255, 255, 0.18);
            }
            .title { color: #ffffff; text-shadow: 0 4px 10px rgba(0, 0, 0, 0.3); }
            .subtitle { color: #e0e0e0; }
            section[data-testid="stSidebar"] {
                background: linear-gradient(-45deg, #1b4332, #2d6a4f, #1f4e79, #40916c, #2563eb, #52b788, #3b82f6);
                color: #f8f8f8;
            }
            section[data-testid="stSidebar"] * { color: #f8f8f8 !important; }
        </style>
        """

# Apply theme CSS
st.markdown(get_theme_css(), unsafe_allow_html=True)

st.markdown("""
<style>
    @keyframes smoothGradient {
        0% { background-position: 0% 50%; }
        25% { background-position: 50% 0%; }
        50% { background-position: 100% 50%; }
        75% { background-position: 50% 100%; }
        100% { background-position: 0% 50%; }
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    @keyframes wave {
        0% { transform: scale(0); opacity: 1; }
        100% { transform: scale(4); opacity: 0; }
    }
    .title {
        font-size: 3.5em;
        font-weight: 700;
        animation: fadeIn 1.8s ease-out;
    }
    .subtitle {
        font-size: 1.3em;
        margin-bottom: 1.5rem;
        animation: fadeIn 2s ease-out;
    }
    .alert-notification {
        position: fixed;
        top: 80px;
        right: 20px;
        z-index: 9999;
        background: #ff4444;
        color: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 4px 20px rgba(255, 68, 68, 0.4);
        animation: pulse 2s infinite;
    }
    .wave-animation {
        position: relative;
        display: inline-block;
    }
    .wave-animation::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 20px;
        height: 20px;
        border: 2px solid #ff4444;
        border-radius: 50%;
        transform: translate(-50%, -50%);
        animation: wave 2s infinite;
    }
    .earthquake-marker {
        animation: pulse 2s infinite;
        filter: drop-shadow(0 0 10px rgba(255, 68, 68, 0.8));
    }
    /* Enhanced team cards and other existing styles */
    .team-card {
        background: rgba(255, 255, 255, 0.18);
        backdrop-filter: blur(12px);
        border-radius: 15px;
        padding: 2rem 1.5rem;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.25);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        height: 100%;
        min-height: 500px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: flex-start;
        position: relative;
        width: 100%;
    }
    .team-card img {
        width: 120px !important;
        height: 120px !important;
        border-radius: 50% !important;
        object-fit: cover !important;
        margin: 0 auto 1.5rem auto !important;
        border: 3px solid rgba(255, 255, 255, 0.3) !important;
        display: block !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2) !important;
        flex-shrink: 0;
        align-self: center;
    }
    .team-card .image-container {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        overflow: hidden;
        margin: 0 auto 1.5rem auto;
        border: 3px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(45deg, #52b788, #40916c);
        flex-shrink: 0;
        position: relative;
        left: 50%;
        transform: translateX(-50%);
    }
    .team-card .image-container img {
        width: 120px !important;
        height: 120px !important;
        border-radius: 50% !important;
        border: none !important;
        margin: 0 !important;
        box-shadow: none !important;
        object-fit: cover !important;
        display: block !important;
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
    }
    .team-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(31, 38, 135, 0.6);
        background: rgba(255, 255, 255, 0.22);
    }
    .team-name {
        font-size: 1.2em;
        font-weight: bold;
        margin: 0.5rem 0;
        width: 100%;
        text-align: center;
        display: block;
    }
    .team-role {
        font-size: 1em;
        color: rgba(255, 255, 255, 0.9);
        margin: 0 0 0.5rem 0;
        width: 100%;
        text-align: center;
        display: block;
    }
    .team-description {
        font-size: 0.9em;
        margin: 1rem 0;
        line-height: 1.4;
        width: 100%;
        text-align: center;
        display: block;
    }
    .skill-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        justify-content: center;
        align-items: center;
        margin: 1rem 0 0 0;
        width: 100%;
    }
    .skill-tag {
        background: rgba(255, 255, 255, 0.25);
        color: #ffffff;
        padding: 0.2rem 0.6rem;
        border-radius: 15px;
        font-size: 0.75em;
        font-weight: 600;
        border: 1px solid rgba(255, 255, 255, 0.4);
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
        display: inline-block;
        margin: 0.2rem;
    }
    .footer {
        text-align: center;
        font-size: 0.85em;
        color: #cccccc;
        margin-top: 40px;
    }
    ::-webkit-scrollbar {
        width: 8px;
    }
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(45deg, #40916c, #2563eb);
        border-radius: 10px;
    }
    ::-webkit-scrollbar-track {
        background: transparent;
    }
</style>
""", unsafe_allow_html=True)

# ------------------ Hero Section ------------------
with st.container():
    st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
    left_col, right_col = st.columns(2)
    with left_col:
        st.markdown(f"<div class='title'>{t['title']}</div>", unsafe_allow_html=True)
        st.markdown(f"<h3><div class='subtitle'>{t['subtitle']}</div></h3>", unsafe_allow_html=True)
        st.write(f"<h4>{t['description']}</h4>", unsafe_allow_html=True)

        st.markdown(f"### {t['key_features']}")
        if st.session_state.language == 'hi':
            st.markdown("- 🌐 भारतीय उपमहाद्वीप की वास्तविक समय भूकंप निगरानी")
            st.markdown("- 🤖 भूकंपीय गतिविधि के लिए मशीन लर्निंग आधारित भविष्यवाणी")
            st.markdown("- 📊 भारत के लिए ऐतिहासिक भूकंपीय डेटा विश्लेषण")
            st.markdown("- 🧠 क्षेत्रीय डेटा पैटर्न पर प्रशिक्षित उन्नत मॉडल")
        else:
            st.markdown("- 🌐 Real-time Indian subcontinent earthquake monitoring")
            st.markdown("- 🤖 Machine Learning-based predictions for seismic activity")
            st.markdown("- 📊 Historical seismic data analysis for India")
            st.markdown("- 🧠 Advanced models trained on regional data patterns")

        # Quick navigation buttons
        col_nav1, col_nav2, col_nav3 = st.columns(3)
        with col_nav1:
            st.page_link("pages/Historical_Earthquake_Data-Visualization.py", label="📊 Historical Analysis")
        with col_nav2:
            st.page_link("pages/Predictor_Earthquake.py", label="🔮 ML Predictions")
        with col_nav3:
            st.page_link("pages/Earthquake_Notifications.py", label="📱 Notifications")

    with right_col:
        st.info("🚀 **Welcome to Bhukamp!** Your trusted earthquake monitoring companion for India.")
        
        # Quick stats or live indicator
        st.success("🛰️ **Live Data Source**: USGS Earthquake API")
        st.warning("🎯 **Focus Region**: Indian Subcontinent")
        st.info("🤖 **AI Models**: Random Forest & PINN")
        
        # Alert status indicator
        if st.session_state.sound_alerts:
            st.success(f"🔔 **Alerts Enabled** (Threshold: M{st.session_state.alert_threshold})")
        else:
            st.info("🔕 **Alerts Disabled**")
        
    st.markdown("</div>", unsafe_allow_html=True)

# ------------------ About Section ------------------
with st.container():
    st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
    st.markdown("## 📘 About Bhukamp")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.write("""
            **Bhukamp** (भूकंप - meaning "earthquake" in Hindi) is an intelligent seismic forecasting platform 
            designed specifically for the Indian subcontinent. Using cutting-edge machine learning and real-time 
            geological data, we help communities prepare for and respond to seismic events.
            
            Our mission is to increase earthquake awareness and promote disaster preparedness across India 
            through advanced AI-powered predictions and comprehensive risk analysis.
        """)
    
    with col2:
        st.markdown("### 🎯 Mission")
        st.markdown("- 🛡️ Enhance earthquake preparedness")
        st.markdown("- 🔬 Advance seismic research")
        st.markdown("- 🇮🇳 Serve Indian communities")
        st.markdown("- 💡 Innovate with AI/ML")
    
    st.markdown("</div>", unsafe_allow_html=True)

# ------------------ Enhanced Real-Time Earthquake Functions ------------------
def get_alert_sound():
    """Generate alert sound using base64 encoded audio"""
    # Simple beep sound (you can replace with actual audio file)
    return """
    <audio autoplay>
        <source src="data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmUcBj2X2fPBdSMFl3PD7d+UQwsWaq7t559NFAo=" type="audio/wav">
    </audio>
    """

def play_alert_sound():
    """Play alert sound using HTML audio"""
    if st.session_state.sound_alerts:
        st.markdown(get_alert_sound(), unsafe_allow_html=True)

def get_multiple_earthquakes(hours=24, limit=50):
    """Get multiple recent earthquakes for data analysis"""
    india_bounds = {
        "minlatitude": 6.0,
        "maxlatitude": 37.0,
        "minlongitude": 68.0,
        "maxlongitude": 97.0
    }
    
    start_time = (datetime.now() - timedelta(hours=hours)).strftime('%Y-%m-%d')
    
    url = (
        "https://earthquake.usgs.gov/fdsnws/event/1/query"
        f"?format=geojson&limit={limit}&orderby=time"
        f"&minlatitude={india_bounds['minlatitude']}"
        f"&maxlatitude={india_bounds['maxlatitude']}"
        f"&minlongitude={india_bounds['minlongitude']}"
        f"&maxlongitude={india_bounds['maxlongitude']}"
        f"&starttime={start_time}"
    )
    
    try:
        r = requests.get(url)
        data = r.json()
        
        earthquakes = []
        for feature in data["features"]:
            props = feature["properties"]
            coords = feature["geometry"]["coordinates"]
            
            quake_data = {
                "magnitude": props["mag"],
                "place": props["place"],
                "time": pd.to_datetime(props["time"], unit="ms"),
                "latitude": coords[1],
                "longitude": coords[0],
                "depth": coords[2] if len(coords) > 2 else 0,
                "id": props.get("id", "")
            }
            earthquakes.append(quake_data)
        
        return earthquakes
    except Exception as e:
        st.error(f"Error fetching earthquake data: {e}")
        return []

def check_for_alerts(latest_quake):
    """Check if latest earthquake meets alert criteria"""
    if not latest_quake or not st.session_state.sound_alerts:
        return False
    
    magnitude = latest_quake.get('magnitude', 0)
    quake_time = latest_quake.get('time')
    
    # Check if magnitude exceeds threshold
    if magnitude >= st.session_state.alert_threshold:
        # Check if this is a new alert (not already alerted for this quake)
        if (st.session_state.last_alert_time is None or 
            quake_time > st.session_state.last_alert_time):
            st.session_state.last_alert_time = quake_time
            return True
    
    return False

def get_latest_quake():
    """Get the latest earthquake from Indian subcontinent"""
    # Indian subcontinent bounding box coordinates
    india_bounds = {
        "minlatitude": 6.0,      # Southern tip (near Kanyakumari)
        "maxlatitude": 37.0,     # Northern border (Kashmir region)
        "minlongitude": 68.0,    # Western border (near Pakistan border)
        "maxlongitude": 97.0     # Eastern border (near Myanmar border)
    }
    
    url = (
        "https://earthquake.usgs.gov/fdsnws/event/1/query"
        f"?format=geojson&limit=1&orderby=time"
        f"&minlatitude={india_bounds['minlatitude']}"
        f"&maxlatitude={india_bounds['maxlatitude']}"
        f"&minlongitude={india_bounds['minlongitude']}"
        f"&maxlongitude={india_bounds['maxlongitude']}"
    )
    try:
        with st.spinner("Fetching latest Indian earthquake data..."):
            r = requests.get(url)
            data = r.json()
            
            if not data["features"]:
                # If no recent earthquakes in India, get the most recent one from a longer time period
                url_extended = (
                    "https://earthquake.usgs.gov/fdsnws/event/1/query"
                    f"?format=geojson&limit=1&orderby=time"
                    f"&minlatitude={india_bounds['minlatitude']}"
                    f"&maxlatitude={india_bounds['maxlatitude']}"
                    f"&minlongitude={india_bounds['minlongitude']}"
                    f"&maxlongitude={india_bounds['maxlongitude']}"
                    f"&starttime={(pd.Timestamp.now() - pd.Timedelta(days=30)).strftime('%Y-%m-%d')}"
                )
                r = requests.get(url_extended)
                data = r.json()
                
                if not data["features"]:
                    return None
            
            feature = data["features"][0]["properties"]
            geometry = data["features"][0]["geometry"]
            
            return {
                "magnitude": feature["mag"],
                "place": feature["place"],
                "time": pd.to_datetime(feature["time"], unit="ms"),
                "latitude": geometry["coordinates"][1],
                "longitude": geometry["coordinates"][0],
                "depth": geometry["coordinates"][2] if len(geometry["coordinates"]) > 2 else "N/A"
            }
    except Exception as e:
        st.error(f"⚠️ Could not fetch latest earthquake data: {e}")
        return None

with st.container():
    st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
    st.markdown(f"## {t.get('live_snapshot', '🇮🇳 Live Indian Subcontinent Earthquake Snapshot')}")

    # Auto-refresh every 30 seconds
    if st.button("🔄 Refresh Data", key="refresh_btn"):
        st.rerun()
    
    latest = get_latest_quake()
    
    # Check for alerts
    if check_for_alerts(latest):
        st.error("🚨 **EARTHQUAKE ALERT!** 🚨")
        play_alert_sound()
        st.markdown("""
        <div class="alert-notification">
            <h3>⚠️ High Magnitude Earthquake Detected!</h3>
            <p>Check the details below for more information.</p>
        </div>
        """, unsafe_allow_html=True)
    
    if latest:
        # Create columns for better layout
        col1, col2 = st.columns(2)
        
        with col1:
            magnitude_class = "wave-animation" if latest['magnitude'] >= st.session_state.alert_threshold else ""
            
            st.success(f"""🛰️ **{t.get('latest_earthquake', 'Latest Indian Region Earthquake')}**

**{t.get('magnitude', 'Magnitude')}**: {latest['magnitude']}

**{t.get('location', 'Location')}**: {latest['place']}

**{t.get('time_utc', 'Time (UTC)')}**: {latest['time'].strftime('%Y-%m-%d %H:%M:%S')} UTC""")

            ist_time = latest['time'] + timedelta(hours=5, minutes=30)
            st.info(f"**{t.get('time_ist', 'Time (IST)')}**: {ist_time.strftime('%Y-%m-%d %H:%M:%S')} IST")
        
        with col2:
            st.info(f"📍 **{t.get('geographic_details', 'Geographic Details')}**\n\n"
                   f"**{t.get('latitude', 'Latitude')}**: {latest['latitude']:.3f}°\n\n"
                   f"**{t.get('longitude', 'Longitude')}**: {latest['longitude']:.3f}°\n\n"
                   f"**{t.get('depth', 'Depth')}**: {latest['depth']} km")
            
            # Detailed Risk Assessment with Symbols
            magnitude = latest['magnitude']
            depth = latest['depth']
            
            # Risk level based on magnitude (Richter Scale)
            if magnitude >= 8.0:
                risk_level = "🔴 EXTREME RISK"
                risk_symbol = "🚨"
                risk_description = "Great Earthquake - Catastrophic damage expected"
                risk_color = "error"
            elif magnitude >= 7.0:
                risk_level = "🟠 MAJOR RISK"
                risk_symbol = "⚠️"
                risk_description = "Major Earthquake - Serious damage expected"
                risk_color = "error"
            elif magnitude >= 6.0:
                risk_level = "🟡 HIGH RISK"
                risk_symbol = "⚡"
                risk_description = "Strong Earthquake - Damage to buildings"
                risk_color = "warning"
            elif magnitude >= 5.0:
                risk_level = "🟠 MODERATE RISK"
                risk_symbol = "📊"
                risk_description = "Moderate Earthquake - Felt by most people"
                risk_color = "warning"
            elif magnitude >= 4.0:
                risk_level = "🟢 LOW RISK"
                risk_symbol = "📉"
                risk_description = "Light Earthquake - Felt by many people"
                risk_color = "info"
            else:
                risk_level = "🔵 MINIMAL RISK"
                risk_symbol = "🔹"
                risk_description = "Minor/Micro Earthquake - Often not felt"
                risk_color = "success"
            
            # Additional depth consideration
            if isinstance(depth, (int, float)) and depth < 70:
                depth_warning = "⚠️ Shallow earthquake - potentially more damaging"
            elif isinstance(depth, (int, float)) and depth > 300:
                depth_warning = "ℹ️ Deep earthquake - less surface impact"
            else:
                depth_warning = "📍 Intermediate depth earthquake"
            
            # Display risk assessment
            if risk_color == "error":
                st.error(f"{risk_symbol} **{risk_level}**\n\n{risk_description}")
            elif risk_color == "warning":
                st.warning(f"{risk_symbol} **{risk_level}**\n\n{risk_description}")
            elif risk_color == "info":
                st.info(f"{risk_symbol} **{risk_level}**\n\n{risk_description}")
            else:
                st.success(f"{risk_symbol} **{risk_level}**\n\n{risk_description}")
            
            # Depth consideration
            st.caption(f"🏔️ **Depth Analysis**: {depth_warning}")
    else:
        st.warning("⚠️ No recent earthquake data available for the Indian subcontinent from USGS.")
        st.info("💡 This could mean there have been no significant earthquakes in the region recently, or there might be a temporary issue with the data source.")
    
    st.markdown("</div>", unsafe_allow_html=True)

# ------------------ Enhanced Data Analysis Section ------------------
with st.container():
    st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
    st.markdown("## 📊 Earthquake Data Analysis")
    
    tab1, tab2 = st.tabs(["� Recent Earthquakes", "� Statistics"])
    
    with tab1:
        st.markdown("### 📋 Recent Earthquake Activity")
        earthquakes = get_multiple_earthquakes(hours=168, limit=50)  # Last week
        
        if earthquakes:
            df = pd.DataFrame(earthquakes)
            df['time_ist'] = df['time'] + timedelta(hours=5, minutes=30)
            df = df.sort_values('time', ascending=False)
            
            # Display recent earthquakes table
            st.dataframe(
                df[['time_ist', 'magnitude', 'place', 'depth']].rename(columns={
                    'time_ist': 'Time (IST)',
                    'magnitude': 'Magnitude',
                    'place': 'Location',
                    'depth': 'Depth (km)'
                }),
                use_container_width=True
            )
            
            # Quick statistics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Earthquakes", len(earthquakes))
            with col2:
                avg_mag = df['magnitude'].mean()
                st.metric("Average Magnitude", f"{avg_mag:.1f}")
            with col3:
                max_mag = df['magnitude'].max()
                st.metric("Highest Magnitude", f"{max_mag:.1f}")
            with col4:
                shallow_count = len(df[df['depth'] < 70])
                st.metric("Shallow Earthquakes", shallow_count)
        else:
            st.warning("No recent earthquake data available")
    
    with tab2:
        st.markdown("### � Earthquake Statistics & Insights")
        earthquakes = get_multiple_earthquakes(hours=720, limit=100)  # Last 30 days
        
        if earthquakes:
            df = pd.DataFrame(earthquakes)
            
            # Magnitude distribution
            st.markdown("#### 📈 Magnitude Distribution")
            mag_ranges = {
                "Minor (2.0-2.9)": len(df[(df['magnitude'] >= 2.0) & (df['magnitude'] < 3.0)]),
                "Light (3.0-3.9)": len(df[(df['magnitude'] >= 3.0) & (df['magnitude'] < 4.0)]),
                "Moderate (4.0-4.9)": len(df[(df['magnitude'] >= 4.0) & (df['magnitude'] < 5.0)]),
                "Strong (5.0-5.9)": len(df[(df['magnitude'] >= 5.0) & (df['magnitude'] < 6.0)]),
                "Major (6.0+)": len(df[df['magnitude'] >= 6.0])
            }
            
            for category, count in mag_ranges.items():
                if count > 0:
                    st.metric(category, count)
            
            # Depth analysis
            st.markdown("#### 🏔️ Depth Analysis")
            depth_ranges = {
                "Shallow (0-70 km)": len(df[df['depth'] < 70]),
                "Intermediate (70-300 km)": len(df[(df['depth'] >= 70) & (df['depth'] < 300)]),
                "Deep (300+ km)": len(df[df['depth'] >= 300])
            }
            
            for category, count in depth_ranges.items():
                if count > 0:
                    st.metric(category, count)
            
            # Regional activity
            st.markdown("#### 🌍 Regional Activity")
            if not df.empty:
                most_active_region = df['place'].value_counts().head(1)
                if not most_active_region.empty:
                    st.info(f"**Most Active Region**: {most_active_region.index[0]} ({most_active_region.iloc[0]} earthquakes)")
                
                # Recent activity summary
                recent_24h = len(df[df['time'] > (datetime.now() - timedelta(hours=24))])
                recent_7d = len(df[df['time'] > (datetime.now() - timedelta(days=7))])
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Last 24 Hours", recent_24h)
                with col2:
                    st.metric("Last 7 Days", recent_7d)
        else:
            st.warning("No earthquake data available for statistical analysis")
    
    st.markdown("</div>", unsafe_allow_html=True)

# ------------------ Meet Our Team Section ------------------
###with st.container():
    #st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
    #st.markdown("##  Meet Team Bhukamp")
    #st.markdown("### *The minds behind India's earthquake forecasting innovation*")
    
    # Team members data
   # team_members = [
      #  {
    #        "name": "Supravo Biswas",
         #   "role": "🔬 Full Pipeline Developer & ML Contributor",
           # "avatar": "myproject/static/images/team/supravo_biswas.jpg",
            #"description": "Developed most of the pipeline for the Streamlit web app, integrating all components for seamless user experience and analytics. Contributed to machine learning model development, data analysis, and validation, ensuring robust and scalable earthquake prediction workflows.",
           # "skills": ["Streamlit", "Full Stack Development", "Pipeline Engineering", "Machine Learning", "Research", "Data Analysis", "Seismic Modeling", "Python", "Statistical Analysis", "Scientific Computing"]
     #   },
     #   {
       #     "name": "Suvanjan Das",
         #   "avatar": "myproject/static/images/team/suvanjan_das.jpg",
           # "description": "Expert in machine learning algorithms and seismic data analysis. Leads the development of predictive models for earthquake forecasting using Random Forest and PINN algorithms.",
         #   "skills": ["Python", "TensorFlow", "Scikit-learn", "Data Science", "Streamlit", "Geospatial Analysis"]
       # },
      #  {
          #  "name": "Abir Saha",
         #   "role": "🌍 ML Model Validator, Feature Engineer & Web Contributor",
         #   "avatar": "myproject/static/images/team/abir_saha.jpg",
        #    "description": "Played a key role in refining and validating the machine learning models for earthquake prediction. Improved the model outputs by correcting configurations, optimizing feature selection, and ensuring realistic results. Also developed a Random Forest-based susceptibility predictor, contributed to parts of the web app, and identified essential data features to enhance prediction quality.",
         #   "skills": ["Seismology", "Geophysics", "Risk Assessment", "Research", "Data Validation", "Streamlit", "Feature Engineering", "ML Validation", "Web Development", "Python"]
       # },
       # {
          #  "name": "Arja Banerjee",
          #  "role": " ML Researcher, Literature Reviewer & Idea Originator",
          #  "avatar": "myproject/static/images/team/arja_banerjee.jpg",
          #  "description": "Selected and originated the core idea for Bhukamp, conducted extensive literature review, and led foundational research. Contributed to machine learning model development and ensured the scientific rigor of the project.",
          #  "skills": ["ML Research", "Literature Review", "Idea Selection", "Python", "Research", "Data Analysis", "Scientific Writing", "Project Initiation", "Seismic Modeling"]
      #  },
      #  {
           # "name": "Sayan Rana",
           # "role": "📊 Data Scientist & ML Contributor",
          #  "avatar": "myproject/static/images/team/sayan_rana.jpg",
         #   "description": "Specializes in feature engineering, statistical analysis of seismic patterns, and machine learning model development. Responsible for data preprocessing, model evaluation metrics, and ensuring robust ML workflows.",
         #   "skills": ["Statistics", "Pandas", "NumPy", "Data Visualization", "Feature Engineering", "Model Validation", "Machine Learning", "Python"]
      #  },
      #  "name": "Iqbal Shaikh",
           # "role": "🎨 ML Contributor",
          #  "avatar": "myproject/static/images/team/iqbal_shaikh.jpg",
          #  "description": "Contributed to machine learning workflows and ensured the platform is user-friendly for emergency responders and researchers.",
         #   "skills": ["Machine Learning", "Python", "Figma", "Design Systems", "Accessibility", "User Research", "Prototyping", "CSS"]
       # }
   # ]
    
    # Display team members in rows of 2
  #    cols = st.columns(2)
     #   for j, member in enumerate(team_members[i:i+2]):
     #       with cols[j]:
                # Create the team card with proper image handling
       #         avatar_path = member["avatar"]
                
                # Generate initials for fallback
         #       initials = ''.join([name[0] for name in member["name"].split()[:2]])
                
                # Check if image exists and create appropriate image tag
           #     if os.path.exists(avatar_path):
            #        try:
              #          with open(avatar_path, "rb") as img_file:
                   #         img_data = base64.b64encode(img_file.read()).decode()
                  #          img_src = f"data:image/png;base64,{img_data}"
                  #  except:
                        #img_src = f"https://ui-avatars.com/api/?name={'+'.join(member['name'].split())}&size=120&background=52b788&color=ffffff&bold=true"
             #   else:
                 #   img_src = f"https://ui-avatars.com/api/?name={'+'.join(member['name'].split())}&size=120&background=52b788&color=ffffff&bold=true"
                
                #st.markdown(f"""
                #<div class='team-card'>
                    #<div class='image-container'>
                        #<img src="{img_src}" alt="{member['name']}" />
                   # </div>
                    #<div class='team-name'>{member["name"]}</div>
                    #<div class='team-role'>{member["role"]}</div>
                    #<div class='team-description'>{member["description"]}</div>
                    #<div class='skill-tags'>
                        #{''.join([f"<span class='skill-tag'>{skill}</span>" for skill in member["skills"]])}
                    #</div>
                #</div>
                #""", unsafe_allow_html=True)
    
    # Team stats and achievements
   # col1, col2, col3, col4 = st.columns(4)
    
   # with col1:
       # st.metric("👥 Team Members", "6", "Experts")
  #  with col2:
      #  st.metric("� Combined Experience", "2+", "Years")
    #with col3:
       # st.metric("🏆 ML Models Developed", "5", "Advanced")
   # with col4:
      #  st.metric("📊 Data Points Analyzed", "1M+", "Seismic Events")
    
   # st.markdown("</div>", unsafe_allow_html=True)

# ------------------ Footer ------------------
st.markdown("---")
st.markdown("<div class='footer'>© 2025 Bhukamp - भूकंप | Built with ❤️ from Team Bhukamp</div>", unsafe_allow_html=True)

