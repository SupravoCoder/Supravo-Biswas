import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import altair as alt
import time
import matplotlib as mpl
import plotly.express as px # type: ignore
import requests
import datetime

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
</style>
""", unsafe_allow_html=True)

# Load dataset with spinner
with st.spinner("🔄 Loading Earthquake Data..."):
    df = pd.read_csv("C:\\Users\\Supravo Biswas\\Desktop\\Coding\\Python Coding\\StreamlitPython\\myproject\\data\\earthquake.csv")
    df=df[df['place'].str.contains('India', case=False, na=False)]
    df['time'] = pd.to_datetime(df['time'], errors='coerce')
    df.dropna(subset=['time'], inplace=True)
    time.sleep(1.2)

# Progress bar
progress = st.progress(0)
for percent in range(50, 101, 10):
    time.sleep(0.05)
    progress.progress(percent)
progress.empty()

# Sidebar
st.sidebar.header("📂 Data Overview")
st.sidebar.write("Total Earthquakes:", len(df))
st.sidebar.write("Date Range:", df['time'].min().date(), "to", df['time'].max().date())

# ---- Chart 1: Magnitude Distribution
with st.expander("📈 Magnitude Distribution (Animated Histogram)", expanded=True):
    st.markdown("**Distribution of Earthquake Magnitudes**")
    fig1, ax1 = plt.subplots(figsize=(8, 4))
    sns.histplot(data=df, x='mag', bins=30, kde=True, color='orangered', ax=ax1)
    ax1.set_xlabel("Magnitude")
    ax1.set_ylabel("Frequency")
    ax1.set_title("Histogram of Earthquake Magnitudes")
    st.pyplot(fig1)
    time.sleep(0.8)

# ---- Chart 2: Top Locations
with st.expander("📍 Top 10 Locations with Most Earthquakes", expanded=True):
    st.markdown("**Top 10 Affected Locations**")
    top_places = df['place'].value_counts().head(10)
    fig2, ax2 = plt.subplots(figsize=(8, 4))
    sns.barplot(x=top_places.values, y=top_places.index, palette='viridis', ax=ax2)
    ax2.set_xlabel("Number of Earthquakes")
    ax2.set_ylabel("Location")
    ax2.set_title("Most Frequent Earthquake Locations")
    st.pyplot(fig2)
    time.sleep(0.8)

# ---- Chart 3: Magnitude vs Depth
with st.expander("🌐 Magnitude vs Depth Scatter Plot", expanded=True):
    st.markdown("**Scatter Plot: Magnitude vs Depth**")
    fig3, ax3 = plt.subplots(figsize=(8, 4))
    sns.scatterplot(data=df, x='depth', y='mag', alpha=0.6, hue='mag', palette='coolwarm', ax=ax3)
    ax3.set_xlabel("Depth (km)")
    ax3.set_ylabel("Magnitude")
    ax3.set_title("Depth vs Magnitude")
    ax3.legend([],[], frameon=False)  # Optional: remove redundant legend
    st.pyplot(fig3)
    time.sleep(0.8)

# ---- Chart 4: Monthly Earthquake Frequencyn
with st.expander("📆 Earthquakes Over Time", expanded=True):
    st.markdown("**Monthly Earthquake Frequency Over Time**")
    df['year_month'] = df['time'].dt.to_period('M').astype(str)
    monthly_counts = df.groupby('year_month').size().reset_index(name='counts')
    line_chart = alt.Chart(monthly_counts).mark_line(
        point=alt.OverlayMarkDef(color='orange', filled=True)
    ).encode(
        x=alt.X('year_month:T', title="Month"),
        y=alt.Y('counts:Q', title="Number of Earthquakes"),
        tooltip=['year_month', 'counts']
    ).properties(
        width=700,
        height=300
    ).interactive()
    st.altair_chart(line_chart, use_container_width=True)
    time.sleep(0.8)

# ---- Chart 5: Heatmap
with st.expander("🔥 Earthquake Geographic Density Heatmap", expanded=True):
    st.markdown("**Geographic Density of Earthquakes**")
    fig5, ax5 = plt.subplots(figsize=(8, 5))
    sns.kdeplot(
        x=df['longitude'], y=df['latitude'],
        cmap="Reds", fill=True, thresh=0.05, ax=ax5
    )
    ax5.set_xlabel("Longitude")
    ax5.set_ylabel("Latitude")
    ax5.set_title("Heatmap of Earthquake Locations")
    st.pyplot(fig5)


# Footer
st.success("✅ All charts rendered successfully!")
st.markdown("<div class='footer'>🗂 Data Source: 2010–2025 Earthquakes | Made with ❤️ using Streamlit</div>", unsafe_allow_html=True)
