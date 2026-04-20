import numpy as np
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout
import joblib

class LSTMPredictor:
    def __init__(self, sequence_length=60):
        self.sequence_length = sequence_length
        self.model = self._build_model()
        # In production: self.model = load_model("models/lstm_predictor.h5")
    
    def _build_model(self):
        model = Sequential([
            LSTM(128, return_sequences=True, input_shape=(self.sequence_length, 20)),
            Dropout(0.2),
            LSTM(64),
            Dropout(0.2),
            Dense(2, activation="softmax")  # [down_prob, up_prob]
        ])
        model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])
        return model
    
    def prepare_sequence(self, df: pd.DataFrame):
        # Select 20 key features (adjust as needed)
        feature_cols = [col for col in df.columns if col not in ["time", "open", "high", "low", "close", "tick_volume", "real_volume"]]
        data = df[feature_cols].values[-self.sequence_length:]
        return np.expand_dims(data, axis=0)  # (1, seq_len, features)
    
    def predict(self, sequence):
        probs = self.model.predict(sequence, verbose=0)[0]
        return {"up_prob": float(probs[1]), "down_prob": float(probs[0])}