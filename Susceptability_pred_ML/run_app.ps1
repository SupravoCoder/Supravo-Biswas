# Earthquake Susceptibility Predictor - PowerShell Script
Write-Host "======================================" -ForegroundColor Green
Write-Host " Earthquake Susceptibility Predictor" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green
Write-Host ""

# Change to script directory
Set-Location -Path $PSScriptRoot

Write-Host "Step 1: Checking virtual environment..." -ForegroundColor Yellow
if (Test-Path ".venv\Scripts\python.exe") {
    Write-Host "✅ Virtual environment found!" -ForegroundColor Green
} else {
    Write-Host "❌ Virtual environment not found. Please run the setup first." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Step 2: Checking model files..." -ForegroundColor Yellow
$requiredFiles = @(
    "EarthquakePredictor.pkl",
    "fault_density_scaler.pkl", 
    "hubdist_scaler.pkl",
    "mag_scaler.pkl",
    "EarthquakeFeatures.csv"
)

$missingFiles = @()
foreach ($file in $requiredFiles) {
    if (-not (Test-Path $file)) {
        $missingFiles += $file
    }
}

if ($missingFiles.Count -gt 0) {
    Write-Host "❌ Missing required files:" -ForegroundColor Red
    foreach ($file in $missingFiles) {
        Write-Host "   - $file" -ForegroundColor Red
    }
    Write-Host ""
    Write-Host "Please run all notebook cells first to generate these files." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "✅ All required files found!" -ForegroundColor Green
Write-Host ""

Write-Host "Step 3: Starting Streamlit app..." -ForegroundColor Yellow
Write-Host "Opening in browser at: http://localhost:8501" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the app." -ForegroundColor Yellow
Write-Host ""

try {
    & ".venv\Scripts\python.exe" -m streamlit run streamlit_app.py
} catch {
    Write-Host "❌ Error starting Streamlit app: $_" -ForegroundColor Red
    Read-Host "Press Enter to exit"
}
