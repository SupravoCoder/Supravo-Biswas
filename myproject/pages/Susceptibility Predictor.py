import pandas as pd
import numpy as np
import joblib
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

# Directory where files will be saved
MODELS_DIR = r"C:\Users\Supravo Biswas\Desktop\Coding\Python Coding\StreamlitPython\Susceptability_pred_ML"

# Create directory if it doesn't exist
os.makedirs(MODELS_DIR, exist_ok=True)

print("🔄 Generating earthquake prediction files...")

# Set random seed for reproducibility
np.random.seed(42)

# -----------------------------
# Generate Mock Earthquake Dataset
# -----------------------------
print("📊 Creating earthquake dataset...")

n_samples = 5000  # Number of earthquake records

# Generate realistic earthquake data for Indian subcontinent
lats = np.random.uniform(8.0, 37.0, n_samples)  # India latitude range
longs = np.random.uniform(68.0, 97.0, n_samples)  # India longitude range
mags = np.random.lognormal(mean=1.2, sigma=0.8, size=n_samples)  # More realistic magnitude distribution
mags = np.clip(mags, 1.0, 9.0)  # Clip to realistic range

# Generate hub distances (distance to nearest fault)
hub_dists = np.random.exponential(scale=30, size=n_samples)  # Exponential distribution
hub_dists = np.clip(hub_dists, 0.1, 300.0)

# Generate fault densities
fault_densities = np.random.beta(a=2, b=8, size=n_samples) * 0.5  # Beta distribution for fault density

# Generate other features
depths = np.random.lognormal(mean=2.5, sigma=1.0, size=n_samples)  # Depth in km
depths = np.clip(depths, 1.0, 700.0)

years = np.random.randint(1900, 2024, n_samples)
months = np.random.randint(1, 13, n_samples)
days = np.random.randint(1, 29, n_samples)

# Create realistic fault hub names
fault_regions = [
    "Himalayan_Front", "Main_Central_Thrust", "Kopili_Fault", "Naga_Thrust", 
    "Dauki_Fault", "Godavari_Graben", "Koyna_Fault", "Cambay_Graben",
    "Delhi_Ridge", "Aravalli_Fault", "Son_Narmada_Fault", "Palghat_Gap",
    "Bhavnagar_Fault", "Kachchh_Mainland_Fault", "Allah_Bund_Fault",
    "Mahendragiri_Fault", "Eastern_Ghats_Fault", "Tan_Shear_Zone",
    "Moyar_Shear_Zone", "Cauvery_Shear_Zone"
]

hub_names = np.random.choice(fault_regions, n_samples)

# Create the earthquake features dataframe
df = pd.DataFrame({
    'LAT': lats,
    'LONG_': longs,
    'MAGMB': mags,
    'HubDist': hub_dists,
    'FaultDensity': fault_densities,
    'DEPTH_KM': depths,
    'YR': years,
    'MO': months,
    'DT': days,
    'HubName': hub_names
})

# Save the earthquake features CSV
csv_path = os.path.join(MODELS_DIR, "EarthquakeFeatures.csv")
df.to_csv(csv_path, index=False)
print(f"✅ Saved earthquake dataset: {csv_path}")

# -----------------------------
# Create and Train the Model
# -----------------------------
print("🤖 Training earthquake prediction model...")

# Create feature scalers
scaler_fd = StandardScaler()
scaler_hd = StandardScaler()
scaler_mag = StandardScaler()

# Fit scalers
scaler_fd.fit(fault_densities.reshape(-1, 1))
scaler_hd.fit(hub_dists.reshape(-1, 1))
scaler_mag.fit(mags.reshape(-1, 1))

# Create training features
X_train = []
y_train = []

# Define landslide-prone keywords for terrain penalty
landslide_prone_keywords = [
    "Joshimath", "Badrinath", "Kedarnath", "Chamoli", "Rudraprayag", "Pithoragarh", 
    "Almora", "Nainital", "Manali", "Kullu", "Chamba", "Dharamshala", "Kangra",
    "Gangtok", "Darjeeling", "Dehradun", "Mussoorie", "Rishikesh", "Haridwar", "Tehri"
]

for i in range(n_samples):
    mag = mags[i]
    hub_dist = hub_dists[i]
    fault_density = fault_densities[i]
    
    # Scale features
    fault_density_norm = scaler_fd.transform([[fault_density]])[0][0]
    has_fault_density = 1 if fault_density > 0.05 else 0
    terrain_penalty = np.random.randint(0, 2)  # Random terrain penalty for training
    
    X_train.append([mag, hub_dist, fault_density_norm, has_fault_density, terrain_penalty])
    
    # Create realistic target labels based on seismic risk factors
    risk_score = 0
    
    # Magnitude contribution (30% weight)
    if mag >= 7.0:
        risk_score += 3
    elif mag >= 5.0:
        risk_score += 2
    elif mag >= 3.0:
        risk_score += 1
    
    # Distance contribution (25% weight)
    if hub_dist <= 10:
        risk_score += 2.5
    elif hub_dist <= 50:
        risk_score += 1.5
    elif hub_dist <= 100:
        risk_score += 0.5
    
    # Fault density contribution (25% weight)
    if fault_density >= 0.3:
        risk_score += 2.5
    elif fault_density >= 0.1:
        risk_score += 1.5
    elif fault_density >= 0.05:
        risk_score += 0.5
    
    # Terrain penalty contribution (20% weight)
    if terrain_penalty == 1:
        risk_score += 2
    
    # Depth contribution (minor factor)
    if depths[i] <= 70:  # Shallow earthquakes are more dangerous
        risk_score += 0.5
    
    # Convert risk score to classification
    if risk_score >= 6:
        y_train.append(2)  # Unsafe
    elif risk_score >= 3:
        y_train.append(1)  # Moderate
    else:
        y_train.append(0)  # Safe

X_train = np.array(X_train)
y_train = np.array(y_train)

# Train the model
model = RandomForestClassifier(
    n_estimators=200,
    max_depth=10,
    min_samples_split=5,
    min_samples_leaf=2,
    random_state=42
)

model.fit(X_train, y_train)

# Print model performance
train_accuracy = model.score(X_train, y_train)
print(f"📈 Model training accuracy: {train_accuracy:.3f}")

# Print class distribution
unique, counts = np.unique(y_train, return_counts=True)
class_names = ['Safe', 'Moderate', 'Unsafe']
print("📊 Class distribution:")
for i, (cls, count) in enumerate(zip(unique, counts)):
    print(f"   {class_names[cls]}: {count} ({count/len(y_train)*100:.1f}%)")

# -----------------------------
# Save Models and Scalers
# -----------------------------
print("💾 Saving models and scalers...")

# Save the trained model
model_path = os.path.join(MODELS_DIR, "EarthquakePredictor.pkl")
joblib.dump(model, model_path)
print(f"✅ Saved model: {model_path}")

# Save scalers
scaler_fd_path = os.path.join(MODELS_DIR, "fault_density_scaler.pkl")
joblib.dump(scaler_fd, scaler_fd_path)
print(f"✅ Saved fault density scaler: {scaler_fd_path}")

scaler_hd_path = os.path.join(MODELS_DIR, "hubdist_scaler.pkl")
joblib.dump(scaler_hd, scaler_hd_path)
print(f"✅ Saved hub distance scaler: {scaler_hd_path}")

scaler_mag_path = os.path.join(MODELS_DIR, "mag_scaler.pkl")
joblib.dump(scaler_mag, scaler_mag_path)
print(f"✅ Saved magnitude scaler: {scaler_mag_path}")

# -----------------------------
# Verify Files
# -----------------------------
print("\n🔍 Verifying created files...")

required_files = [
    "EarthquakePredictor.pkl",
    "fault_density_scaler.pkl",
    "hubdist_scaler.pkl",
    "mag_scaler.pkl",
    "EarthquakeFeatures.csv"
]

all_files_exist = True
for filename in required_files:
    filepath = os.path.join(MODELS_DIR, filename)
    if os.path.exists(filepath):
        file_size = os.path.getsize(filepath)
        print(f"✅ {filename} - {file_size:,} bytes")
    else:
        print(f"❌ {filename} - Missing!")
        all_files_exist = False

if all_files_exist:
    print("\n🎉 All required files have been successfully created!")
    print(f"📁 Files location: {MODELS_DIR}")
    print("\n🚀 You can now run your Streamlit app!")
else:
    print("\n❌ Some files are missing. Please check for errors above.")

# -----------------------------
# Test the Model
# -----------------------------
print("\n🧪 Testing the model with sample data...")

# Test with a sample input
sample_input = np.array([[5.5, 25.0, 0.5, 1, 0]])  # mag, hub_dist, fault_density_norm, has_fault_density, terrain_penalty
prediction = model.predict(sample_input)[0]
probabilities = model.predict_proba(sample_input)[0]

class_names = ['Safe', 'Moderate', 'Unsafe']
print(f"📊 Sample prediction: {class_names[prediction]}")
print("🎯 Probabilities:")
for i, prob in enumerate(probabilities):
    print(f"   {class_names[i]}: {prob:.3f}")

print(f"\n✨ Setup complete! Your earthquake prediction system is ready to use.")
print(f"📝 Dataset contains {len(df)} earthquake records from {len(df['HubName'].unique())} fault systems.")
