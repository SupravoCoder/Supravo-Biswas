mport streamlit as st
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
MODELS_DIR = r"C:\Users\Supravo Biswas\Desktop\Coding\Python Coding\StreamlitPython\Susceptability_pred_ML\Susceptability_pred_ML\models"

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
        model_path = os.path.join(MODELS_DIR, "C:\\Users\\Supravo Biswas\\Desktop\\Coding\\Python Coding\\StreamlitPython\\Susceptability_pred_ML\\Susceptability_pred_ML\\EarthquakePredictor.pkl")
        scaler_fd_path = os.path.join(MODELS_DIR, "C:\\Users\\Supravo Biswas\\Desktop\\Coding\\Python Coding\\StreamlitPython\\Susceptability_pred_ML\\Susceptability_pred_ML\\fault_density_scaler.pkl")
        scaler_hd_path = os.path.join(MODELS_DIR, "C:\\Users\\Supravo Biswas\\Desktop\\Coding\\Python Coding\\StreamlitPython\\Susceptability_pred_ML\\Susceptability_pred_ML\\hubdist_scaler.pkl")
        scaler_mag_path = os.path.join(MODELS_DIR, "C:\\Users\\Supravo Biswas\\Desktop\\Coding\\Python Coding\\StreamlitPython\\Susceptability_pred_ML\\Susceptability_pred_ML\\mag_scaler.pkl")
        data_path = os.path.join(MODELS_DIR, "C:\\Users\\Supravo Biswas\\Desktop\\Coding\\Python Coding\\StreamlitPython\\Susceptability_pred_ML\\Susceptability_pred_ML\\EarthquakeFeatures.csv")

        # Check if files exist
        missing_files = []
        for path, name in [(model_path, "C:\\Users\\Supravo Biswas\\Desktop\\Coding\\Python Coding\\StreamlitPython\\Susceptability_pred_ML\\Susceptability_pred_ML\\EarthquakePredictor.pkl"), 
                          (scaler_fd_path, "C:\\Users\\Supravo Biswas\\Desktop\\Coding\\Python Coding\\StreamlitPython\\Susceptability_pred_ML\\Susceptability_pred_ML\\fault_density_scaler.pkl"),
                          (scaler_hd_path, "C:\\Users\\Supravo Biswas\\Desktop\\Coding\\Python Coding\\StreamlitPython\\Susceptability_pred_ML\\Susceptability_pred_ML\\hubdist_scaler.pkl"),
                          (scaler_mag_path, "C:\\Users\\Supravo Biswas\\Desktop\\Coding\\Python Coding\\StreamlitPython\\Susceptability_pred_ML\\Susceptability_pred_ML\\mag_scaler.pkl"),
                          (data_path, "C:\\Users\\Supravo Biswas\\Desktop\\Coding\\Python Coding\\StreamlitPython\\Susceptability_pred_ML\\Susceptability_pred_ML\\EarthquakeFeatures.csv")]:
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
        st.success(f"📌 Found: {location.address}")
        st.write(f"🛍 Coordinates: `{lat:.4f}, {lon:.4f}`")

        landslide_prone_keywords = [
        "Joshimath", "Badrinath", "Kedarnath", "Chamoli", "Rudraprayag", "Pithoragarh", "Almora", "Nainital",
        "Manali", "Kullu", "Chamba", "Dharamshala", "Kangra",
        "Baramulla", "Pahalgam", "Uri", "Banihal", "Ramban",
        "Gangtok", "Mangan", "Chungthang", "Cherrapunji", "East Khasi Hills",
        "Kohima", "Wokha", "Itanagar", "Tawang", "Ziro",
        "Dima Hasao", "Karbi Anglong",
        "Idukki", "Wayanad", "Munnar", "Pathanamthitta", "Kottayam", "Ernakulam",
        "Kodagu", "Coorg", "Chikmagalur", "Uttara Kannada",
        "Nilgiris", "Ooty", "Coonoor",
        "Darjeeling"," Dehradun"," Mussoorie", "Rishikesh", "Haridwar", "Tehri"
        ]

        # -----------------------------
        # Match top 3 nearest faults
        # -----------------------------
        lat_col = next((col for col in df.columns if col.lower().startswith('lat')), None)
        lon_col = next((col for col in df.columns if col.lower().startswith('lon') or 'long' in col.lower()), None)
        fault_name_col = next((col for col in df.columns if 'hubname' in col.lower()), None)
        mag_col = next((col for col in df.columns if col.lower().startswith('mag')), None)

        if not lat_col or not lon_col:
            st.error("❌ Could not find latitude/longitude columns in the dataset.")
        else:
            df['distance_to_input'] = np.sqrt((df[lat_col] - lat)**2 + (df[lon_col] - lon)**2)
            top3 = df.nsmallest(3, 'distance_to_input')
            nearest = top3.iloc[0]  # use distance from nearest
            hub_dist = nearest['HubDist']

            # pick first fault with name
            fault_name = None
            if fault_name_col:
                named_faults = top3[top3[fault_name_col].notna()]
                if not named_faults.empty:
                    valid_fault_row = named_faults.iloc[0]
                    fault_name = valid_fault_row[fault_name_col]
                else:
                    valid_fault_row = top3.iloc[0]  # fallback to nearest even if no name
                    fault_name = valid_fault_row.get(fault_name_col) if fault_name_col else None
            else:
                valid_fault_row = top3.iloc[0]
                fault_name = None

            # extract magnitude and fault density from chosen fault
            if fault_name and fault_name_col:
                fault_quakes = df[df[fault_name_col] == fault_name]
                mag = fault_quakes[mag_col].nlargest(4).mean() if not fault_quakes.empty and mag_col else 0.0
                fault_density = fault_quakes['FaultDensity'].mean() if not fault_quakes.empty and 'FaultDensity' in fault_quakes.columns else np.nan
            else:
                mag, fault_density = 0.0, np.nan

            # -----------------------------
            # Normalize features and predict
            # -----------------------------
            fault_density_norm = 0.0 if pd.isna(fault_density) else scaler_fd.transform([[fault_density]])[0][0]
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
                0.3 * (1 - hub_dist_norm) +
                0.3 * fault_density_norm +
                0.4 * mag_norm
            )

            if pd.isna(fault_density) or fault_density <= 0.05:
                if hub_dist <= 50000 or mag >= 5.5:
                    risk += 0.4
            if hub_dist <= 100000 or mag >= 4.0:
                    risk += 0.2
            if mag >= 3.5 or hub_dist <= 150000:
                    risk += 0.1

            # -------------------------------
            # Terrain-based landslide penalty
            # -------------------------------

            # Check if input place or hub name matches landslide-prone keywords
            place_lower = place.lower()
            hub_name = ""
            if fault_name_col and valid_fault_row is not None:
                hub_name = valid_fault_row.get(fault_name_col, "") or ""
            hub_name_lower = str(hub_name).lower()

            terrain_risky = any(keyword.lower() in place_lower or keyword.lower() in hub_name_lower
                    for keyword in landslide_prone_keywords)

            if terrain_risky:
                risk += 0.15
                
            rating = round(max(0.0, min(5.0, 5.0 - 5.0 * risk)), 2)

            # -----------------------------
            # Output
            # -----------------------------
            # -----------------------------
            # Map Visualization with Plotly
            # -----------------------------
            st.subheader("🗺️ Map: Entered Location & Nearest Fault Hub")
            entered_color = 'green' if rating >= 2.5 else ('orange' if rating >= 1.25 else 'red')
            
            # Create map data with error handling
            map_data = [{
                'name': place,
                'latitude': lat,
                'longitude': lon,
                'type': '📍 Entered Location',
                'rating': f"{rating}/5.0",
                'color': entered_color,
                'hover': f"📍 {place}<br>Rating: {rating}/5.0"
            }]
            
            # Add fault hub if data is available
            if valid_fault_row is not None and lat_col and lon_col:
                try:
                    fault_lat = valid_fault_row[lat_col]
                    fault_lon = valid_fault_row[lon_col]
                    map_data.append({
                        'name': fault_name if fault_name else "Unknown Fault",
                        'latitude': fault_lat,
                        'longitude': fault_lon,
                        'type': '🌋 Fault Hub',
                        'color': 'gray',
                        'hover': f"🌋 {fault_name if fault_name else 'Unknown Fault'}"
                    })
                except (KeyError, IndexError):
                    st.warning("⚠️ Could not display fault hub location on map.")
            
            map_df = pd.DataFrame(map_data)

            fig = px.scatter_mapbox(
            map_df,
            lat="latitude",
            lon="longitude",
            color="type",
            hover_name="name",
            zoom=5,
            height=500,
            color_discrete_map={
                '📍 Entered Location': entered_color,
                '🌋 Fault Hub': 'cyan' 
            }
        )

            fig.update_layout(mapbox_style="open-street-map")
            fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("---")
            st.metric("📏 Distance from Fault Hub", f"{hub_dist:.2f} m")
            st.metric("🔥 Fault Density", f"{fault_density:.4f}")
            st.metric("📊 Estimated Magnitude", f"{mag:.2f}")
            st.metric("💡 Safety Rating", f"{rating}/5.0")
            st.subheader("🧠 Model Prediction:")
            st.markdown(label)

            # -----------------------------
            # Earthquakes from same fault
            # -----------------------------
            if fault_name and fault_name_col:
                st.markdown("### 🗒️ Earthquakes on Same Fault")
                st.markdown(f"**Nearest Fault Name:** `{fault_name}`")

                related_quakes = df[df[fault_name_col] == fault_name]

                if related_quakes.empty:
                    st.info("No recorded earthquakes found for this fault.")
                else:
                    if 'time' in related_quakes.columns:
                        related_quakes = related_quakes.sort_values('time', ascending=False)
                    elif mag_col:
                        related_quakes = related_quakes.sort_values(mag_col, ascending=False)

                    cols_to_show = []
                    if lat_col: cols_to_show.append(lat_col)
                    if lon_col: cols_to_show.append(lon_col)
                    if mag_col: cols_to_show.append(mag_col)
                    if 'time' in related_quakes.columns: cols_to_show.append('time')

                    if cols_to_show:
                        st.dataframe(related_quakes[cols_to_show].head(5))
                    else:
                        st.warning("⚠️ No valid columns found to display.")
            else:
                st.warning("⚠️ Fault name not found in this record.")

