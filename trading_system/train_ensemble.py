import pandas as pd
import numpy as np
import logging
import os
from utils.logger import setup_logger
from utils.helpers import load_historical_data, save_historical_data, normalize_features
from feature_engineering import FeatureEngineer
from ai_models.ensemble import HybridPredictor   # for LSTM class
from ai_models.lstm_predictor import LSTMPredictor
import joblib
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

setup_logger()

def train_ensemble(symbol: str = "EURUSD", timeframe: str = "M5", bars: int = 10000):
    logging.info("=== Starting Ensemble Training ===")
    os.makedirs("models", exist_ok=True)
    
    # 1. Load / collect data
    df = load_historical_data(symbol, timeframe)
    if df.empty:
        logging.error("No historical data – run data collection first")
        return
    
    # 2. Features + target (next bar direction)
    features = FeatureEngineer().generate_features(df)
    features = normalize_features(features)
    
    # Target: 1 = up, 0 = down (next close)
    features["target"] = (features["close"].shift(-1) > features["close"]).astype(int)
    features.dropna(inplace=True)
    
    X = features.drop(columns=["target", "open", "high", "low", "close", "time", "real_volume", "tick_volume"])
    y = features["target"]
    
    # 3. Train XGBoost (fast, robust)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
    xgb = XGBClassifier(n_estimators=300, max_depth=6, learning_rate=0.05, subsample=0.8, colsample_bytree=0.8, random_state=42)
    xgb.fit(X_train, y_train)
    joblib.dump(xgb, "models/xgb_ensemble.pkl")
    logging.info(f"✅ XGB trained – Test accuracy: {xgb.score(X_test, y_test):.1%}")
    
    # 4. Train LSTM (sequence model)
    lstm = LSTMPredictor(sequence_length=60)
    # Prepare sequences (simple implementation – you can expand with full DataGenerator)
    seqs = []
    labels = []
    for i in range(60, len(features)-1):
        seq = features.iloc[i-60:i]   # will be filtered inside prepare_sequence
        seqs.append(lstm.prepare_sequence(features.iloc[i-60:i])[0][0])  # drop batch dim
        labels.append(features["target"].iloc[i])
    
    seqs = np.array(seqs)
    labels = np.array(labels)
    # One-hot for categorical_crossentropy
    labels_onehot = np.eye(2)[labels]
    
    lstm.model.fit(seqs, labels_onehot, epochs=20, batch_size=64, validation_split=0.2, verbose=1)
    lstm.save()
    
    logging.info("🎉 Training completed – models saved to /models/")
    # Quick backtest metrics
    print("Run WalkForwardBacktester to evaluate!")

if __name__ == "__main__":
    train_ensemble()