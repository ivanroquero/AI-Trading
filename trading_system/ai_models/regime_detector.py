import pandas as pd
import pandas_ta as ta

class RegimeDetector:
    def detect(self, df: pd.DataFrame) -> str:
        if len(df) < 100:
            return "HIGH_VOLATILITY"
        
        atr_ratio = df["atr"].iloc[-1] / df["atr"].rolling(100).mean().iloc[-1]
        adx = df["adx"].iloc[-1]
        
        if adx > 25 and atr_ratio < 1.5:
            return "TRENDING"
        elif adx < 20:
            return "RANGING"
        else:
            return "HIGH_VOLATILITY"