import numpy as np
import pandas as pd 
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout
import joblib

class LSTMPredictor:
    def __init__(self, sequence_length=60):
        self.sequence_length = sequence_length
        # 22 features confirmed from FeatureEngineer output
        self.num_features = 22
        self.model = self._build_model()
    
    def _build_model(self):
        model = Sequential([
            LSTM(128, return_sequences=True, input_shape=(self.sequence_length, self.num_features)),
            Dropout(0.2),
            LSTM(64),
            Dropout(0.2),
            Dense(2, activation="softmax")  # [down_prob, up_prob]
        ])
        model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])
        return model
    
    def prepare_sequence(self, df: pd.DataFrame):
        # EXACT 22 predictive features (spread + all engineered)
        feature_cols = [
            "spread", "ema_8", "sma_8", "ema_13", "sma_13", "ema_21", "sma_21",
            "ema_34", "sma_34", "ema_55", "sma_55", "rsi",
            "MACD_12_26_9", "MACDh_12_26_9", "MACDs_12_26_9",
            "atr", "bb_width", "returns", "zscore_20", "adx",
            "higher_high", "lower_low"
        ]
        # Safety guard (in case of future feature changes)
        available_cols = [col for col in feature_cols if col in df.columns]
        if len(available_cols) != self.num_features:
            raise ValueError(f"Feature mismatch: expected {self.num_features}, got {len(available_cols)}")
        
        data = df[available_cols].values[-self.sequence_length:]
        if len(data) < self.sequence_length:
            raise ValueError(f"Insufficient history: need {self.sequence_length} bars, have {len(data)}")
        
        return np.expand_dims(data, axis=0)  # (1, seq_len, 22)
    
    def predict(self, sequence):
        probs = self.model.predict(sequence, verbose=0)[0]
        return {"up_prob": float(probs[1]), "down_prob": float(probs[0])}