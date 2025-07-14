import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import plotly.express as px

# ---- Setup ----
st.set_page_config(page_title="Earthquake Susceptibility Predictor", layout="centered")

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

st.title("🌍 Earthquake Susceptibility Predictor")

# Use current directory for models
MODELS_DIR = "."

@st.cache_resource
def load_resources():
    model_path = os.path.join(MODELS_DIR, "Susceptability_pred_ML/EarthquakePredictor.pkl")
    scaler_fd_path = os.path.join(MODELS_DIR, "Susceptability_pred_ML/fault_density_scaler.pkl")
    scaler_hd_path = os.path.join(MODELS_DIR, "Susceptability_pred_ML/hubdist_scaler.pkl")
    scaler_mag_path = os.path.join(MODELS_DIR, "Susceptability_pred_ML/mag_scaler.pkl")
    data_path = os.path.join(MODELS_DIR, "Susceptability_pred_ML/EarthquakeFeatures.csv")

    for path, name in [
        (model_path, "EarthquakePredictor.pkl"),
        (scaler_fd_path, "fault_density_scaler.pkl"),
        (scaler_hd_path, "hubdist_scaler.pkl"),
        (scaler_mag_path, "mag_scaler.pkl"),
        (data_path, "EarthquakeFeatures.csv"),
    ]:
        if not os.path.exists(path):
            st.error(f"Missing file: {name}")
            st.stop()

    model_with_cols = joblib.load(model_path)
    model, expected_columns = model_with_cols
    scaler_fd = joblib.load(scaler_fd_path)
    scaler_hd = joblib.load(scaler_hd_path)
    scaler_mag = joblib.load(scaler_mag_path)
    df = pd.read_csv(data_path)
    return model, expected_columns, scaler_fd, scaler_hd, scaler_mag, df

try:
    model, expected_columns, scaler_fd, scaler_hd, scaler_mag, df = load_resources()
except Exception as e:
    st.error(f"Error loading resources: {e}")
    st.stop()

place = st.text_input("📍 Enter Place Name (e.g., Delhi, Guwahati):")

if place:
    geolocator = Nominatim(user_agent="earthquake_predictor_v1")
    try:
        loc = geolocator.geocode(place, timeout=10)
    except Exception:
        st.error("Geocode timeout. Please try again.")
        loc = None

    if not loc:
        st.error("Place not found.")
    else:
        lat, lon = loc.latitude, loc.longitude
        st.success(f"📌 Found: {loc.address}")
        st.write(f"📍 Coordinates: {lat:.4f}, {lon:.4f}")

        # -- Distance to nearest faults --
        lat_col = "LAT"  # Based on CSV structure
        lon_col = "LONG_"  # Based on CSV structure
        fault_col = "HubName"  # Based on CSV structure
        mag_col = "MAGMB"  # Based on CSV structure

        # Calculate distance to all earthquake points
        df["distance"] = df.apply(
            lambda r: geodesic((lat, lon), (r[lat_col], r[lon_col])).meters
            if pd.notna(r[lat_col]) and pd.notna(r[lon_col]) else float('inf'),
            axis=1
        )
        
        # Get top 3 nearest points
        top3 = df.nsmallest(3, "distance")
        nearest = top3.iloc[0]
        hub_dist = nearest["distance"]

        # Find fault information
        fault_name = None
        if fault_col and pd.notna(nearest[fault_col]):
            fault_name = nearest[fault_col]
            subset = df[df[fault_col] == fault_name]
        else:
            # Use nearest points if no fault name
            subset = top3

        # Calculate magnitude (average of top earthquakes in the area)
        if mag_col in subset.columns:
            valid_mags = subset[mag_col].dropna()
            mag = valid_mags.nlargest(4).mean() if not valid_mags.empty else 0.0
        else:
            mag = 0.0

        # Calculate fault density
        fault_density = subset["FaultDensity"].mean() if "FaultDensity" in subset.columns else np.nan

        # -- Normalize using the saved scalers --
        # Handle fault density normalization
        if pd.isna(fault_density):
            fd_norm = 0.0
        else:
            fd_norm = float(scaler_fd.transform([[fault_density]])[0][0])
        
        hd_norm = float(scaler_hd.transform([[hub_dist]])[0][0])
        mag_norm = float(scaler_mag.transform([[mag]])[0][0])

        # -- Terrain risk: landslide-prone check --
        landslide_keywords = [
            "Joshimath", "Badrinath", "Kedarnath", "Chamoli", "Rudraprayag", "Pithoragarh", "Almora",
            "Nainital", "Manali", "Kullu", "Chamba", "Dharamshala", "Kangra", "Darjeeling", "Dehradun",
            "Mussoorie", "Rishikesh", "Haridwar", "Tawang", "Ziro", "Nilgiris", "Wayanad", "Munnar",
            "Baramulla", "Pahalgam", "Uri", "Banihal", "Ramban", "Gangtok", "Mangan", "Chungthang", 
            "Shillong", "Cherrapunji", "East Khasi Hills", "Kohima", "Wokha", "Itanagar", "Dima Hasao", 
            "Karbi Anglong", "Idukki", "Pathanamthitta", "Kottayam", "Ernakulam", "Kodagu", "Coorg", 
            "Chikmagalur", "Uttara Kannada", "Ooty", "Coonoor", "Tehri"
        ]
        
        terrain_penalty = int(any(k.lower() in place.lower() or 
                                (fault_name and k.lower() in str(fault_name).lower()) 
                                for k in landslide_keywords))

        # -- Model input & prediction --
        X = pd.DataFrame([{
            "mag": mag,
            "HubDist": hub_dist,
            "fault_density_norm": fd_norm,
            "has_fault_density": int(not pd.isna(fault_density) and fault_density > 0.05),
            "terrain_penalty": terrain_penalty
        }], columns=expected_columns)

        pred = model.predict(X)[0]
        label_map = {0: "✅ Safe", 1: "⚠️ Moderate", 2: "❌ Unsafe"}
        label = label_map.get(pred, "Unknown")

        # -- Realistic Risk score & user-facing rating (0–5) aligned with model predictions --
        # Create realistic ratings based on actual risk factors
        # Unsafe: 0-1.49, Moderate: 1.5-2.99, Safe: 3.0-5.0
        
        # Base rating based on prediction class
        base_ratings = {0: 4.0, 1: 2.2, 2: 1.0}  # Safe, Moderate, Unsafe
        base_rating = base_ratings[pred]
        
        # Adjust based on actual risk factors for realism
        distance_factor = min(1.0, hub_dist / 100000)  # Normalize distance (100km = 1.0)
        mag_factor = min(1.0, mag / 6.0)  # Normalize magnitude (6.0 = 1.0)
        
        # Calculate realistic adjustments within specified ranges
        if pred == 0:  # Safe areas: 3.0-5.0
            distance_bonus = 1.0 * distance_factor  # More distance = safer
            mag_penalty = -0.5 * mag_factor  # Higher mag = less safe
            terrain_penalty_val = -0.3 if terrain_penalty else 0
            rating = base_rating + distance_bonus + mag_penalty + terrain_penalty_val
            rating = max(3.0, min(5.0, rating))  # Clamp to 3.0-5.0 range
            
        elif pred == 1:  # Moderate areas: 1.5-2.99
            distance_bonus = 0.4 * distance_factor
            mag_penalty = -0.3 * mag_factor
            terrain_penalty_val = -0.2 if terrain_penalty else 0
            rating = base_rating + distance_bonus + mag_penalty + terrain_penalty_val
            rating = max(1.5, min(2.99, rating))  # Clamp to 1.5-2.99 range
            
        else:  # Unsafe areas: 0.0-1.49
            distance_bonus = 0.3 * distance_factor  # Even unsafe areas can vary
            mag_penalty = -0.2 * mag_factor
            terrain_penalty_val = -0.1 if terrain_penalty else 0
            rating = base_rating + distance_bonus + mag_penalty + terrain_penalty_val
            rating = max(0.0, min(1.49, rating))  # Clamp to 0.0-1.49 range
        
        rating = round(rating, 1)

        # Display confidence and risk factors
        if hasattr(model, "predict_proba"):
            probs = model.predict_proba(X)[0]
            st.write(f"**Confidence** – Safe: {probs[0]:.1%}, Moderate: {probs[1]:.1%}, Unsafe: {probs[2]:.1%}")
        
        # Show risk factors for transparency
        st.write(f"**Risk Factors** – Distance: {hub_dist/1000:.1f}km, Magnitude: {mag:.1f}, Terrain Risk: {'Yes' if terrain_penalty else 'No'}")

        # -- Plot map --
        # Color based on prediction class for consistency
        color_map = {0: 'green', 1: 'orange', 2: 'red'}
        entered_color = color_map.get(pred, 'gray')
        map_data = [
            {"name": place, "latitude": lat, "longitude": lon, "type": "Entered Location",
             "color": entered_color, "hover": f"{place}: Rating {rating}/5"},
            {"name": fault_name or "Nearest Point", "latitude": nearest[lat_col], "longitude": nearest[lon_col],
             "type": "Nearest Earthquake Point", "color": "cyan", "hover": f"{fault_name or 'Nearest Point'}"}
        ]
        mdf = pd.DataFrame(map_data)
        
        fig = px.scatter_mapbox(
            mdf, lat="latitude", lon="longitude",
            color="type", hover_name="name", zoom=6, height=450,
            color_discrete_map={"Entered Location": entered_color, "Nearest Earthquake Point": "cyan"}
        )
        fig.update_layout(mapbox_style="open-street-map", margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)

        # -- Display metrics --
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Distance to Nearest Point", f"{hub_dist:.0f} m")
            st.metric("Estimated Magnitude", f"{mag:.2f}")
        with col2:
            st.metric("Fault Density", f"{fault_density:.4f}" if not pd.isna(fault_density) else "N/A")
            st.metric("Safety Rating (0–5)", f"{rating}")
        
        st.subheader("🔮 Prediction:")
        st.markdown(f"## {label}")

        # -- Show related earthquakes --
        if fault_name:
            st.markdown(f"### 🗺️ Earthquakes related to: {fault_name}")
            related_eq = df[df[fault_col] == fault_name].copy()
        else:
            st.markdown(f"### 🗺️ Nearest Earthquakes")
            related_eq = top3.copy()
        
        if not related_eq.empty:
            # Sort by magnitude if available
            if mag_col in related_eq.columns:
                related_eq = related_eq.sort_values(mag_col, ascending=False)
            
            # Display relevant columns
            display_cols = [lat_col, lon_col, mag_col]
            if "YR" in related_eq.columns:
                display_cols.append("YR")
            if "DEPTH_KM" in related_eq.columns:
                display_cols.append("DEPTH_KM")
            
            st.dataframe(related_eq[display_cols].head(5), use_container_width=True)

        # -- Additional Information --
        st.markdown("---")
        st.markdown("### ℹ️ About the Prediction")
        st.write(f"""
        - **Location**: {place}
        - **Coordinates**: {lat:.4f}°, {lon:.4f}°
        - **Nearest earthquake distance**: {hub_dist/1000:.1f} km
        - **Terrain risk**: {'Yes' if terrain_penalty else 'No'} (landslide-prone area)
        - **Model features used**: Magnitude, Distance, Fault Density, Terrain Risk
        
        **Rating Scale** (Realistic Risk Assessment):
        - **3.0-5.0**: ✅ Safe (Low earthquake risk - distant from major fault lines)
        - **1.5-2.99**: ⚠️ Moderate (Medium earthquake risk - some seismic activity expected)  
        - **0.0-1.49**: ❌ Unsafe (High earthquake risk - near active fault zones)
        """)
        
        # Risk explanation with rating context
        if pred == 0:
            st.success(f"This area appears to be relatively safe from earthquake hazards (Rating: {rating}/5). Based on historical data, the risk is low.")
        elif pred == 1:
            st.warning(f"This area has moderate earthquake risk (Rating: {rating}/5). Stay prepared and follow safety guidelines.")
        else:
            st.error(f"This area has high earthquake risk (Rating: {rating}/5). Take necessary precautions and emergency preparedness measures.")

