import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import plotly.express as px

# -----------------------------
# Setup
# -----------------------------
st.set_page_config(page_title="Earthquake Susceptibility Predictor", layout="centered")
st.title("🌍 Earthquake Susceptibility Predictor")
st.write("Enter a place name to see its safety rating (0–5) and classification as **Safe**, **Moderate**, or **Unsafe** based on fault density, magnitude, and distance.")

# Centralized model and data paths
MODELS_DIR = r"C:\Users\Supravo Biswas\Desktop\Coding\Python Coding\StreamlitPython\Susceptability_pred_ML\Susceptability_pred_ML"

# -----------------------------
# Custom CSS
# -----------------------------
st.markdown("""
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
    @keyframes smoothGradient {
        0% { background-position: 0% 50%; }
        25% { background-position: 50% 0%; }
        50% { background-position: 100% 50%; }
        75% { background-position: 50% 100%; }
        100% { background-position: 0% 50%; }
    }
    .glass-container {
        background: rgba(255, 255, 255, 0.12);
        backdrop-filter: blur(15px);
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
        border: 1px solid rgba(255, 255, 255, 0.18);
    }
    .title {
        font-size: 3.5em;
        font-weight: 700;
        color: #ffffff;
        text-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
        animation: fadeIn 1.8s ease-out;
    }
    .subtitle {
        font-size: 1.3em;
        color: #e0e0e0;
        margin-bottom: 1.5rem;
        animation: fadeIn 2s ease-out;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    section[data-testid="stSidebar"] {
        background: linear-gradient(-45deg, #1b4332, #2d6a4f, #40916c, #52b788, #1f4e79, #2563eb);
        background-size: 400% 400%;
        animation: smoothGradient 25s ease infinite;
        color: #f8f8f8;
        font-family: 'Roboto', sans-serif;
        border-right: 1px solid rgba(255, 255, 255, 0.15);
        padding: 1rem;
    }
    section[data-testid="stSidebar"] * {
        color: #f8f8f8 !important;
    }
    section[data-testid="stSidebar"] input,
    section[data-testid="stSidebar"] textarea,
    section[data-testid="stSidebar"] select {
        background-color: rgba(255, 255, 255, 0.1);
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 8px;
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
    .st-lottie-container {
        background-color: transparent !important;
        box-shadow: none !important;
    }
    /* Earth-inspired earthquake theme styling */
    .stMetric {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 10px;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    .stAlert {
        background: rgba(255, 255, 255, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.3);
        color: #f8f8f8;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Load resources
# -----------------------------
@st.cache_resource
def load_resources():
    """Load ML models and data with robust error handling."""
    try:
        # Define file paths
        model_path = os.path.join(MODELS_DIR, "EarthquakePredictor.pkl")
        scaler_fd_path = os.path.join(MODELS_DIR, "fault_density_scaler.pkl")
        scaler_hd_path = os.path.join(MODELS_DIR, "hubdist_scaler.pkl")
        scaler_mag_path = os.path.join(MODELS_DIR, "mag_scaler.pkl")
        data_path = os.path.join(MODELS_DIR, "EarthquakeFeatures.csv")

        # Check if files exist
        missing_files = []
        file_paths = [
            (model_path, "EarthquakePredictor.pkl"),
            (scaler_fd_path, "fault_density_scaler.pkl"),
            (scaler_hd_path, "hubdist_scaler.pkl"),
            (scaler_mag_path, "mag_scaler.pkl"),
            (data_path, "EarthquakeFeatures.csv")
        ]
        
        for path, name in file_paths:
            if not os.path.exists(path):
                missing_files.append(name)
        
        if missing_files:
            st.error(f"❌ Missing required files: {', '.join(missing_files)}")
            st.error(f"Please ensure all files are in: {MODELS_DIR}")
            st.stop()
        
        # Load models and data
        model_with_features = joblib.load(model_path)
        model, expected_columns = model_with_features  # Unpack model and expected column order
        scaler_fd = joblib.load(scaler_fd_path)
        scaler_hd = joblib.load(scaler_hd_path)
        scaler_mag = joblib.load(scaler_mag_path)
        df = pd.read_csv(data_path)
        
        return model, expected_columns, scaler_fd, scaler_hd, scaler_mag, df
        
    except Exception as e:
        st.error(f"❌ Error loading resources: {str(e)}")
        st.error("Please check file paths and ensure all required files are available.")
        st.stop()

# Define landslide-prone keywords
landslide_prone_keywords = [
    "Joshimath", "Badrinath", "Kedarnath", "Chamoli", "Rudraprayag", "Pithoragarh", "Almora", "Nainital",
    "Manali", "Kullu", "Chamba", "Dharamshala", "Kangra",
    "Gangtok", "Darjeeling", "Dehradun", "Mussoorie", "Rishikesh", "Haridwar", "Tehri"
]

# Load resources with error handling
try:
    model, expected_columns, scaler_fd, scaler_hd, scaler_mag, df = load_resources()
except:
    st.error("Failed to load required models and data. Please check the setup.")
    st.stop()

# -----------------------------
# Input location
# -----------------------------
place = st.text_input("📍 Enter Place Name (e.g., Delhi, Guwahati):")

if place:
    geolocator = Nominatim(user_agent="streamlit_eq_predictor")

    try:
        location = geolocator.geocode(place, timeout=10)
    except GeocoderTimedOut:
        st.error("⏱️ Geocoding service timed out. Please try again.")
        location = None

    if location is None:
        st.error("❌ Place not found. Please enter a valid location.")
    else:
        lat, lon = location.latitude, location.longitude
        st.success(f"✅ **{place}** found at coordinates: ({lat:.4f}, {lon:.4f})")

        # -----------------------------
        # Data processing
        # -----------------------------
        if not df.empty:
            # Find nearest point
            distances = np.sqrt((df['LAT'] - lat)**2 + (df['LONG_'] - lon)**2)
            nearest_idx = distances.idxmin()
            nearest_point = df.iloc[nearest_idx]
            
            # Extract features
            mag = nearest_point.get('MAGMB', 3.0)
            hub_dist = nearest_point.get('HubDist', 50.0)
            fault_density = nearest_point.get('FaultDensity', 0.0)
            fault_name = nearest_point.get('HubName', 'Unknown')
            
            # Handle NaN values
            if pd.isna(mag):
                mag = 3.0
            if pd.isna(hub_dist):
                hub_dist = 50.0
            if pd.isna(fault_density):
                fault_density = 0.0
            
            # Scale features
            fault_density_norm = scaler_fd.transform([[fault_density]])[0][0]
            hub_dist_norm = scaler_hd.transform([[hub_dist]])[0][0]
            mag_norm = scaler_mag.transform([[mag]])[0][0]
            
            # Check for terrain risk
            terrain_risky = any(
                keyword.lower() in place.lower()
                for keyword in landslide_prone_keywords
            )
            has_fault_density = 0 if pd.isna(fault_density) or fault_density < 0.05 else 1
            terrain_penalty = 1 if terrain_risky else 0

            X_input = pd.DataFrame([{
                'mag': mag,
                'HubDist': hub_dist,
                'fault_density_norm': fault_density_norm,
                'has_fault_density': has_fault_density,
                'terrain_penalty': terrain_penalty
            }])

            prediction = model.predict(X_input)[0]
            label = "❌ **Unsafe**" if prediction == 2 else ("⚠️ **Moderate**" if prediction == 1 else "✅ **Safe**")

            # -----------------------------
            # Compute risk-based safety rating
            # -----------------------------
            risk = (
                0.4 * (mag / 10.0) +
                0.3 * (1 - min(hub_dist / 100.0, 1)) +
                0.2 * min(fault_density * 10, 1) +
                0.1 * terrain_penalty
            )
            rating = min(risk * 5, 5.0)

            # -----------------------------
            # Display results
            # -----------------------------
            st.markdown("---")
            st.subheader("📊 **Earthquake Susceptibility Analysis**")
            
            # Create map
            fig = px.scatter_mapbox(
                lat=[lat], lon=[lon], 
                color_discrete_sequence=["red"], 
                size=[10], 
                hover_name=[place],
                zoom=8, height=400
            )
            fig.update_layout(mapbox_style="open-street-map")
            fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("---")
            st.metric("📏 Distance from Fault Hub", f"{hub_dist:.2f} m")
            st.metric("🔥 Fault Density", f"{fault_density:.4f}")
            st.metric("📊 Estimated Magnitude", f"{mag:.2f}")
            st.metric("💡 Safety Rating", f"{rating:.1f}/5.0")
            st.subheader("🧠 Model Prediction:")
            st.markdown(label)

            # -----------------------------
            # Earthquakes from same fault
            # -----------------------------
            fault_name_col = 'HubName'
            if fault_name and fault_name_col:
                st.markdown("### 🗒️ Earthquakes on Same Fault")
                st.markdown(f"**Nearest Fault Name:** `{fault_name}`")

                related_quakes = df[df[fault_name_col] == fault_name]

                if related_quakes.empty:
                    st.info("No related earthquakes found on this fault.")
                else:
                    st.write(f"Found **{len(related_quakes)}** earthquakes on the same fault:")
                    
                    # Display summary statistics
                    avg_mag = related_quakes['MAGMB'].mean()
                    max_mag = related_quakes['MAGMB'].max()
                    min_mag = related_quakes['MAGMB'].min()
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Average Magnitude", f"{avg_mag:.2f}")
                    with col2:
                        st.metric("Maximum Magnitude", f"{max_mag:.2f}")
                    with col3:
                        st.metric("Minimum Magnitude", f"{min_mag:.2f}")
                    
                    # Show recent earthquakes
                    st.subheader("Recent Earthquakes on Same Fault")
                    display_cols = ['YR', 'MO', 'DT', 'LAT', 'LONG_', 'MAGMB', 'DEPTH_KM']
                    available_cols = [col for col in display_cols if col in related_quakes.columns]
                    
                    if available_cols:
                        st.dataframe(related_quakes[available_cols].head(10))

        else:
            st.error("❌ No earthquake data available for analysis.")

# -----------------------------
# Footer
# -----------------------------
st.markdown("""
<div class="footer">
    <p>🌍 Bhukamp - Earthquake Susceptibility Predictor | Built with ❤️ for safer communities</p>
</div>
""", unsafe_allow_html=True)
