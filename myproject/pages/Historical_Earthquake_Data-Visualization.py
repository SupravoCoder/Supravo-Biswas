import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import altair as alt
import time
import matplotlib as mpl
import plotly.express as px
from pathlib import Path
import numpy as np
import os

# Set style and page layout
st.set_page_config(page_title="Historical Earthquake Analysis", layout="wide")
sns.set_style("whitegrid")
mpl.rcParams['figure.dpi'] = 120
mpl.rcParams['axes.titlesize'] = 14
mpl.rcParams['axes.labelsize'] = 12

# Title
st.title("📊 Historical Earthquake Data - India")

# Replace existing CSS with enhanced gradient background and animations
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
    .stAlert {
        background-color: rgba(255, 255, 255, 0.1);
        border: none;
    }
    .stProgress > div > div {
        background-image: linear-gradient(to right, #1b4332, #2d6a4f, #40916c);
    }
</style>
""", unsafe_allow_html=True)

# Function to get relative path for data file
@st.cache_data
def get_data_path():
    """Get the path to the earthquake data file, handling different deployment environments"""
    # Try different possible locations
    possible_paths = [
        # Local development path - relative to this script
        Path(__file__).parent.parent / "data" / "earthquake.csv",
        # Repository root relative path
        Path("myproject/data/earthquake.csv"),
        # Current directory path
        Path("data/earthquake.csv"),
        # Fallback to original path (not recommended for deployment)
        Path("C:/Users/Supravo Biswas/Desktop/Coding/Python Coding/StreamlitPython/myproject/data/earthquake.csv")
    ]
    
    for path in possible_paths:
        if path.exists():
            return str(path)
    
    # If no file is found, return the first path (will cause an error, but with a meaningful path)
    return str(possible_paths[0])

# Load and process data with caching
@st.cache_data(ttl=3600)
def load_earthquake_data():
    """Load and preprocess earthquake data with caching for better performance"""
    try:
        data_path = get_data_path()
        df = pd.read_csv(data_path)
        # Filter for India
        df = df[df['place'].str.contains('India', case=False, na=False)]
        df['time'] = pd.to_datetime(df['time'], errors='coerce')
        df.dropna(subset=['time'], inplace=True)
        
        # Add additional calculated columns for analysis
        df['year'] = df['time'].dt.year
        df['month'] = df['time'].dt.month
        df['day'] = df['time'].dt.day
        df['hour'] = df['time'].dt.hour
        df['magnitude_category'] = pd.cut(
            df['mag'], 
            bins=[0, 2, 4, 6, 8, 10], 
            labels=['Very Minor', 'Minor', 'Moderate', 'Strong', 'Major']
        )
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        # Return empty DataFrame with expected columns to prevent further errors
        return pd.DataFrame(columns=['time', 'place', 'mag', 'depth', 'latitude', 'longitude'])

# Load the data with spinner
with st.spinner("🔄 Loading Earthquake Data..."):
    df = load_earthquake_data()
    if df.empty:
        st.warning("No earthquake data found for India. Please check the data source.")

# Progress bar
if not df.empty:
    progress = st.progress(0)
    for percent in range(50, 101, 10):
        time.sleep(0.03)  # Reduced sleep time for better UX
        progress.progress(percent)
    progress.empty()

# Sidebar - Data Overview and Filters
st.sidebar.header("📂 Data Overview")
if not df.empty:
    st.sidebar.write("Total Earthquakes:", len(df))
    st.sidebar.write("Date Range:", df['time'].min().date(), "to", df['time'].max().date())
    
    # Add interactive filters
    st.sidebar.header("🔍 Filters")
    
    # Date range filter
    min_date = df['time'].min().date()
    max_date = df['time'].max().date()
    
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = df[(df['time'].dt.date >= start_date) & (df['time'].dt.date <= end_date)]
    else:
        filtered_df = df.copy()
    
    # Magnitude filter
    min_mag = float(df['mag'].min())
    max_mag = float(df['mag'].max())
    mag_range = st.sidebar.slider(
        "Magnitude Range",
        min_value=min_mag,
        max_value=max_mag,
        value=(min_mag, max_mag),
        step=0.1
    )
    
    filtered_df = filtered_df[(filtered_df['mag'] >= mag_range[0]) & (filtered_df['mag'] <= mag_range[1])]
    
    # Show filtered data count
    st.sidebar.write("Filtered Earthquakes:", len(filtered_df))
    
    # Download filtered data option
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(
        label="📥 Download Filtered Data",
        data=csv,
        file_name="filtered_earthquake_data.csv",
        mime="text/csv",
    )

    # Display summary metrics at the top
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Earthquakes", f"{len(filtered_df):,}")
    with col2:
        st.metric("Average Magnitude", f"{filtered_df['mag'].mean():.2f}")
    with col3:
        st.metric("Max Magnitude", f"{filtered_df['mag'].max():.2f}")
    with col4:
        st.metric("Recent Event", filtered_df['time'].max().strftime("%Y-%m-%d"))

    # Main visualizations section
    tab1, tab2, tab3 = st.tabs(["📊 Statistical Analysis", "🗺️ Geographical Analysis", "🔍 Detailed Data"])

    with tab1:
        # ---- Chart 1: Magnitude Distribution
        with st.expander("📈 Magnitude Distribution", expanded=True):
            st.markdown("**Distribution of Earthquake Magnitudes**")
            fig1 = px.histogram(
                filtered_df, 
                x='mag',
                nbins=30,
                color_discrete_sequence=['orangered'],
                labels={'mag': 'Magnitude'},
                title="Distribution of Earthquake Magnitudes",
                opacity=0.7
            )
            fig1.update_layout(
                xaxis_title="Magnitude",
                yaxis_title="Frequency",
                plot_bgcolor='rgba(0,0,0,0.1)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color="#f8f8f8")
            )
            # Add a kde line
            fig1.add_scatter(
                x=filtered_df['mag'].sort_values(),
                y=filtered_df['mag'].value_counts(normalize=True, bins=30).sort_index().cumsum(),
                mode='lines',
                line=dict(color='cyan', width=2),
                name='Cumulative'
            )
            st.plotly_chart(fig1, use_container_width=True)

        # ---- Chart 3: Magnitude vs Depth
        with st.expander("🌐 Magnitude vs Depth Relationship", expanded=True):
            st.markdown("**Scatter Plot: Magnitude vs Depth**")
            fig3 = px.scatter(
                filtered_df, 
                x='depth', 
                y='mag',
                color='mag',
                color_continuous_scale='Viridis',
                opacity=0.7,
                hover_data=['place', 'time'],
                labels={'mag': 'Magnitude', 'depth': 'Depth (km)'}
            )
            fig3.update_layout(
                xaxis_title="Depth (km)",
                yaxis_title="Magnitude",
                title="Relationship Between Earthquake Depth and Magnitude",
                plot_bgcolor='rgba(0,0,0,0.1)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color="#f8f8f8")
            )
            st.plotly_chart(fig3, use_container_width=True)

        # ---- Chart 4: Monthly Earthquake Frequency
        with st.expander("📆 Earthquakes Over Time", expanded=True):
            st.markdown("**Monthly Earthquake Frequency Over Time**")
            filtered_df['year_month'] = filtered_df['time'].dt.to_period('M').astype(str)
            monthly_counts = filtered_df.groupby('year_month').size().reset_index(name='counts')
            
            fig4 = px.line(
                monthly_counts,
                x='year_month',
                y='counts',
                markers=True,
                labels={'counts': 'Number of Earthquakes', 'year_month': 'Month'},
                title="Monthly Earthquake Frequency"
            )
            fig4.update_layout(
                xaxis_title="Month",
                yaxis_title="Number of Earthquakes",
                plot_bgcolor='rgba(0,0,0,0.1)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color="#f8f8f8")
            )
            st.plotly_chart(fig4, use_container_width=True)

    with tab2:
        # ---- Chart 2: Top Locations
        with st.expander("📍 Top 10 Locations with Most Earthquakes", expanded=True):
            st.markdown("**Top 10 Affected Locations**")
            top_places = filtered_df['place'].value_counts().head(10)
            fig2 = px.bar(
                x=top_places.values,
                y=top_places.index,
                orientation='h',
                color=top_places.values,
                color_continuous_scale='Viridis',
                labels={'x': 'Number of Earthquakes', 'y': 'Location'}
            )
            fig2.update_layout(
                xaxis_title="Number of Earthquakes",
                yaxis_title="Location",
                title="Most Frequent Earthquake Locations",
                plot_bgcolor='rgba(0,0,0,0.1)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color="#f8f8f8")
            )
            st.plotly_chart(fig2, use_container_width=True)
        
        # ---- Map visualization with Plotly
        with st.expander("🗺️ Interactive Earthquake Map", expanded=True):
            st.markdown("**Geographic Distribution of Earthquakes**")
            fig_map = px.scatter_mapbox(
                filtered_df,
                lat='latitude',
                lon='longitude',
                color='mag',
                size='mag',
                size_max=15,
                zoom=4,
                center={"lat": 20.5937, "lon": 78.9629},  # Center of India
                hover_name='place',
                hover_data=['time', 'mag', 'depth'],
                color_continuous_scale='Viridis',
                mapbox_style="carto-darkmatter"
            )
            fig_map.update_layout(
                title="Earthquake Locations and Magnitudes",
                margin={"r":0, "t":40, "l":0, "b":0},
                height=600
            )
            st.plotly_chart(fig_map, use_container_width=True)

        # ---- Chart 5: Heatmap using Plotly
        with st.expander("🔥 Earthquake Geographic Density", expanded=True):
            st.markdown("**Density of Earthquake Locations**")
            fig5 = px.density_mapbox(
                filtered_df, 
                lat='latitude', 
                lon='longitude', 
                z='mag', 
                radius=10,
                center={"lat": 20.5937, "lon": 78.9629},
                zoom=4, 
                mapbox_style="carto-darkmatter",
                color_continuous_scale='Viridis'
            )
            fig5.update_layout(
                title="Earthquake Density Map",
                margin={"r":0, "t":40, "l":0, "b":0},
                height=500
            )
            st.plotly_chart(fig5, use_container_width=True)

    with tab3:
        # Data table with search
        st.markdown("#### Earthquake Data Explorer")
        search_term = st.text_input("🔍 Search by location:", "")
        if search_term:
            search_results = filtered_df[filtered_df['place'].str.contains(search_term, case=False)]
            st.dataframe(search_results, use_container_width=True)
        else:
            st.dataframe(filtered_df, use_container_width=True)
else:
    st.error("No data available. Please check the data source and try again.")

# Footer
st.markdown("<div class='footer'>🗂 Data Source: 2010–2025 Earthquakes | Made with ❤️ using Streamlit</div>", unsafe_allow_html=True)

# Add a message about data loading issues if needed
if df.empty:
    st.warning("""
    ⚠️ Unable to load earthquake data. This could be due to:
    1. The data file path needs updating
    2. The CSV file format may have changed
    3. Server access issues
    
    Please check the data source and try again.
    """)
