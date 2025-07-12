# Bhukamp Models Directory

This directory contains the machine learning models and data files required for the Bhukamp earthquake prediction system.

## Required Files

### Model Files
- **EarthquakePredictor.pkl** - Main earthquake prediction model
- **fault_density_scaler.pkl** - Scaler for fault density features
- **hubdist_scaler.pkl** - Scaler for hub distance features  
- **mag_scaler.pkl** - Scaler for magnitude features

### Data Files
- **EarthquakeFeatures.csv** - Main earthquake features dataset
- **earthquakes_labeled.csv** - Labeled earthquake data for risk analysis

## File Descriptions

### EarthquakePredictor.pkl
The main machine learning model used for earthquake susceptibility prediction. Contains both the trained model and expected column order.

### Scaler Files
These files contain the StandardScaler objects used to normalize input features:
- `fault_density_scaler.pkl` - Normalizes fault density values
- `hubdist_scaler.pkl` - Normalizes hub distance values
- `mag_scaler.pkl` - Normalizes magnitude values

### Data Files
- `EarthquakeFeatures.csv` - Contains processed earthquake features from USGS data
- `earthquakes_labeled.csv` - Contains labeled earthquake data with risk classifications

## Usage

These files are automatically loaded by the Streamlit applications:
- `pages/Predictor_Earthquake.py` - Uses all files for prediction and analysis
- `pages/Susceptibility Predictor.py` - Uses model files and EarthquakeFeatures.csv

## File Sources

Files are copied from the original `Susceptability_pred_ML/Susceptability_pred_ML/` directory to maintain the expected directory structure.

## Troubleshooting

If you encounter "Files not found" errors:
1. Ensure all files listed above are present in this directory
2. Check file permissions (should be readable)
3. Verify file integrity (not corrupted)

For missing files, copy them from the original source directory:
```bash
cp ../Susceptability_pred_ML/Susceptability_pred_ML/[filename] .
```