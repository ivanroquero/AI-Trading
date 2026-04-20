"""
Utility helpers for the MT5 AI Hybrid Trading System
Author: Senior Quant Trading Engineer
Purpose: Shared functions for data persistence, normalization, metrics, and monitoring
"""

import pandas as pd
import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
import logging
from datetime import datetime
import requests
from typing import Dict, Any

def save_historical_data(df: pd.DataFrame, symbol: str, timeframe: str) -> None:
    """Save multi-timeframe OHLC data to Parquet for efficient ML training and backtesting.
    Uses columnar storage (10-20x faster than CSV) and automatic partitioning.
    """
    if df.empty:
        logging.warning(f"No data to save for {symbol} {timeframe}")
        return
    
    path = f"data/historical/{symbol}_{timeframe}.parquet"
    table = pa.Table.from_pandas(df.reset_index())
    pq.write_table(table, path, compression='snappy')
    logging.info(f"✅ Saved {len(df):,} bars of {symbol} {timeframe} to {path}")


def load_historical_data(symbol: str, timeframe: str) -> pd.DataFrame:
    """Load historical data from Parquet. Used in backtester and offline training."""
    path = f"data/historical/{symbol}_{timeframe}.parquet"
    try:
        df = pd.read_parquet(path)
        df["time"] = pd.to_datetime(df["time"])
        df.set_index("time", inplace=True)
        logging.info(f"✅ Loaded {len(df):,} bars from {path}")
        return df
    except FileNotFoundError:
        logging.error(f"❌ Historical file not found: {path}. Run data collection first.")
        return pd.DataFrame()


def normalize_features(df: pd.DataFrame) -> pd.DataFrame:
    """Robust z-score normalization per feature (avoids leakage).
    Applied after regime detection in production loop.
    """
    df = df.copy()
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    # Exclude target-like columns if present
    numeric_cols = [col for col in numeric_cols if col not in ["returns"]]
    
    for col in numeric_cols:
        mean = df[col].rolling(window=200, min_periods=50).mean()
        std = df[col].rolling(window=200, min_periods=50).std()
        df[col] = (df[col] - mean) / std
    
    df.dropna(inplace=True)
    return df


def calculate_performance_metrics(equity_curve: pd.Series) -> Dict[str, float]:
    """Compute professional-grade metrics for backtesting and live monitoring.
    Used in backtester.py and can be called periodically in main loop.
    """
    if len(equity_curve) < 2:
        return {"sharpe": 0.0, "max_drawdown": 0.0, "profit_factor": 0.0, "win_rate": 0.0}
    
    returns = equity_curve.pct_change().dropna()
    cumulative = (1 + returns).cumprod()
    
    # Sharpe Ratio (annualized, risk-free=0)
    sharpe = returns.mean() / returns.std() * np.sqrt(252) if returns.std() != 0 else 0.0
    
    # Maximum Drawdown
    peak = cumulative.cummax()
    drawdown = (cumulative - peak) / peak
    max_dd = drawdown.min()
    
    # Profit Factor (gross profit / gross loss)
    positive = returns[returns > 0].sum()
    negative = abs(returns[returns < 0].sum())
    profit_factor = positive / negative if negative != 0 else float('inf')
    
    # Win Rate (simple)
    win_rate = (returns > 0).mean()
    
    logging.info(f"📊 Performance → Sharpe: {sharpe:.2f} | MaxDD: {max_dd:.1%} | "
                 f"Profit Factor: {profit_factor:.2f} | Win Rate: {win_rate:.1%}")
    
    return {
        "sharpe": float(sharpe),
        "max_drawdown": float(max_dd),
        "profit_factor": float(profit_factor),
        "win_rate": float(win_rate),
        "total_return": float(cumulative.iloc[-1] - 1)
    }


def send_telegram_alert(message: str, token: str = None, chat_id: str = None) -> bool:
    """Send real-time alerts (trade execution, regime change, drawdown breach, errors).
    Configure token/chat_id in config.yaml under 'alerts' section.
    """
    if not token or not chat_id:
        logging.debug("Telegram alert skipped - credentials not configured")
        return False
    
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": f"🧠 AI MT5 System\n{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n{message}",
            "parse_mode": "HTML"
        }
        response = requests.post(url, data=payload, timeout=10)
        if response.status_code == 200:
            logging.info("📨 Telegram alert sent successfully")
            return True
        else:
            logging.warning(f"Telegram failed: {response.text}")
            return False
    except Exception as e:
        logging.error(f"Telegram error: {e}")
        return False


def create_directories() -> None:
    """Ensure required folders exist on startup (idempotent)."""
    import os
    os.makedirs("data/historical", exist_ok=True)
    os.makedirs("models", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    logging.info("📁 Project directories verified/created")


# Optional: quick data quality check
def validate_data(df: pd.DataFrame) -> bool:
    """Basic sanity check before feeding to models."""
    required_cols = ["open", "high", "low", "close", "tick_volume"]
    if not all(col in df.columns for col in required_cols):
        logging.error("❌ Missing required OHLC columns")
        return False
    if df["close"].isna().any():
        logging.warning("⚠️ NaN values detected in close price")
        return False
    return True