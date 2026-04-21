import numpy as np
import pandas as pd  # ← ADDED: required for type hint
from ai_models.lstm_predictor import LSTMPredictor
from ai_models.xgb_classifier import XGBClassifier

class HybridPredictor:
    def __init__(self):
        self.lstm = LSTMPredictor()
        self.xgb = XGBClassifier()
        self.conf_threshold = 0.70

    def predict(self, df_m5: pd.DataFrame):
        # LSTM sequence (now guaranteed 22 features)
        seq = self.lstm.prepare_sequence(df_m5)
        lstm_probs = self.lstm.predict(seq)
        
        # XGBoost on last row + LSTM output (dummy-safe)
        xgb_input = np.hstack([
            df_m5.iloc[-1].values,
            [lstm_probs["up_prob"], lstm_probs["down_prob"]]
        ])
        xgb_probs = self.xgb.predict_proba(xgb_input)
        
        # Weighted ensemble (60% LSTM + 40% XGB)
        final_up = 0.6 * lstm_probs["up_prob"] + 0.4 * xgb_probs[1]
        confidence = abs(final_up - 0.5) * 2

        return {
            "up_prob": final_up,
            "down_prob": 1 - final_up,
            "confidence": confidence
        }