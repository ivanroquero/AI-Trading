import numpy as np
import joblib
import logging

class XGBClassifier:
    def __init__(self):
        try:
            self.model = joblib.load("models/xgb_ensemble.pkl")
            logging.info("✅ Loaded pre-trained XGB model")
        except FileNotFoundError:
            logging.warning("⚠️ XGB model not found — using DUMMY predictor (safe demo mode)")
            self.model = None
    
    def predict_proba(self, features):
        if self.model is None:
            return np.array([0.45, 0.55])  # slight bias, never triggers low-confidence trades
        return self.model.predict_proba(features.reshape(1, -1))[0]