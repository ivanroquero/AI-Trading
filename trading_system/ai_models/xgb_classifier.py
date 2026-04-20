import xgboost as xgb
import joblib

class XGBClassifier:
    def __init__(self):
        self.model = joblib.load("models/xgb_ensemble.pkl")  # Train once offline
    
    def predict_proba(self, features):
        return self.model.predict_proba(features.reshape(1, -1))[0]