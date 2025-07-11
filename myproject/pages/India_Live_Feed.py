import streamlit as st
import pandas as pd
import plotly.express as px  # type: ignore
import time
import os

# ----------------------------------
# Page Configuration
# ----------------------------------
st.set_page_config(page_title="📊 Historical Earthquake Analysis - India & SAARC", layout="wide")
st.title("🌏 Earthquake Insights: India, SAARC & China")

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
</style>
""", unsafe_allow_html=True)

# ----------------------------------
# Show Current Working Directory
# ----------------------------------
st.sidebar.markdown("📁 **Working Directory:**")
st.sidebar.code(os.getcwd())

# ----------------------------------
# Load Data: From Local or Upload
# ----------------------------------
@st.cache_data
def load_earthquake_data(file):
    df = pd.read_csv(file)

    # 1. Parse or build 'time'
    if 'time' in df.columns:
        df['time'] = pd.to_datetime(df['time'], errors='coerce')
    else:
        df['time'] = pd.NaT

    cols_upper = df.columns.str.upper()
    col_map = {c.upper(): c for c in df.columns}

    if all(x in cols_upper for x in ['YR', 'MO', 'DT']):
        year = df[col_map['YR']].astype(int)
        month = df[col_map['MO']].astype(int)
        day = df[col_map['DT']].astype(int)
        hour = df[col_map['HR']].astype(int) if 'HR' in col_map else 0
        minute = df[col_map['MN']].astype(int) if 'MN' in col_map else 0
        second = df[col_map['SEC']].astype(float) if 'SEC' in col_map else 0

        df['time'] = df['time'].fillna(pd.to_datetime({
            'year': year,
            'month': month,
            'day': day,
            'hour': hour,
            'minute': minute,
            'second': second
        }, errors='coerce')) # type: ignore

    # 2. Auto-detect key columns
    def detect_column(df, options):
        for col in df.columns:
            for opt in options:
                if col.lower().startswith(opt):
                    return col
        return None

    lat_col = detect_column(df, ['lat'])
    lon_col = detect_column(df, ['lon', 'lng'])
    mag_col = detect_column(df, ['mag', 'magnitude'])
    place_col = detect_column(df, ['place', 'location', 'region', 'area'])

    if not lat_col or not lon_col or not mag_col:
        raise ValueError("❌ Required columns not found: latitude, longitude, or magnitude.")

    df = df.rename(columns={
        lat_col: 'latitude',
        lon_col: 'longitude',
        mag_col: 'mag'
    })

    if place_col:
        df = df.rename(columns={place_col: 'place'})
    else:
        df['place'] = "Unknown Location"

    # Optional: rename depth variants
    depth_col = detect_column(df, ['depth', 'dep'])
    if depth_col and depth_col != 'depth':
        df = df.rename(columns={depth_col: 'depth'})

    df.dropna(subset=['time', 'latitude', 'longitude', 'mag'], inplace=True)

    return df

# Use only the models directory for all files
models_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'Susceptability_pred_ML', 'Susceptability_pred_ML', 'models'))
default_file_path = os.path.join(models_path, r'C:\Users\Supravo Biswas\Desktop\Coding\Python Coding\StreamlitPython\myproject\data\earthquake.csv')

uploaded_file = st.sidebar.file_uploader("\U0001F4E4 Upload `earthquake.csv`", type="csv")

if uploaded_file is not None:
    df = load_earthquake_data(uploaded_file)
elif os.path.exists(default_file_path):
    df = load_earthquake_data(default_file_path)
else:
    st.error("❌ `earthquake.csv` not found in the models directory and no file uploaded. Please upload it using the sidebar.")
    st.stop()

st.markdown("### 📊 Loading Earthquake Data... Please wait.")
time.sleep(1)

# ----------------------------------
# Preprocess Data
# ----------------------------------
df['year'] = df['time'].dt.year
df['month'] = df['time'].dt.month
df['day'] = df['time'].dt.day

# ----------------------------------
# Sidebar Filters
# ----------------------------------
st.sidebar.header("🔍 Filter Data")

regions = ["All", "India", "Nepal", "Bangladesh", "Pakistan", "Sri Lanka", "Bhutan", "Maldives", "Afghanistan", "China"]
region = st.sidebar.selectbox("Region", regions)

date_range = st.sidebar.date_input("Date Range", [df['time'].min().date(), df['time'].max().date()])
min_mag = st.sidebar.slider("Minimum Magnitude", float(df['mag'].min()), float(df['mag'].max()), 4.0, 0.1)

if region != "All":
    df = df[df['place'].str.contains(region, case=False, na=False)]

if len(date_range) == 2:
    start_date, end_date = date_range
elif len(date_range) == 1:
    start_date = end_date = date_range[0]
else:
    start_date = df['time'].min().date()
    end_date = df['time'].max().date()

filtered_df = df[
    (df['time'].dt.date >= start_date) &
    (df['time'].dt.date <= end_date) &
    (df['mag'] >= min_mag)
]

st.success(f"🔎 Showing {len(filtered_df)} earthquakes in {region} from {start_date} to {end_date}")

# ----------------------------------
# Map View
# ----------------------------------
st.subheader("🗺️ Earthquake Locations Map with Details")

map_fig = px.scatter_mapbox(
    filtered_df,
    lat="latitude",
    lon="longitude",
    color="mag",
    size="mag",
    hover_name="place",
    hover_data={"mag": True, "depth": True, "time": True},
    color_continuous_scale="Turbo",
    size_max=15,
    zoom=3,
    height=600,
    title="Earthquake Map with Hover Info"
)

map_fig.update_layout(mapbox_style="open-street-map")
map_fig.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0})
st.plotly_chart(map_fig, use_container_width=True)

# ----------------------------------
# Charts and Insights
# ----------------------------------
st.subheader("📈 Magnitude Distribution")
st.plotly_chart(
    px.histogram(filtered_df, x="mag", nbins=25, color_discrete_sequence=['#66fcf1'], title="Earthquake Magnitudes"),
    use_container_width=True
)

st.subheader("📅 Earthquakes Over Time")
time_series = filtered_df.groupby(filtered_df['time'].dt.to_period('M')).size().reset_index(name='Counts')
time_series['time'] = time_series['time'].astype(str)
st.plotly_chart(
    px.line(time_series, x='time', y='Counts', markers=True, title="Monthly Earthquake Trends"),
    use_container_width=True
)

st.subheader("🕳️ Depth vs Magnitude")
st.plotly_chart(
    px.scatter(filtered_df, x='depth', y='mag', color='mag', size='mag', title='Depth vs Magnitude', color_continuous_scale='Turbo'),
    use_container_width=True
)

st.subheader("🌐 Earthquakes by Country (Keyword in Location)")
if 'place' in filtered_df.columns:
    country_counts = filtered_df['place'].str.extract(r'(India|Nepal|Pakistan|China|Bangladesh|Afghanistan|Sri Lanka|Bhutan|Maldives)', expand=False)
    country_counts = country_counts.value_counts().reset_index()
    country_counts.columns = ['Country', 'Count']
    st.plotly_chart(
        px.bar(country_counts, x='Country', y='Count', color='Country', title="Number of Earthquakes by Country"),
        use_container_width=True
    )
else:
    st.warning("The 'place' column is not available in the data, so country breakdown cannot be displayed.")

# ----------------------------------
# Table View
# ----------------------------------
st.subheader("📋 Raw Earthquake Data")
desired_columns = ['time', 'place', 'mag', 'depth', 'latitude', 'longitude', 'source']
available_columns = [col for col in desired_columns if col in filtered_df.columns]
st.dataframe(filtered_df[available_columns])

# ----------------------------------
# Footer
# ----------------------------------
st.markdown("---")
st.markdown("<div class='footer'>Data source: Local CSV (USGS Earthquake Records) | Supports flexible column naming | Built with ❤️ by Team Bhukamp</div>", unsafe_allow_html=True)

# Remove the cursor blob and click burst effects and replace them with the homepage's animated gradient background and glassmorphism effect.
st.markdown("""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;700&display=swap');

    /* Base Styling for Body and App */
    html, body, .stApp {
        height: 100%;
        margin: 0;
        padding: 0;
        font-family: 'Roboto', sans-serif;
        background: linear-gradient(-45deg, #0f3460, #2c5364, #134e5e, #0d4f3c);
        background-size: 300% 300%;
        animation: smoothGradient 20s ease infinite;
        color: #f8f8f8;
    }

    /* Background Animation */
    @keyframes smoothGradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Glass Container Styling */
    .glass-container {
        background: rgba(76, 161, 175, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 4px 10px rgba(15, 32, 39, 0.4);
        border: 1px solid rgba(196, 224, 229, 0.2);
    }

    /* Title Styling */
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

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(-45deg, #0f3460, #2c5364, #134e5e, #0d4f3c);
        background-size: 300% 300%;
        animation: smoothGradient 20s ease infinite;
        color: #f8f8f8;
        font-family: 'Roboto', sans-serif;
        border-right: 1px solid rgba(255, 255, 255, 0.1);
        padding: 1rem;
    }

    section[data-testid="stSidebar"] * {
        color: #f8f8f8 !important;
    }

    section[data-testid="stSidebar"] input,
    section[data-testid="stSidebar"] textarea,
    section[data-testid="stSidebar"] select {
        background-color: rgba(255, 255, 255, 0.07);
        color: #ffffff !important;
        border: none;
        border-radius: 6px;
    }

    /* Footer */
    .footer {
        text-align: center;
        font-size: 0.85em;
        color: #cccccc;
        margin-top: 40px;
    }

    /* Scrollbar Customization */
    ::-webkit-scrollbar {
        width: 8px;
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.2);
        border-radius: 10px;
    }
    ::-webkit-scrollbar-track {
        background: transparent;
    }

    /* Fix for Black Box Behind Lottie Animations */
    .st-lottie-container {
        background-color: transparent !important;
        box-shadow: none !important;
    }
</style>
""", unsafe_allow_html=True)


# Wrap the main content in a div with the glassmorphism effect
st.markdown('<div class="main-container">', unsafe_allow_html=True)
# ...existing code...
st.markdown('</div>', unsafe_allow_html=True)
