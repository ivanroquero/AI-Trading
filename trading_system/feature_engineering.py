import pandas as pd
import pandas_ta as ta
import numpy as np

class FeatureEngineer:
    def generate_features(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        
        # Moving averages
        for w in [8, 13, 21, 34, 55]:
            df[f"ema_{w}"] = ta.ema(df["close"], length=w)
            df[f"sma_{w}"] = ta.sma(df["close"], length=w)
        
        # Oscillators
        df["rsi"] = ta.rsi(df["close"], length=14)
        macd = ta.macd(df["close"], fast=12, slow=26, signal=9)
        df = pd.concat([df, macd], axis=1)
        
        # Volatility
        df["atr"] = ta.atr(df["high"], df["low"], df["close"], length=14)
        bb = ta.bbands(df["close"], length=20)
        df["bb_width"] = bb["BBU_20_2.0"] - bb["BBL_20_2.0"]
        
        # Momentum & statistics
        df["returns"] = df["close"].pct_change()
        df["zscore_20"] = (df["close"] - df["close"].rolling(20).mean()) / df["close"].rolling(20).std()
        df["adx"] = ta.adx(df["high"], df["low"], df["close"])["ADX_14"]
        
        # Price action
        df["higher_high"] = (df["high"] > df["high"].shift(1)).astype(int)
        df["lower_low"] = (df["low"] < df["low"].shift(1)).astype(int)
        
        df.dropna(inplace=True)
        return df