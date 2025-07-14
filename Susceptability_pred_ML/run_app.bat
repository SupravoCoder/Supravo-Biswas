@echo off
echo ======================================
echo  Earthquake Susceptibility Predictor
echo ======================================

echo.
echo Step 1: Activating virtual environment...
cd /d "%~dp0"

echo.
echo Step 2: Checking if model files exist...
if not exist "EarthquakePredictor.pkl" (
    echo WARNING: Model files not found!
    echo Please run the notebook cells first to train the model.
    echo.
    pause
    exit /b 1
)

echo ✅ Model files found!
echo.

echo Step 3: Starting Streamlit app...
echo Opening in browser at: http://localhost:8501
echo.
echo Press Ctrl+C to stop the app.
echo.

".venv\Scripts\python.exe" -m streamlit run streamlit_app.py

pause
