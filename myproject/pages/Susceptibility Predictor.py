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
st.title("🌍 Earthquake Susceptibility Predictor")

MODELS_DIR = r"myproject/models"

@st.cache_resource
def load_resources():
    model_path = os.path.join(MODELS_DIR, "EarthquakePredictor.pkl")
    scaler_fd_path = os.path.join(MODELS_DIR, "fault_density_scaler.pkl")
    scaler_hd_path = os.path.join(MODELS_DIR, "hubdist_scaler.pkl")
    scaler_mag_path = os.path.join(MODELS_DIR, "mag_scaler.pkl")
    data_path = os.path.join(MODELS_DIR, "EarthquakeFeatures.csv")

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
        lat_col = next((c for c in df.columns if c.lower().startswith("lat")), None)
        lon_col = next((c for c in df.columns if c.lower().startswith("lon") or "long" in c.lower()), None)
        fault_col = next((c for c in df.columns if "hubname" in c.lower()), None)
        mag_col = next((c for c in df.columns if c.lower().startswith("mag")), None)

        df["distance"] = df.apply(
            lambda r: geodesic((lat, lon), (r[lat_col], r[lon_col])).meters,
            axis=1
        )
        top3 = df.nsmallest(3, "distance")
        nearest = top3.iloc[0]
        hub_dist = nearest["distance"]

        fault_name = None
        if fault_col:
            named = top3[top3[fault_col].notna()]
            if not named.empty:
                fault_name = named.iloc[0][fault_col]
                subset = df[df[fault_col] == fault_name]
            else:
                subset = pd.DataFrame([nearest])
        else:
            subset = pd.DataFrame([nearest])

        mag = subset[mag_col].nlargest(4).mean() if mag_col and not subset.empty else 0.0
        fault_density = subset["FaultDensity"].mean() if "FaultDensity" in subset.columns else np.nan

        # -- Normalize --
        fd_norm = 0.0 if pd.isna(fault_density) else float(scaler_fd.transform([[fault_density]])[0][0])
        hd_norm = float(scaler_hd.transform([[hub_dist]])[0][0])
        mag_norm = float(scaler_mag.transform([[mag]])[0][0])

        # -- Terrain risk: landslide-prone check --
        landslide_keywords = [
            "Joshimath", "Badrinath", "Kedarnath", "Chamoli", "Rudraprayag", "Pithoragarh", "Almora",
            "Nainital", "Manali", "Kullu", "Chamba", "Dharamshala", "Kangra", "Darjeeling", "Dehradun",
            "Mussoorie", "Rishikesh", "Haridwar", "Tawang", "Ziro", "Nilgiris", "Wayanad", "Munnar"
        ]
        terrain_penalty = int(any(k.lower() in place.lower() or (fault_name and k.lower() in fault_name.lower()) for k in landslide_keywords))

        # -- Model input & prediction --
        X = pd.DataFrame([{
            "mag": mag,
            "HubDist": hub_dist,
            "fault_density_norm": fd_norm,
            "has_fault_density": int(not pd.isna(fault_density) and fault_density > 0.05),
            "terrain_penalty": terrain_penalty
        }], columns=["mag", "HubDist", "fault_density_norm", "has_fault_density", "terrain_penalty"])

        pred = model.predict(X)[0]
        label = "✅ Safe" if pred == 0 else ("⚠️ Moderate" if pred == 1 else "❌ Unsafe")
        
        # -- Risk score & user-facing rating (0–5) --
        risk_score = 0.35 * mag_norm + 0.35 * fd_norm + 0.2 * (1 - hd_norm) + 0.1 * terrain_penalty
        risk_score = min(1.0, risk_score)
        rating = round(5.0 * (1 - risk_score), 2)

        # -- Plot map --
        entered_color = 'green' if rating >= 2.5 else ('orange' if rating >= 1.25 else 'red')
        map_data = [
            {"name": place, "latitude": lat, "longitude": lon, "type": "Entered Location",
             "color": entered_color, "hover": f"{place}: Rating {rating}/5"},
            {"name": fault_name or "Fault Hub", "latitude": nearest[lat_col], "longitude": nearest[lon_col],
             "type": "Fault Hub", "color": "cyan", "hover": f"{fault_name or 'Hub'}"}
        ]
        mdf = pd.DataFrame(map_data)
        fig = px.scatter_mapbox(
            mdf, lat="latitude", lon="longitude",
            color="type", hover_name="name", zoom=5, height=450,
            color_discrete_map={"Entered Location": entered_color, "Fault Hub": "cyan"}
        )
        fig.update_layout(mapbox_style="open-street-map", margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)

        # -- Display metrics --
        st.metric("Distance to Nearest Fault Hub", f"{hub_dist:.0f} m")
        st.metric("Fault Density", f"{fault_density:.4f}")
        st.metric("Estimated Magnitude", f"{mag:.2f}")
        st.metric("Safety Rating (0–5)", f"{rating}")
        st.subheader("Prediction:")
        st.markdown(f"{label}")

        # -- Show related earthquakes --
        if fault_name:
            st.markdown(f"### Earthquakes on Fault: {fault_name}")
            rq = df[df[fault_col] == fault_name].copy()
            if "time" in rq.columns:
                rq = rq.sort_values("time", ascending=False)
            elif mag_col:
                rq = rq.sort_values(mag_col, ascending=False)
            st.dataframe(rq[[lat_col, lon_col, mag_col] + (["time"] if "time" in rq.columns else [])].head(5))
