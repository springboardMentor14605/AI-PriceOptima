import joblib
import os

FEATURES_PATH = "models/feature_names.joblib"
if os.path.exists(FEATURES_PATH):
    features = joblib.load(FEATURES_PATH)
    print(features)
else:
    print("Feature names not found.")
