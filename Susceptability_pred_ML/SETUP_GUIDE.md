# 🔧 Setup and Installation Guide

## ✅ Problem Solved!

The error you encountered was due to using a system Python installation that wasn't properly configured. I've now set up a **virtual environment** specifically for your project.

## 🚀 Current Setup Status

### ✅ Completed:
- **Virtual Environment**: Created at `.venv/`
- **Python Version**: 3.12.10
- **All Packages Installed**: streamlit, pandas, numpy, scikit-learn, joblib, geopy, plotly, matplotlib, seaborn
- **Scripts Created**: `run_app.bat` and `run_app.ps1` for easy execution

## 📋 How to Run the Project

### Method 1: Use the Batch File (Recommended)
```cmd
run_app.bat
```

### Method 2: Use PowerShell Script
```powershell
.\run_app.ps1
```

### Method 3: Manual Command
```powershell
& ".venv\Scripts\python.exe" -m streamlit run streamlit_app.py
```

## 🧪 Before Running the App

**IMPORTANT**: You must first run the notebook to train the model:

1. **Open** `Susceptibility.ipynb` in VS Code
2. **Run all cells** in sequence (Ctrl+Enter for each cell)
3. **Wait** for all cells to complete execution
4. **Verify** that these files are created:
   - `EarthquakePredictor.pkl`
   - `fault_density_scaler.pkl`
   - `hubdist_scaler.pkl`
   - `mag_scaler.pkl`
   - `earthquakes_labeled.csv`

## 🔍 Troubleshooting

### If you get permission errors with PowerShell:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### If packages are missing:
```powershell
& ".venv\Scripts\python.exe" -m pip install -r requirements.txt
```

### If the virtual environment is corrupted:
1. Delete the `.venv` folder
2. Run: `python -m venv .venv`
3. Activate: `.venv\Scripts\activate`
4. Install: `pip install -r requirements.txt`

## 🎯 Quick Start Commands

```powershell
# 1. Navigate to project directory
cd "c:\Users\Supravo\Documents\Susceptability_pred_ML[1]\Susceptability_pred_ML"

# 2. Run the application
.\run_app.ps1
```

## 🌟 What's Fixed

- **Virtual Environment**: Isolated Python environment prevents conflicts
- **Proper Paths**: Using correct Python executable paths
- **All Dependencies**: All required packages are installed and verified
- **Easy Execution**: Simple scripts to run the application
- **Error Checking**: Scripts verify all files exist before running

Your project is now ready to run! 🎉
