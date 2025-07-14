# 🌍 Earthquake Susceptibility Predictor

A machine learning application that predicts earthquake susceptibility for any location using historical earthquake data, fault density, and terrain characteristics.

## Features

- **Location-based predictions**: Enter any place name to get earthquake risk assessment
- **Interactive map visualization**: See your location and nearest earthquake points
- **Safety rating system**: 0-5 scale rating with confidence levels
- **Terrain risk analysis**: Considers landslide-prone areas
- **Historical data insights**: Shows related earthquakes and patterns

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Train the Model
Run all cells in the `Susceptibility.ipynb` notebook to:
- Process the earthquake data
- Train the machine learning model
- Save scalers and model files

### 3. Run the Streamlit App
```bash
streamlit run streamlit_app.py
```

Or use the batch file on Windows:
```bash
run_app.bat
```

## Required Files

The following files must be present in the directory:
- `EarthquakeFeatures.csv` - Raw earthquake data
- `EarthquakePredictor.pkl` - Trained model
- `fault_density_scaler.pkl` - Fault density scaler
- `hubdist_scaler.pkl` - Distance scaler  
- `mag_scaler.pkl` - Magnitude scaler
- `earthquakes_labeled.csv` - Processed data with labels

## Usage

1. Open the Streamlit app in your browser
2. Enter a place name (e.g., "Delhi", "Guwahati", "Mumbai")
3. View the prediction results including:
   - Safety rating (0-5 scale)
   - Risk classification (Safe/Moderate/Unsafe)
   - Interactive map with location and nearest earthquake points
   - Distance to nearest fault/earthquake point
   - Historical earthquake data for the area

## Model Features

The model uses the following features for prediction:
- **Magnitude**: Average magnitude of nearby earthquakes
- **Distance**: Distance to nearest earthquake/fault point
- **Fault Density**: Density of faults in the area
- **Terrain Risk**: Whether location is in landslide-prone area

## Safety Classifications

- **Safe (0)**: Rating ≥ 2.5 - Low earthquake risk
- **Moderate (1)**: Rating 1.25-2.5 - Medium earthquake risk  
- **Unsafe (2)**: Rating < 1.25 - High earthquake risk

## Data Source

Based on earthquake data including:
- Historical earthquake records
- Fault line information
- Geographic coordinates
- Magnitude and depth measurements
- Terrain characteristics

## Disclaimer

This tool is for educational and research purposes. For official earthquake risk assessments, consult geological survey authorities and emergency management agencies.
