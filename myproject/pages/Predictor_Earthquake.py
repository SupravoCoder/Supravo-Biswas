import streamlit as st
import pandas as pd
import numpy as np
import os
import pickle
import io
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler
import plotly.express as px
import plotly.graph_objects as go

# Safely import Keras/TensorFlow
try:
    from tensorflow.keras.models import load_model
    KERAS_AVAILABLE = True
except ImportError:
    load_model = None  # Ensure load_model is always defined
    KERAS_AVAILABLE = False

# Centralized model and data paths
MODELS_DIR = r"Bhukamp/Susceptability_pred_ML/Susceptability_pred_ML"
LABELED_DATA_PATH = os.path.join(MODELS_DIR, "earthquakes_labeled.csv")
FEATURES_DATA_PATH = os.path.join(MODELS_DIR, "EarthquakeFeatures.csv")

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
    /* Enhanced Plotly legend text visibility */
    .js-plotly-plot .legend text {
        fill: #000000 !important;
        font-weight: bold !important;
        font-size: 13px !important;
        text-shadow: 1px 1px 2px rgba(255,255,255,0.8) !important;
    }
    .js-plotly-plot .legend .legendtitle text {
        fill: #000000 !important;
        font-weight: bold !important;
        font-size: 15px !important;
        text-shadow: 1px 1px 2px rgba(255,255,255,0.8) !important;
    }
    /* Ensure map markers have good visibility */
    .js-plotly-plot .scattermapbox text {
        text-shadow: 2px 2px 4px rgba(0,0,0,0.8) !important;
        font-weight: bold !important;
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

@st.cache_data
def load_data():
    """Loads the earthquake datasets with caching."""
    try:
        if not os.path.exists(FEATURES_DATA_PATH):
            st.error(f"Features data file not found at: {FEATURES_DATA_PATH}")
            return None, None
        
        earthquake_data = pd.read_csv(FEATURES_DATA_PATH)
        
        labeled_data = None
        if os.path.exists(LABELED_DATA_PATH):
            labeled_data = pd.read_csv(LABELED_DATA_PATH)
        
        return earthquake_data, labeled_data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None

def safe_load_model(path):
    """Safely loads a model (.pkl or .keras), handling errors gracefully."""
    if not os.path.exists(path):
        return None
    
    try:
        if path.endswith('.pkl'):
            with open(path, "rb") as f:
                return pickle.load(f)
        elif path.endswith('.keras') or path.endswith('.h5'):
            if not KERAS_AVAILABLE or load_model is None:
                st.warning("TensorFlow/Keras is not installed. Keras models cannot be loaded.")
                return None
            return load_model(path)
        else:
            st.warning(f"Unknown model format for file: {os.path.basename(path)}")
            return None
    except Exception as e:
        st.warning(f"Could not load model '{os.path.basename(path)}': {str(e)}")
        return None

def get_model_features(labeled_data):
    """Determines the available features for modeling."""
    potential_features = ['LAT', 'LONG_', 'DEPTH_KM', 'HubDist', 'FaultDensity_filled']
    available_features = [col for col in potential_features if col in labeled_data.columns]
    
    if not available_features:
        st.error("No required features found in the dataset.")
        return None
    
    return available_features

def prepare_data(labeled_data, features):
    """Prepares the data for model evaluation."""
    target_cols = ['mag']
    
    # Check for target column
    if 'mag' not in labeled_data.columns:
        st.error("Target column 'mag' not found in the dataset.")
        return None, None
    
    # Remove rows with missing values
    df = labeled_data.dropna(subset=features + target_cols).copy()
    
    if df.empty:
        st.error("No valid data rows found after removing missing values.")
        return None, None
    
    X = df[features]
    y = df[target_cols]
    
    return X, y

@st.cache_data
def evaluate_models():
    """Evaluates models and returns their performance metrics."""
    if not os.path.exists(LABELED_DATA_PATH):
        st.warning("Labeled data for evaluation not found.")
        return None
    
    try:
        test_data = pd.read_csv(LABELED_DATA_PATH)
        features = get_model_features(test_data)
        
        if features is None:
            return None
        
        X, y = prepare_data(test_data, features)
        if X is None or y is None:
            return None
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Model configurations
        models = {
            'Random Forest': 'random_forest_model.pkl',
        }
        
        # Note: Only Random Forest and PINN models are available for evaluation
        # Other models (SVR, MLP, LSTM) have been removed from the interface
        
        metrics = []
        
        for name, filename in models.items():
            path = os.path.join(MODELS_DIR, filename)
            model = safe_load_model(path)
            
            if model is None:
                metrics.append({
                    'Model': name,
                    'MAE': 'N/A',
                    'R² Score': 'N/A',
                    'Status': '❌ Model not found or corrupted'
                })
                continue
            
            try:
                # Make predictions based on model type
                if name in ['MLP', 'LSTM'] and KERAS_AVAILABLE:
                    y_pred = model.predict(X_scaled, verbose=0)
                    if y_pred.ndim > 1:
                        y_pred = y_pred.flatten()
                else:
                    y_pred = model.predict(X_scaled)
                
                # Calculate metrics
                mae = mean_absolute_error(y, y_pred)
                r2 = r2_score(y, y_pred)
                
                metrics.append({
                    'Model': name,
                    'MAE': round(mae, 4),
                    'R² Score': round(r2, 4),
                    'Status': '✅ Success'
                })
                
            except Exception as e:
                metrics.append({
                    'Model': name,
                    'MAE': 'N/A',
                    'R² Score': 'N/A',
                    'Status': f'❌ Error: {str(e)[:50]}...'
                })
        
        return pd.DataFrame(metrics) if metrics else None
    
    except Exception as e:
        st.error(f"Critical error in model evaluation: {e}")
        return None

def classify_risk_level(df):
    """Classifies earthquake risk based on enhanced magnitude assessment."""
    if 'mag' not in df.columns:
        st.warning("Magnitude column ('mag') missing for risk analysis.")
        return df
    
    def classify(mag):
        """Enhanced risk classification with 6 levels matching main app"""
        if mag >= 8.0:
            return 'Extreme'
        elif mag >= 7.0:
            return 'Major'
        elif mag >= 6.0:
            return 'High'
        elif mag >= 5.0:
            return 'Moderate'
        elif mag >= 4.0:
            return 'Low'
        else:
            return 'Minimal'
    
    df['Risk Level'] = df['mag'].apply(classify)
    return df

# Enhanced Risk Level Color Mapping (matching main app)
ENHANCED_RISK_COLORS = {
    'Extreme': '#8B0000',    # Dark Red
    'Major': '#FF0000',      # Red  
    'High': '#FF4500',       # Orange Red
    'Moderate': '#FF8C00',   # Dark Orange
    'Low': '#32CD32',        # Lime Green
    'Minimal': '#00CED1'     # Dark Turquoise
}

# Enhanced Risk Level Symbols
ENHANCED_RISK_SYMBOLS = {
    'Extreme': '🚨',
    'Major': '⚠️', 
    'High': '⚡',
    'Moderate': '📊',
    'Low': '📉',
    'Minimal': '🔹'
}

def display_risk_plots(df_risk):
    """Displays various plots for risk analysis."""
    # Check required columns
    required_cols = ['DEPTH_KM', 'mag', 'Risk Level']
    if not all(col in df_risk.columns for col in required_cols):
        st.error("Missing required columns for risk visualization.")
        return
    
    # Risk level distribution
    st.subheader("📊 Risk Level Distribution")
    risk_counts = df_risk['Risk Level'].value_counts()
    fig_pie = px.pie(
        values=risk_counts.values,
        names=risk_counts.index,
        title="Distribution of Earthquake Risk Levels",
        color_discrete_map=ENHANCED_RISK_COLORS
    )
    st.plotly_chart(fig_pie, use_container_width=True)
    
    # Magnitude vs Depth scatter plot
    st.subheader("🌋 Magnitude vs Depth Risk Analysis")
    fig_scatter = px.scatter(
        df_risk,
        x="DEPTH_KM",
        y="mag",
        color="Risk Level",
        color_discrete_map=ENHANCED_RISK_COLORS,
        hover_data=["LAT", "LONG_"] if all(col in df_risk.columns for col in ["LAT", "LONG_"]) else None,
        title="Magnitude vs Depth (Colored by Risk Level)"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    # 3D plot if geographic data is available
    if all(col in df_risk.columns for col in ['LONG_', 'LAT', 'DEPTH_KM']):
        st.subheader("🗺️ 3D Geographic Risk Distribution")
        fig_3d = px.scatter_3d(
            df_risk,
            x='LONG_',
            y='LAT',
            z='DEPTH_KM',
            color='Risk Level',
            size='mag',
            hover_name='Risk Level',
            title="3D Geographic Distribution of Earthquake Risk",
            color_discrete_map=ENHANCED_RISK_COLORS
        )
        st.plotly_chart(fig_3d, use_container_width=True)

def display_data_info(df):
    """Displays information about the dataset."""
    st.subheader("📋 Dataset Information")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Records", len(df))
    
    with col2:
        st.metric("Total Features", len(df.columns))
    
    with col3:
        st.metric("Missing Values", df.isnull().sum().sum())

def main():
    """Main function to run the Streamlit app."""
    st.set_page_config(
        page_title="🇮🇳 Bhukamp - Earthquake Dashboard",
        layout="wide",
        initial_sidebar_state="expanded",
        page_icon="🇮�"
    )
    
    st.title("🌍 Bhukamp - Earthquake Prediction & Risk Analysis Dashboard")
    st.markdown("---")
    
    # Load data
    with st.spinner("Loading data..."):
        earthquake_data, labeled_data = load_data()
    
    if earthquake_data is None:
        st.error("Application cannot start because the primary data file is missing.")
        st.stop()
    
    # Sidebar navigation
    st.sidebar.title("🇮🇳 Bhukamp Navigation")
    sections = [
        "📊 Dataset Preview",
        "⚠️ Risk Analysis & Earthquake ML Prediction",
        "📈 Susceptibility Map"
    ]
    
    section = st.sidebar.selectbox("Choose Section", sections)
    
    st.sidebar.markdown("---")
    st.sidebar.info("📝 This Bhukamp dashboard analyzes earthquake data and evaluates predictive models.")
    
    # Display Keras availability status
    if not KERAS_AVAILABLE:
        st.sidebar.warning("⚠️ TensorFlow/Keras not available. Some models will be skipped.")
    
    # Main content based on selected section
    if section == "📊 Dataset Preview":
        st.header("📊 Dataset Overview")
        
        # Data source information
        st.subheader("📁 Data Source Information")
        st.info("**Data Source:** USGS (United States Geological Survey) Earthquake Database")
        st.markdown("This dataset contains earthquake features processed from USGS GeoJSON earthquake data for comprehensive seismic analysis.")
        
        # Dataset information
        display_data_info(earthquake_data)
        
        # Dataset preview
        st.subheader("📋 Data Preview")
        st.dataframe(earthquake_data.head(20))
        
        # Download button
        csv_data = earthquake_data.to_csv(index=False)
        st.download_button(
            label="📥 Download Dataset",
            data=csv_data,
            file_name="earthquake_features.csv",
            mime="text/csv"
        )
        
        # Show additional datasets if available
        if os.path.exists(MODELS_DIR):
            st.subheader("📂 Additional Datasets")
            csv_files = [f for f in os.listdir(MODELS_DIR) if f.endswith('.csv')]
            
            if csv_files:
                selected_file = st.selectbox("Select additional dataset:", csv_files)
                if selected_file:
                    try:
                        additional_df = pd.read_csv(os.path.join(MODELS_DIR, selected_file))
                        st.dataframe(additional_df.head(10))
                        
                        additional_csv = additional_df.to_csv(index=False)
                        st.download_button(
                            label=f"📥 Download {selected_file}",
                            data=additional_csv,
                            file_name=selected_file,
                            mime="text/csv"
                        )
                    except Exception as e:
                        st.error(f"Error loading {selected_file}: {e}")
    
    elif section == "⚠️ Risk Analysis & Earthquake ML Prediction":
        st.header("⚠️ Risk Analysis & Earthquake ML Prediction")
        
        # Create tabs for different functionalities
        tab1, tab2 = st.tabs(["📊 Historical Risk Analysis", "🔮 Future Earthquake Predictions"])
        
        with tab1:
            st.subheader("📊 Historical Risk Analysis")
            
            if labeled_data is None:
                st.warning("⚠️ Risk analysis requires the 'earthquakes_labeled.csv' file.")
            else:
                # Perform risk classification
                df_risk = classify_risk_level(labeled_data.copy())
                
                # Risk summary
                st.subheader("📊 Risk Summary")
                risk_summary = df_risk['Risk Level'].value_counts()
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "🟢 Low Risk",
                        risk_summary.get('Low', 0),
                        f"{risk_summary.get('Low', 0) / len(df_risk) * 100:.1f}%"
                    )
                
                with col2:
                    st.metric(
                        "🟡 Moderate Risk",
                        risk_summary.get('Moderate', 0),
                        f"{risk_summary.get('Moderate', 0) / len(df_risk) * 100:.1f}%"
                    )
                
                with col3:
                    st.metric(
                        "🔴 High Risk",
                        risk_summary.get('High', 0),
                        f"{risk_summary.get('High', 0) / len(df_risk) * 100:.1f}%"
                    )
                
                # Risk data table
                st.subheader("📋 Risk Analysis Data")
                st.dataframe(df_risk.head(20))
                
                # Download button
                risk_csv = df_risk.to_csv(index=False)
                st.download_button(
                    label="📥 Download Risk Analysis",
                    data=risk_csv,
                    file_name="earthquake_risk_analysis.csv",
                    mime="text/csv"
                )
                
                # Risk visualizations
                display_risk_plots(df_risk)
                
                # Alerts section
                st.subheader("🚨 Risk Alerts")
                high_risk_count = risk_summary.get('High', 0)
                
                if high_risk_count > 0:
                    st.error(f"⚠️ Alert: {high_risk_count} high-risk earthquakes detected!")
                    
                    # Show high risk events
                    high_risk_events = df_risk[df_risk['Risk Level'] == 'High']
                    if not high_risk_events.empty:
                        st.subheader("🔴 High Risk Events")
                        st.dataframe(high_risk_events[['mag', 'DEPTH_KM', 'LAT', 'LONG_', 'Risk Level']].head(10))
                else:
                    st.success("✅ No high-risk earthquakes detected in the current dataset.")
        
        with tab2:
            st.subheader("🔮 Future Earthquake Predictions using Machine Learning")
            st.markdown("*Visualize earthquake predictions from various ML models for the next 25-100 years*")
            
            # File paths for prediction data
            main_path = r"C:\Users\Supravo Biswas\Desktop\Coding\Python Coding\StreamlitPython\myproject\data\future_earthquake_predictions_100years.csv"
            pinn_path = r"C:\Users\Supravo Biswas\Desktop\Coding\Python Coding\StreamlitPython\myproject\data\future_earthquake_predictions_india_25years_2025_2050.csv"
            
            # Model-specific column mappings
            model_options = {
                "Random Forest": ("RF_Predicted_LAT", "RF_Predicted_LONG_", "RF_Predicted_MAGMB"),
                "PINN": ("latitude", "longitude", "predicted_magnitude")
            }
            
            model_color = {
                "Random Forest": "orange", 
                "PINN": "blue"
            }
            
            # Model selection
            col1, col2 = st.columns([2, 1])
            with col1:
                model = st.selectbox("🤖 Choose Prediction Model", list(model_options.keys()))
            with col2:
                st.info(f"Model Color: {model_color[model].title()}")
            
            # Load correct dataset
            try:
                if model == "PINN":
                    if not os.path.exists(pinn_path):
                        st.error(f"PINN prediction file not found at: {pinn_path}")
                        st.stop()
                    df_pred = pd.read_csv(pinn_path)
                    st.success(f"✅ Loaded PINN predictions (25 years: 2025-2050)")
                else:
                    if not os.path.exists(main_path):
                        st.error(f"Main prediction file not found at: {main_path}")
                        st.stop()
                    df_pred = pd.read_csv(main_path)
                    st.success(f"✅ Loaded {model} predictions (100 years)")
                
                lat_col, lon_col, mag_col = model_options[model]
                
                # Validate columns
                missing = [col for col in (lat_col, lon_col, mag_col) if col not in df_pred.columns]
                if missing:
                    st.error(f"Missing columns for {model}: {missing}")
                    st.stop()
                
                # Drop missing values
                df_pred = df_pred.dropna(subset=[lat_col, lon_col, mag_col])
                
                if df_pred.empty:
                    st.warning("No valid prediction data available after cleaning.")
                    st.stop()
                
                # Dataset info
                st.subheader("📊 Prediction Dataset Information")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Predictions", len(df_pred))
                with col2:
                    st.metric("Avg Magnitude", f"{df_pred[mag_col].mean():.2f}")
                with col3:
                    st.metric("Max Magnitude", f"{df_pred[mag_col].max():.2f}")
                with col4:
                    st.metric("Min Magnitude", f"{df_pred[mag_col].min():.2f}")
                
                # === Magnitude Filter ===
                st.subheader("🎚️ Filter Controls")
                min_mag, max_mag = float(df_pred[mag_col].min()), float(df_pred[mag_col].max())
                mag_range = st.slider(
                    "Select Magnitude Range", 
                    min_value=round(min_mag, 1), 
                    max_value=round(max_mag, 1), 
                    value=(round(min_mag, 1), round(max_mag, 1)), 
                    step=0.1
                )
                df_pred = df_pred[(df_pred[mag_col] >= mag_range[0]) & (df_pred[mag_col] <= mag_range[1])]
                
                # === PINN-specific Filters ===
                if model == "PINN":
                    with st.expander("� Advanced PINN Filters"):
                        filter_applied = False
                        
                        if 'decade' in df_pred.columns:
                            decade = st.multiselect("📅 Select Decade", sorted(df_pred['decade'].dropna().unique()))
                            if decade:
                                df_pred = df_pred[df_pred['decade'].isin(decade)]
                                filter_applied = True
                        
                        if 'regional_zone' in df_pred.columns:
                            region = st.multiselect("🗺️ Select Regional Zone", sorted(df_pred['regional_zone'].dropna().unique()))
                            if region:
                                df_pred = df_pred[df_pred['regional_zone'].isin(region)]
                                filter_applied = True
                        
                        if 'risk_category' in df_pred.columns:
                            risk = st.multiselect("⚠️ Select Risk Category", sorted(df_pred['risk_category'].dropna().unique()))
                            if risk:
                                df_pred = df_pred[df_pred['risk_category'].isin(risk)]
                                filter_applied = True
                        
                        if filter_applied:
                            st.success(f"✅ Filters applied. Showing {len(df_pred)} predictions.")
                
                # Check if data remains after filtering
                if df_pred.empty:
                    st.warning("⚠️ No data available after applying filters. Please adjust your selection.")
                    st.stop()
                
                # === Map Visualization ===
                st.subheader(f"🗺️ {model} Earthquake Predictions Map")
                
                # Create the map
                fig = px.scatter_mapbox(
                    df_pred,
                    lat=lat_col,
                    lon=lon_col,
                    color=mag_col,
                    size=mag_col,
                    color_continuous_scale="OrRd",
                    zoom=4,
                    height=700,
                    title=f"📌 Future Predicted Earthquakes using {model} Model",
                    hover_data={
                        lat_col: ':.3f',
                        lon_col: ':.3f', 
                        mag_col: ':.2f'
                    },
                    labels={
                        lat_col: 'Latitude',
                        lon_col: 'Longitude',
                        mag_col: 'Predicted Magnitude'
                    }
                )
                
                fig.update_layout(
                    mapbox_style="carto-positron",
                    mapbox=dict(
                        center=dict(lat=20.5937, lon=78.9629),  # Center on India
                        zoom=4
                    ),
                    title=dict(x=0.5, font=dict(size=16)),
                    coloraxis_colorbar=dict(
                        title="Predicted<br>Magnitude"
                    )
                )
                fig.update_traces(marker=dict(opacity=0.7))
                
                st.plotly_chart(fig, use_container_width=True)
                
                # === Prediction Statistics ===
                st.subheader("�📈 Prediction Statistics")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Magnitude distribution
                    fig_hist = px.histogram(
                        df_pred,
                        x=mag_col,
                        nbins=20,
                        title=f"Magnitude Distribution - {model}",
                        labels={mag_col: "Predicted Magnitude", "count": "Number of Predictions"},
                        color_discrete_sequence=[model_color[model]]
                    )
                    fig_hist.update_layout(title=dict(x=0.5))
                    st.plotly_chart(fig_hist, use_container_width=True)
                
                with col2:
                    # Risk level classification for predictions
                    def classify_prediction_risk(mag):
                        if mag < 4.0:
                            return 'Low'
                        elif mag < 6.0:
                            return 'Moderate'
                        else:
                            return 'High'
                    
                    df_pred['Predicted_Risk'] = df_pred[mag_col].apply(classify_prediction_risk)
                    risk_counts = df_pred['Predicted_Risk'].value_counts()
                    
                    fig_pie = px.pie(
                        values=risk_counts.values,
                        names=risk_counts.index,
                        title=f"Predicted Risk Distribution - {model}",
                        color_discrete_map={'Low': 'green', 'Moderate': 'orange', 'High': 'red'}
                    )
                    fig_pie.update_layout(title=dict(x=0.5))
                    st.plotly_chart(fig_pie, use_container_width=True)
                
                # === Data Export ===
                st.subheader("📥 Export Predictions")
                
                # Add summary statistics to export
                summary_stats = pd.DataFrame({
                    'Metric': ['Total Predictions', 'Average Magnitude', 'Max Magnitude', 'Min Magnitude', 'High Risk Count', 'Moderate Risk Count', 'Low Risk Count'],
                    'Value': [
                        len(df_pred),
                        round(df_pred[mag_col].mean(), 2),
                        round(df_pred[mag_col].max(), 2),
                        round(df_pred[mag_col].min(), 2),
                        len(df_pred[df_pred['Predicted_Risk'] == 'High']),
                        len(df_pred[df_pred['Predicted_Risk'] == 'Moderate']),
                        len(df_pred[df_pred['Predicted_Risk'] == 'Low'])
                    ]
                })
                
                # Create comprehensive export data
                export_data = df_pred.copy()
                
                # Prepare download
                csv_data = export_data.to_csv(index=False)
                st.download_button(
                    label=f"📥 Download {model} Predictions (Filtered)",
                    data=csv_data,
                    file_name=f"{model.lower()}_earthquake_predictions_filtered.csv",
                    mime="text/csv"
                )
                
                # Show summary table
                st.subheader("📊 Summary Statistics")
                col1, col2 = st.columns([1, 1])
                with col1:
                    st.dataframe(summary_stats, hide_index=True)
                with col2:
                    st.dataframe(df_pred[['Predicted_Risk']].value_counts().reset_index(), hide_index=True)
                
                # Model comparison info
                st.subheader("🤖 Model Information")
                model_info = {
                    "Random Forest": "Ensemble method - Robust and interpretable predictions", 
                    "PINN": "Physics-Informed Neural Network - Incorporates physical laws"
                }
                
                st.info(f"**{model}**: {model_info[model]}")
                
            except FileNotFoundError as e:
                st.error(f"❌ Prediction data file not found: {str(e)}")
                st.info("📝 Please ensure the prediction CSV files are available in the data directory.")
            except Exception as e:
                st.error(f"❌ Error loading prediction data: {str(e)}")
                st.info("📝 Please check the file format and column names.")
    
    elif section == "📈 Susceptibility Map":
        st.header("📈 Earthquake Susceptibility Map")
        st.markdown("*Comprehensive analysis of earthquake-prone zones across India using ML-derived data*")

        if labeled_data is None:
            st.warning("⚠️ Labeled earthquake data is required for susceptibility analysis. Please ensure 'earthquakes_labeled.csv' is available in the models directory.")
            st.stop()

        # Performance optimization - cache data processing
        @st.cache_data
        def process_earthquake_data(data):
            """Process earthquake data with caching for better performance"""
            processed_data = data.copy()
            processed_data = processed_data.dropna(subset=['LAT', 'LONG_', 'mag'])
            processed_data['Risk Level'] = processed_data['mag'].apply(
                lambda mag: 'High' if mag >= 6.0 else ('Moderate' if mag >= 4.0 else 'Low')
            )
            return processed_data

        # Enhanced overview with key insights
        st.markdown("""
        ### 🔍 Key Insights
        This analysis provides comprehensive earthquake susceptibility mapping across India's major regions:
        - **Northern India**: Himalayan seismic zone with high tectonic activity
        - **Eastern India**: Bengal Basin and northeast regions 
        - **Western India**: Arabian Sea coastal and intraplate zones
        - **Southern India**: Peninsular shield with moderate activity
        - **Central India**: Intraplate regions with varying seismic patterns
        """)

        # Process data with caching
        data_copy = process_earthquake_data(labeled_data)
        
        # Enhanced region classification covering all of India
        region_mapping = {
            'Northern India': {
                'states': ['Jammu and Kashmir', 'Himachal Pradesh', 'Punjab', 'Haryana', 'Delhi', 'Uttarakhand'],
                'coordinates': {'lat': 30.7333, 'lon': 76.7794},
                'bounds': {'lat_min': 28, 'lat_max': 35, 'lon_min': 72, 'lon_max': 80}
            },
            'Eastern India': {
                'states': ['West Bengal', 'Odisha', 'Jharkhand', 'Bihar', 'Assam', 'Meghalaya', 'Nagaland', 'Manipur'],
                'coordinates': {'lat': 25.0961, 'lon': 85.3131},
                'bounds': {'lat_min': 20, 'lat_max': 28, 'lon_min': 85, 'lon_max': 97}
            },
            'Western India': {
                'states': ['Rajasthan', 'Gujarat', 'Maharashtra', 'Goa'],
                'coordinates': {'lat': 22.2587, 'lon': 71.8253},
                'bounds': {'lat_min': 15, 'lat_max': 30, 'lon_min': 68, 'lon_max': 78}
            },
            'Southern India': {
                'states': ['Tamil Nadu', 'Kerala', 'Karnataka', 'Andhra Pradesh', 'Telangana'],
                'coordinates': {'lat': 12.9716, 'lon': 77.5946},
                'bounds': {'lat_min': 8, 'lat_max': 20, 'lon_min': 72, 'lon_max': 84}
            },
            'Central India': {
                'states': ['Madhya Pradesh', 'Chhattisgarh', 'Uttar Pradesh'],
                'coordinates': {'lat': 23.4734, 'lon': 77.9479},
                'bounds': {'lat_min': 20, 'lat_max': 28, 'lon_min': 75, 'lon_max': 85}
            }
        }

        def classify_region(lat, lon):
            """Classify earthquakes into regions based on geographical boundaries"""
            for region, info in region_mapping.items():
                bounds = info['bounds']
                if (bounds['lat_min'] <= lat <= bounds['lat_max'] and 
                    bounds['lon_min'] <= lon <= bounds['lon_max']):
                    return region
            return 'Other'

        # Apply region classification
        data_copy['Region'] = data_copy.apply(lambda row: classify_region(row['LAT'], row['LONG_']), axis=1)
        
        # Filter out 'Other' regions and focus on the 5 main regions
        main_regions_data = data_copy[data_copy['Region'].isin(region_mapping.keys())]
        
        if main_regions_data.empty:
            st.warning("No earthquake data found for the defined regions. Please check the data coverage.")
            st.stop()

        # Calculate comprehensive risk statistics
        region_risk_summary = main_regions_data.groupby('Region')['Risk Level'].value_counts().unstack(fill_value=0)
        
        # Ensure all risk levels are present
        for risk_level in ['Extreme', 'Major', 'High', 'Moderate', 'Low', 'Minimal']:
            if risk_level not in region_risk_summary.columns:
                region_risk_summary[risk_level] = 0

        # Overview of India map
        st.subheader("🗺️ India - Earthquake Monitoring Overview")
        india_overview = px.scatter_mapbox(
            pd.DataFrame([region_mapping[region]['coordinates'] for region in region_mapping.keys()]),
            lat="lat",
            lon="lon",
            zoom=4,
            title="Earthquake Monitoring Zones Across India",
            mapbox_style="open-street-map",
            height=500
        )
        india_overview.update_traces(marker=dict(size=15, color='blue', opacity=0.7))
        india_overview.update_layout(
            title=dict(text="🗺️ Earthquake Monitoring Zones Across India", x=0.5, font=dict(size=16)),
            mapbox=dict(center=dict(lat=20.5937, lon=78.9629), zoom=4)
        )
        st.plotly_chart(india_overview, use_container_width=True)

        # Regional Risk Analysis
        st.subheader("📊 Regional Earthquake Risk Analysis")
        
        # Display risk summary table
        st.markdown("**Risk Distribution by Region:**")
        region_risk_summary['Total'] = region_risk_summary.sum(axis=1)
        
        # Calculate percentages for all risk levels
        for risk_level in ['Extreme', 'Major', 'High', 'Moderate', 'Low', 'Minimal']:
            region_risk_summary[f'{risk_level} %'] = (region_risk_summary[risk_level] / region_risk_summary['Total'] * 100).round(1)
        
        st.dataframe(
            region_risk_summary[['Extreme', 'Major', 'High', 'Moderate', 'Low', 'Minimal', 'Total', 
                               'Extreme %', 'Major %', 'High %', 'Moderate %', 'Low %', 'Minimal %']],
            use_container_width=True
        )

        # Enhanced Bar Chart
        fig_bar = px.bar(
            region_risk_summary.reset_index(),
            x='Region',
            y=['High', 'Moderate', 'Low'],
            title="📈 Earthquake Risk Distribution by Region",
            labels={'value': 'Number of Events', 'variable': 'Risk Level'},
            barmode='group',
            color_discrete_map={'High': '#FF0000', 'Moderate': '#FF8C00', 'Low': '#32CD32'},
            height=500
        )
        fig_bar.update_layout(
            title=dict(x=0.5, font=dict(size=16)),
            xaxis_title="Region",
            yaxis_title="Number of Earthquake Events",
            legend_title="Risk Level"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        # Comprehensive Map Visualizations
        st.subheader("🗺️ Comprehensive Risk Mapping")

        # Prepare data for mapping with safe type conversion
        zones_data = []
        for region in region_mapping.keys():
            if region in region_risk_summary.index:
                coords = region_mapping[region]['coordinates']
                
                # Safe integer conversion for risk values
                def safe_int_convert(value):
                    try:
                        return int(float(value)) if pd.notna(value) else 0
                    except (ValueError, TypeError):
                        return 0
                
                high_risk = safe_int_convert(region_risk_summary.loc[region, 'High']) if 'High' in region_risk_summary.columns else 0
                moderate_risk = safe_int_convert(region_risk_summary.loc[region, 'Moderate']) if 'Moderate' in region_risk_summary.columns else 0
                low_risk = safe_int_convert(region_risk_summary.loc[region, 'Low']) if 'Low' in region_risk_summary.columns else 0
                total_events = high_risk + moderate_risk + low_risk
                
                # Determine dominant risk level safely
                risk_counts = {'High': high_risk, 'Moderate': moderate_risk, 'Low': low_risk}
                dominant_risk = max(risk_counts.keys(), key=lambda x: risk_counts[x]) if total_events > 0 else 'Low'
                
                zones_data.append({
                    'Region': region,
                    'lat': coords['lat'],
                    'lon': coords['lon'],
                    'High Risk': high_risk,
                    'Moderate Risk': moderate_risk,
                    'Low Risk': low_risk,
                    'Total Events': total_events,
                    'Dominant Risk': dominant_risk,
                    'Risk Score': (high_risk * 3 + moderate_risk * 2 + low_risk * 1) / total_events if total_events > 0 else 0
                })

        zones_df = pd.DataFrame(zones_data)

        # 1. Regional Overview Map
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Regional Distribution:**")
            fig_regional = px.scatter_mapbox(
                zones_df,
                lat="lat",
                lon="lon",
                size="Total Events",
                color="Region",
                hover_name="Region",
                hover_data={"High Risk": True, "Moderate Risk": True, "Low Risk": True, "Total Events": True},
                title="Earthquake Events by Region",
                mapbox_style="open-street-map",
                size_max=40,
                height=400
            )
            fig_regional.update_layout(
                title=dict(x=0.5, font=dict(size=12)),
                mapbox=dict(center=dict(lat=20.5937, lon=78.9629), zoom=4),
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig_regional, use_container_width=True)

        with col2:
            st.markdown("**Risk Level Distribution:**")
            fig_risk = px.scatter_mapbox(
                zones_df,
                lat="lat",
                lon="lon",
                size="Total Events",
                color="Dominant Risk",
                hover_name="Region",
                hover_data={"High Risk": True, "Moderate Risk": True, "Low Risk": True},
                title="Dominant Risk Levels",
                mapbox_style="open-street-map",
                color_discrete_map={"High": "#FF0000", "Moderate": "#FF8C00", "Low": "#32CD32"},
                size_max=40,
                height=400
            )
            fig_risk.update_layout(
                title=dict(x=0.5, font=dict(size=12)),
                mapbox=dict(center=dict(lat=20.5937, lon=78.9629), zoom=4),
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig_risk, use_container_width=True)

        # 2. Detailed Risk Assessment Map
        st.markdown("**Detailed Risk Assessment with Symbols:**")
        fig_detailed = go.Figure()
        
        # Color and symbol mapping - Enhanced for better visibility
        risk_config = {
            'High': {'color': '#FF0000', 'symbol': 'triangle-up', 'size': 35},
            'Moderate': {'color': '#FF8C00', 'symbol': 'diamond', 'size': 30},
            'Low': {'color': '#32CD32', 'symbol': 'circle', 'size': 25}
        }
        
        for _, row in zones_df.iterrows():
            config = risk_config[row['Dominant Risk']]
            
            # Add text outline effect by adding multiple text traces with slight offsets
            text_content = f"<b>{row['Region']}</b><br><b>{row['Dominant Risk']} Risk</b><br>{row['Total Events']} events"
            
            # Text shadow/outline (black background)
            fig_detailed.add_trace(go.Scattermapbox(
                lat=[row['lat']],
                lon=[row['lon']],
                mode='text',
                text=text_content,
                textposition="top center",
                textfont=dict(
                    size=12, 
                    color="black",  # Shadow color
                    family="Arial Black"
                ),
                showlegend=False,
                hoverinfo='skip'
            ))
            
            # Main marker and text
            fig_detailed.add_trace(go.Scattermapbox(
                lat=[row['lat']],
                lon=[row['lon']],
                mode='markers+text',
                marker=dict(
                    size=config['size'],
                    color=config['color'],
                    symbol=config['symbol'],
                    opacity=0.9
                    # Note: scattermapbox markers don't support line borders
                ),
                text=text_content,
                textposition="top center",
                textfont=dict(
                    size=12,  # Slightly larger text
                    color="white",  # White text for better contrast
                    family="Arial Black"
                ),
                hovertemplate=(
                    f"<b>{row['Region']}</b><br>"
                    f"<b>Dominant Risk:</b> {row['Dominant Risk']}<br>"
                    f"<b>Total Events:</b> {row['Total Events']}<br>"
                    f"<b>High Risk:</b> {row['High Risk']}<br>"
                    f"<b>Moderate Risk:</b> {row['Moderate Risk']}<br>"
                    f"<b>Low Risk:</b> {row['Low Risk']}<br>"
                    f"<b>Risk Score:</b> {row['Risk Score']:.2f}<br>"
                    "<extra></extra>"
                ),
                name=f"{row['Region']} ({row['Dominant Risk']})",
                showlegend=True
            ))
        
        fig_detailed.update_layout(
            mapbox=dict(
                style="carto-positron",  # Lighter map style for better contrast
                center=dict(lat=20.5937, lon=78.9629),
                zoom=4
            ),
            title=dict(
                text="<b>🎯 Comprehensive Earthquake Risk Assessment Map</b>",
                x=0.5,
                font=dict(size=18, color="white", family="Arial Black")
            ),
            height=650,  # Slightly taller for better legend visibility
            legend=dict(
                orientation="v",
                yanchor="top",
                y=0.98,
                xanchor="left", 
                x=1.01,
                bgcolor="rgba(255,255,255,0.98)",  # Nearly opaque white background
                bordercolor="rgba(0,0,0,0.8)",
                borderwidth=3,
                font=dict(
                    size=13, 
                    color="rgba(0,0,0,0.9)",  # Nearly black text for maximum contrast
                    family="Arial Black"
                ),
                title=dict(
                    text="<b>🎯 Risk Levels</b>",
                    font=dict(
                        size=15, 
                        color="rgba(0,0,0,0.95)",  # Nearly black title
                        family="Arial Black"
                    )
                )
                # Note: xpad and ypad are not valid properties for Plotly legends
                # Use itemsizing, indentation, or tracegroupgap for spacing control
            ),
            paper_bgcolor="rgba(14,17,23,1)",  # Match app background
            plot_bgcolor="rgba(14,17,23,1)",
            font=dict(color="white")
        )
        
        st.plotly_chart(fig_detailed, use_container_width=True)

        # 3. Risk Statistics and Insights
        st.subheader("📊 Risk Statistics & Insights")
        
        # Regional statistics in columns
        cols = st.columns(5)
        for i, (_, row) in enumerate(zones_df.iterrows()):
            with cols[i]:
                risk_color = {"High": "🔴", "Moderate": "🟠", "Low": "🟢"}[row['Dominant Risk']]
                st.metric(
                    f"{risk_color} {row['Region']}",
                    f"{row['Total Events']} events",
                    f"Risk Score: {row['Risk Score']:.2f}"
                )
                st.write(f"🔺 High: {row['High Risk']}")
                st.write(f"🔶 Moderate: {row['Moderate Risk']}")
                st.write(f"🔵 Low: {row['Low Risk']}")

        # Overall statistics
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Overall Risk Distribution:**")
            total_high = zones_df['High Risk'].sum()
            total_moderate = zones_df['Moderate Risk'].sum()
            total_low = zones_df['Low Risk'].sum()
            total_events = total_high + total_moderate + total_low
            
            overall_stats = pd.DataFrame({
                'Risk Level': ['High', 'Moderate', 'Low'],
                'Count': [total_high, total_moderate, total_low],
                'Percentage': [
                    f"{(total_high/total_events*100):.1f}%" if total_events > 0 else "0%",
                    f"{(total_moderate/total_events*100):.1f}%" if total_events > 0 else "0%",
                    f"{(total_low/total_events*100):.1f}%" if total_events > 0 else "0%"
                ]
            })
            st.dataframe(overall_stats, use_container_width=True, hide_index=True)

        with col2:
            st.markdown("**Risk Distribution Pie Chart:**")
            fig_pie = px.pie(
                values=[total_high, total_moderate, total_low],
                names=['High', 'Moderate', 'Low'],
                color_discrete_map={'High': '#FF0000', 'Moderate': '#FF8C00', 'Low': '#32CD32'},
                hole=0.4
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            fig_pie.update_layout(height=300, showlegend=False)
            st.plotly_chart(fig_pie, use_container_width=True)

        # Legend and Methodology
        st.subheader("📋 Legend & Methodology")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Map Symbols:**
            - 🔺 **Red Triangle**: High Risk Zones (Magnitude ≥ 6.0)
            - 🔶 **Orange Square**: Moderate Risk Zones (4.0 ≤ Magnitude < 6.0)
            - 🔵 **Green Circle**: Low Risk Zones (Magnitude < 4.0)
            - **Size**: Proportional to total earthquake events
            """)
        
        with col2:
            st.markdown(f"""
            **Analysis Summary:**
            - **Dataset**: {len(main_regions_data)} earthquake events analyzed
            - **Regions Covered**: 5 major zones of India
            - **Risk Classification**: Based on earthquake magnitude
            - **Data Source**: Historical seismic data processed through ML
            - **Last Updated**: Real-time analysis
            """)

        # High-Risk Alerts
        high_risk_regions = zones_df[zones_df['Dominant Risk'] == 'High']
        if not high_risk_regions.empty:
            st.error(f"⚠️ **HIGH RISK ALERT**: {len(high_risk_regions)} region(s) showing high earthquake risk!")
            for _, region in high_risk_regions.iterrows():
                st.warning(f"🚨 **{region['Region']}**: {region['High Risk']} high-risk events recorded")
        else:
            st.success("✅ No regions currently showing dominant high-risk earthquake activity.")

        # Export functionality for comprehensive reporting
        st.subheader("📥 Export Analysis Results")
        
        # CSV Export (always available)
        if st.button("📄 Generate Comprehensive CSV Report"):
            # Create comprehensive CSV report
            from io import StringIO
            csv_output = StringIO()
            csv_output.write("=== EARTHQUAKE SUSCEPTIBILITY ANALYSIS REPORT ===\n")
            csv_output.write(f"Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            csv_output.write(f"Total Events Analyzed: {len(main_regions_data)}\n")
            csv_output.write(f"Regions Covered: {', '.join(region_mapping.keys())}\n\n")
            
            csv_output.write("=== REGIONAL RISK SUMMARY ===\n")
            region_risk_summary.to_csv(csv_output)
            csv_output.write("\n=== ZONE ANALYSIS ===\n")
            zones_df.to_csv(csv_output, index=False)
            csv_output.write("\n=== OVERALL STATISTICS ===\n")
            overall_stats.to_csv(csv_output, index=False)
            
            st.download_button(
                label="📥 Download Comprehensive Analysis Report (CSV)",
                data=csv_output.getvalue(),
                file_name=f"earthquake_analysis_report_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
            st.success("✅ Comprehensive CSV Report generated successfully!")

        # 4. Actual Earthquake Data Points Map
        st.subheader("🗺️ Actual Earthquake Distribution Map")
        st.markdown("**All earthquake events plotted with density-based visualization:**")
        
        # Create earthquake points map with density visualization
        fig_earthquake_points = px.density_mapbox(
            main_regions_data,
            lat='LAT',
            lon='LONG_',
            z='mag',
            radius=10,
            center=dict(lat=20.5937, lon=78.9629),
            zoom=4,
            mapbox_style="open-street-map",
            title="🔴 Earthquake Density Heatmap - Red indicates high activity zones",
            color_continuous_scale="Reds",
            height=600
        )
        
        fig_earthquake_points.update_layout(
            title=dict(
                text="🔴 Earthquake Density Heatmap - Dense areas shown in red",
                x=0.5,
                font=dict(size=16)
            ),
            coloraxis_colorbar=dict(
                title="Earthquake<br>Magnitude<br>Density"
            )
        )
        
        st.plotly_chart(fig_earthquake_points, use_container_width=True)
        
        # 5. Individual earthquake points with risk-based coloring
        st.markdown("**Individual earthquake events with risk classification:**")
        
        # Sample data if too many points (for performance)
        display_data = main_regions_data.copy()
        if len(display_data) > 1000:
            display_data = display_data.sample(n=1000, random_state=42)
            st.info(f"📊 Showing sample of 1000 points from {len(main_regions_data)} total earthquakes for better performance")
        
        fig_scatter_map = px.scatter_mapbox(
            display_data,
            lat='LAT',
            lon='LONG_',
            color='Risk Level',
            size='mag',
            hover_data=['Region', 'mag', 'Risk Level'],
            color_discrete_map={'High': '#FF0000', 'Moderate': '#FF8C00', 'Low': '#32CD32'},
            zoom=4,
            center=dict(lat=20.5937, lon=78.9629),
            mapbox_style="open-street-map",
            title="Individual Earthquake Events by Risk Level",
            height=600
        )
        
        fig_scatter_map.update_layout(
            title=dict(
                text="🎯 Individual Earthquake Events - Color coded by risk level",
                x=0.5,
                font=dict(size=16)
            ),
            legend=dict(
                orientation="v",
                yanchor="top",
                y=1,
                xanchor="left",
                x=1.02,
                title="Risk Level"
            )
        )
        
        st.plotly_chart(fig_scatter_map, use_container_width=True)
        
        # Density analysis by region
        st.subheader("📈 Earthquake Density Analysis by Region")
        
        # Calculate earthquake density per region
        region_density = main_regions_data.groupby('Region').agg({
            'LAT': 'count',
            'mag': ['mean', 'max', 'std']
        }).round(2)
        
        region_density.columns = ['Total_Events', 'Avg_Magnitude', 'Max_Magnitude', 'Mag_Std_Dev']
        region_density = region_density.reset_index()
        region_density = region_density.sort_values('Total_Events', ascending=False)
        
        # Color coding based on density
        def get_density_color(count):
            if count >= region_density['Total_Events'].quantile(0.8):
                return "🔴 Very High Density"
            elif count >= region_density['Total_Events'].quantile(0.6):
                return "🟠 High Density"
            elif count >= region_density['Total_Events'].quantile(0.4):
                return "🟡 Medium Density"
            else:
                return "🟢 Low Density"
        
        region_density['Density_Level'] = region_density['Total_Events'].apply(get_density_color)
        
        st.markdown("**Earthquake density ranking by region:**")
        st.dataframe(region_density, use_container_width=True, hide_index=True)
        
        # Density visualization
        fig_density_bar = px.bar(
            region_density,
            x='Region',
            y='Total_Events',
            color='Total_Events',
            color_continuous_scale='Reds',
            title="🔥 Earthquake Event Density by Region - Red indicates high density",
            labels={'Total_Events': 'Number of Earthquakes', 'Region': 'Indian Regions'},
            text='Total_Events'
        )
        
        fig_density_bar.update_traces(texttemplate='%{text}', textposition='outside')
        fig_density_bar.update_layout(
            title=dict(x=0.5, font=dict(size=16)),
            showlegend=False,
            height=400
        )
        
        st.plotly_chart(fig_density_bar, use_container_width=True)

    # Footer
    st.markdown("---")
    st.markdown("<div class='footer'>Built with ❤️ from Team Bhukamp</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
