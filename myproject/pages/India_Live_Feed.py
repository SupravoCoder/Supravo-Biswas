import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import requests
import datetime
import time
from pathlib import Path
import json
import io
import os

# Page configuration
st.set_page_config(
    page_title="India Earthquake Live Feed",
    page_icon="🔴",
    layout="wide"
)

# Custom CSS styling
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
    margin: 0;
    padding: 0;
}

@keyframes smoothGradient {
    0% { background-position: 0% 50%; }
    25% { background-position: 50% 0%; }
    50% { background-position: 100% 50%; }
    75% { background-position: 50% 100%; }
    100% { background-position: 0% 50%; }
}

.glass-container {
    background: rgba(255, 255, 255, 0.16);
    backdrop-filter: blur(12px);
    border-radius: 15px;
    padding: 1.5rem;
    box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
    border: 1px solid rgba(255, 255, 255, 0.13);
    max-width: 900px;
    margin: 2rem auto;
}

.title {
    font-size: clamp(2.5em, 6vw, 3.5em);
    font-weight: 700;
    color: #fff;
    text-shadow: 0 4px 10px rgba(0,0,0,0.3);
    animation: fadeIn 1.8s ease-out;
    margin-bottom: 0.5em;
}

.subtitle {
    font-size: clamp(1em, 2vw, 1.3em);
    color: #e0e0e0;
    margin-bottom: 1.5rem;
    animation: fadeIn 2s ease-out;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px);}
    to   { opacity: 1; transform: translateY(0);}
}

.alert-box {
    padding: 1rem;
    border-radius: 8px;
    margin: 1rem 0;
    border-left: 4px solid #ff6b6b;
    background: rgba(255, 107, 107, 0.1);
    color: #fff;
}

.alert-high {
    border-left-color: #ff4757;
    background: rgba(255, 71, 87, 0.15);
}

/* Sidebar improvements */
section[data-testid="stSidebar"] {
    background: linear-gradient(-45deg, #1b4332, #2d6a4f, #40916c, #52b788, #1f4e79, #2563eb);
    background-size: 400% 400%;
    animation: smoothGradient 25s ease infinite;
    color: #f8f8f8;
    font-family: 'Roboto', sans-serif;
    border-right: 1px solid rgba(255,255,255,0.12);
    padding: 1rem;
}

section[data-testid="stSidebar"] * {
    color: #f8f8f8 !important;
}

/* Form field enhancements */
section[data-testid="stSidebar"] input,
section[data-testid="stSidebar"] textarea,
section[data-testid="stSidebar"] select {
    background-color: rgba(255,255,255,0.13);
    color: #fff !important;
    border: 1px solid rgba(255,255,255,0.23);
    border-radius: 8px;
    margin-bottom: 0.7em;
}

/* Footer */
.footer {
    text-align: center;
    font-size: 0.90em;
    color: #cccccc;
    margin-top: 2.5rem;
}

/* Plotly legend & map marker visibility */
.js-plotly-plot .legend text,
.js-plotly-plot .legend .legendtitle text {
    fill: #000 !important;
    font-weight: bold !important;
    font-size: 14px !important;
    text-shadow: 1px 1px 2px rgba(255,255,255,0.8) !important;
}

.js-plotly-plot .legend .legendtitle text {
    font-size: 16px !important;
}

.js-plotly-plot .scattermapbox text {
    text-shadow: 2px 2px 4px rgba(0,0,0,0.8) !important;
    font-weight: bold !important;
}

/* Scrollbar styling */
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

html {
    scrollbar-width: thin;
    scrollbar-color: #40916c #2563eb;
}

/* Make images and iframe responsive */
img, iframe {
    max-width: 100%;
    height: auto;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

# Main title
st.markdown('<h1 class="title">🔴 India Earthquake Live Feed</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Real-time monitoring of earthquake activity in India</p>', unsafe_allow_html=True)

# Current time display
current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
st.markdown(f"<p>Current Date and Time (UTC): {current_time}</p>", unsafe_allow_html=True)

# Sidebar for data source selection
st.sidebar.header("Data Source")
data_source = st.sidebar.radio(
    "Select Data Source:",
    ["USGS API", "EMSC API", "Local CSV File", "Upload CSV"]
)

# Function to load data from various sources
@st.cache_data(ttl=300)  # Cache data for 5 minutes
def load_earthquake_data(source, uploaded_file=None):
    """Load earthquake data from various sources with error handling"""
    try:
        if source == "USGS API":
            # USGS API for earthquakes in India region (approximate bounding box)
            url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
            params = {
                "format": "geojson",
                "starttime": (datetime.datetime.now() - datetime.timedelta(days=30)).strftime("%Y-%m-%d"),
                "endtime": datetime.datetime.now().strftime("%Y-%m-%d"),
                "minlatitude": 6.5,
                "maxlatitude": 35.5,
                "minlongitude": 68.0,
                "maxlongitude": 97.5,
                "minmagnitude": 2.5
            }
            
            response = requests.get(url, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                
                # Convert GeoJSON to DataFrame
                earthquakes = []
                for feature in data['features']:
                    props = feature['properties']
                    coords = feature['geometry']['coordinates']
                    
                    # Check if the place contains India or is in the India region
                    place = props.get('place', '').lower()
                    if 'india' in place or any(region in place for region in ['kashmir', 'delhi', 'mumbai', 'kolkata', 'chennai', 'himalayas']):
                        earthquakes.append({
                            'time': datetime.datetime.fromtimestamp(props['time']/1000).strftime('%Y-%m-%d %H:%M:%S'),
                            'place': props['place'],
                            'mag': props['mag'],
                            'depth': coords[2],
                            'latitude': coords[1],
                            'longitude': coords[0],
                            'status': props['status'],
                            'tsunami': props['tsunami'],
                            'felt': props.get('felt', None),
                            'source': 'USGS'
                        })
                
                return pd.DataFrame(earthquakes)
            else:
                st.error(f"API Error: {response.status_code}")
                return pd.DataFrame()
                
        elif source == "EMSC API":
            # European-Mediterranean Seismological Centre API
            url = "https://www.seismicportal.eu/fdsnws/event/1/query"
            params = {
                "format": "json",
                "start": (datetime.datetime.now() - datetime.timedelta(days=30)).strftime("%Y-%m-%d"),
                "end": datetime.datetime.now().strftime("%Y-%m-%d"),
                "minlat": 6.5,
                "maxlat": 35.5,
                "minlon": 68.0,
                "maxlon": 97.5,
                "minmag": 2.5
            }
            
            response = requests.get(url, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                
                # Filter for events in India
                earthquakes = []
                for event in data['features']:
                    props = event['properties']
                    coords = event['geometry']['coordinates']
                    
                    # Filter for India region
                    place = props.get('flynn_region', '').lower()
                    if 'india' in place or any(region in place for region in ['kashmir', 'delhi', 'mumbai', 'kolkata', 'chennai', 'himalayas']):
                        earthquakes.append({
                            'time': props['time'].replace('T', ' ').split('.')[0],
                            'place': props.get('flynn_region', 'Unknown'),
                            'mag': props['mag'],
                            'depth': coords[2],
                            'latitude': coords[1],
                            'longitude': coords[0],
                            'status': props.get('status', 'unknown'),
                            'tsunami': 0,  # EMSC doesn't provide this directly
                            'felt': props.get('felt', None),
                            'source': 'EMSC'
                        })
                
                return pd.DataFrame(earthquakes)
            else:
                st.error(f"API Error: {response.status_code}")
                return pd.DataFrame()
                
        elif source == "Local CSV File":
            # Try multiple possible locations for earthquake.csv
            possible_paths = [
                Path("data/earthquake.csv"),
                Path("myproject/data/earthquake.csv"),
                Path(__file__).parent.parent / "data" / "earthquake.csv" if __file__ else Path("data/earthquake.csv"),
                Path(__file__).parent.parent / "models" / "earthquake.csv" if __file__ else Path("models/earthquake.csv"),
                Path("../data/earthquake.csv"),
                Path("models/earthquake.csv"),
                Path("earthquake.csv")
            ]
            
            for path in possible_paths:
                if path.exists():
                    df = pd.read_csv(path)
                    # Filter for India data if place column exists
                    if 'place' in df.columns:
                        df = df[df['place'].str.contains('India', case=False, na=False)]
                    # Convert time to datetime if needed
                    if 'time' in df.columns and not pd.api.types.is_datetime64_any_dtype(df['time']):
                        df['time'] = pd.to_datetime(df['time'], errors='coerce')
                        df['time'] = df['time'].dt.strftime('%Y-%m-%d %H:%M:%S')
                    # Add source column
                    df['source'] = 'CSV File'
                    return df
            
            st.error("❌ earthquake.csv not found in any of the expected locations")
            return pd.DataFrame()
            
        elif source == "Upload CSV" and uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            # Filter for India data if needed
            if 'place' in df.columns:
                df = df[df['place'].str.contains('India', case=False, na=False)]
            # Convert time to datetime if needed
            if 'time' in df.columns and not pd.api.types.is_datetime64_any_dtype(df['time']):
                df['time'] = pd.to_datetime(df['time'], errors='coerce')
                df['time'] = df['time'].dt.strftime('%Y-%m-%d %H:%M:%S')
            # Add source column
            df['source'] = 'Uploaded File'
            return df
        
        return pd.DataFrame()  # Return empty DataFrame as fallback
        
    except requests.RequestException as e:
        st.error(f"Network error: {str(e)}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()

# Handle file upload if selected
uploaded_file = None
if data_source == "Upload CSV":
    uploaded_file = st.sidebar.file_uploader("Upload earthquake data CSV", type="csv")
    if uploaded_file is None:
        st.warning("Please upload a CSV file containing earthquake data")

# Load data based on selected source
# (Imports and CSS remain unchanged above this point...)

# Load data based on selected source
with st.spinner("Fetching earthquake data..."):
    df = load_earthquake_data(data_source, uploaded_file)
    df.columns = df.columns.str.strip()  # Clean column headers
    df = standardize_columns(df)

# Display error if no data
if df.empty:
    st.error("No earthquake data available. Please try another data source or upload a CSV file.")

    st.markdown("""
    ### Expected Data Format
    The CSV file should contain these columns:
    - `time`: Date and time of the earthquake
    - `place`: Location description (should contain "India")
    - `mag`: Magnitude of the earthquake
    - `depth`: Depth in kilometers
    - `latitude`: Geographic latitude
    - `longitude`: Geographic longitude

    ### Sample Data:
    ```
    time,latitude,longitude,depth,mag,place
    2022-01-15T12:30:45Z,28.7041,77.1025,10.5,4.2,5km NE of Delhi, India
    2022-02-20T08:15:30Z,19.0760,72.8777,15.2,3.8,3km W of Mumbai, India
    ```
    """)

    st.markdown("""
    ### Suggested Directory Structure
    ```
    myproject/
    ├── data/
    │   └── earthquake.csv  # Place your data file here
    ├── pages/
    │   └── India_Live_Earthquake_Feed.py
    ```
    """)

    st.stop()

# Add refresh button
if st.button("🔄 Refresh Data", key="refresh"):
    st.cache_data.clear()
    st.rerun()

# Display summary metrics
if not df.empty:
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Recent Earthquakes", f"{len(df)}")
        
    with col2:
        if 'mag' in df.columns and not df['mag'].isnull().all():
            st.metric("Average Magnitude", f"{df['mag'].mean():.2f}")
        else:
            st.metric("Average Magnitude", "N/A")

    with col3:
        if 'mag' in df.columns and not df['mag'].isnull().all():
            st.metric("Max Magnitude", f"{df['mag'].max():.2f}")
        else:
            st.metric("Max Magnitude", "N/A")

    with col4:
        time_col = next((col for col in ['time', 'datetime', 'event_time', 'timestamp'] if col in df.columns), None)
        recent_time = df[time_col].max() if time_col else "N/A"
        st.metric("Latest Update", recent_time)

    # Check for significant recent earthquakes
    if 'time' in df.columns:
        df['datetime'] = pd.to_datetime(df['time'], errors='coerce')
        recent_df = df[df['datetime'] > (datetime.datetime.now() - datetime.timedelta(hours=24))]

        if not recent_df.empty:
            significant = recent_df[recent_df['mag'] >= 4.5]
            if not significant.empty:
                st.markdown("""
                <div class="alert-box alert-high">
                    <h3>⚠️ Significant Earthquake Alert</h3>
                    <p>Significant earthquake activity detected in the last 24 hours</p>
                </div>
                """, unsafe_allow_html=True)
                
                for _, quake in significant.iterrows():
                    st.markdown(f"""
                    <div class="glass-container">
                        <h4>M{quake['mag']:.1f} - {quake['place']}</h4>
                        <p>Time: {quake['time']}</p>
                        <p>Depth: {quake['depth']} km</p>
                    </div>
                    <br>
                    """, unsafe_allow_html=True)

    # Tabs for map, charts, and table
    tab1, tab2, tab3 = st.tabs(["🗺️ Map View", "📊 Recent Activity", "📋 Data Table"])

    with tab1:
        st.markdown("### Recent Earthquake Locations")
        required_cols = ['latitude', 'longitude', 'mag']
        missing_cols = [col for col in required_cols if col not in df.columns]

        if missing_cols:
            st.error(f"❌ Required columns missing for map: {missing_cols}")
            st.stop()

        df = df.dropna(subset=required_cols)
        df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
        df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
        df['mag'] = pd.to_numeric(df['mag'], errors='coerce')
        df = df.dropna(subset=required_cols)

        try:
            fig = px.scatter_mapbox(
                df,
                lat='latitude',
                lon='longitude',
                color='mag',
                size='mag',
                size_max=15,
                zoom=4,
                center={"lat": 20.5937, "lon": 78.9629},
                hover_name='place',
                hover_data=['time', 'mag', 'depth'],
                color_continuous_scale='Inferno',
                title="Recent Earthquakes in India"
            )
            fig.update_layout(mapbox_style="carto-darkmatter", margin={"r":0,"t":30,"l":0,"b":0}, height=600)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"⚠️ Map could not be displayed: {e}")

        st.markdown("""
        ### Earthquake Magnitude Scale
        - **< 3.0**: Very Minor - Generally not felt
        - **3.0–3.9**: Minor - Felt by many people
        - **4.0–4.9**: Light - Felt by everyone, minor damage
        - **5.0–5.9**: Moderate - Slight damage to buildings
        - **6.0–6.9**: Strong - Moderate damage in populated areas
        - **≥ 7.0**: Major - Serious damage over large areas
        """)

    with tab2:
        st.markdown("### Earthquake Activity - Last 30 Days")
        if 'datetime' not in df.columns and 'time' in df.columns:
            df['datetime'] = pd.to_datetime(df['time'], errors='coerce')

        df_sorted = df.sort_values(by='datetime')

        fig2 = px.scatter(
            df_sorted, x='datetime', y='mag',
            color='mag', size='mag',
            color_continuous_scale='Inferno',
            title="Earthquake Magnitudes Over Time"
        )
        fig2.update_layout(height=400, plot_bgcolor='rgba(0,0,0,0.1)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig2, use_container_width=True)

        fig3 = px.histogram(df, x='mag', nbins=20, title="Distribution of Earthquake Magnitudes")
        fig3.update_layout(height=350, plot_bgcolor='rgba(0,0,0,0.1)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig3, use_container_width=True)

        fig4 = px.scatter(df, x='depth', y='mag', color='mag', title="Depth vs Magnitude Relationship")
        fig4.update_layout(height=400, plot_bgcolor='rgba(0,0,0,0.1)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig4, use_container_width=True)

    with tab3:
        st.markdown("### Earthquake Data Records")
        search_term = st.text_input("🔍 Search by location:", "")
        filtered_data = df[df['place'].str.contains(search_term, case=False, na=False)] if search_term else df
        st.dataframe(filtered_data.sort_values(by='time', ascending=False), use_container_width=True, height=500)

        csv_data = filtered_data.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Current Data", csv_data, f"india_earthquakes_{datetime.datetime.now():%Y%m%d}.csv", "text/csv")

# Footer
st.markdown(f"""
<div class="footer">
    <p>Data sources: USGS, EMSC, CSV | Last updated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <p>This app is for educational use only. For official data, refer to government agencies.</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.info("ℹ️ Live feed data is cached for 5 minutes. Use 'Refresh Data' to manually update.")

# Add data directory creation helper
if data_source == "Local CSV File" and df.empty:
    if st.sidebar.button("🛠️ Create Data Directory"):
        try:
            os.makedirs("data", exist_ok=True)
            st.sidebar.success("✅ Created 'data' directory. Please place earthquake.csv file there.")
        except Exception as e:
            st.sidebar.error(f"Error creating directory: {e}")
