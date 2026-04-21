import pandas as pd
import numpy as np

class FeatureEngineer:
    def generate_features(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        
        # Moving averages (exact match to original pandas_ta behavior)
        for w in [8, 13, 21, 34, 55]:
            df[f"ema_{w}"] = df["close"].ewm(span=w, adjust=False).mean()
            df[f"sma_{w}"] = df["close"].rolling(window=w).mean()
        
        # Oscillators
        df["rsi"] = self._rsi(df["close"], length=14)
        macd_df = self._macd(df["close"])
        df = pd.concat([df, macd_df], axis=1)
        
        # Volatility
        df["atr"] = self._atr(df["high"], df["low"], df["close"], length=14)
        bb_df = self._bbands(df["close"], length=20)
        df["bb_width"] = bb_df["BBU_20_2.0"] - bb_df["BBL_20_2.0"]
        
        # Momentum & statistics
        df["returns"] = df["close"].pct_change()
        df["zscore_20"] = (df["close"] - df["close"].rolling(20).mean()) / df["close"].rolling(20).std()
        
        # ADX (column name kept as "adx" for RegimeDetector compatibility)
        adx_df = self._adx(df["high"], df["low"], df["close"])
        df["adx"] = adx_df["ADX_14"]
        
        # Price action
        df["higher_high"] = (df["high"] > df["high"].shift(1)).astype(int)
        df["lower_low"] = (df["low"] < df["low"].shift(1)).astype(int)
        
        df.dropna(inplace=True)
        return df

    @staticmethod
    def _rsi(close: pd.Series, length: int = 14) -> pd.Series:
        delta = close.diff()
        gain = delta.where(delta > 0, 0).rolling(window=length).mean()
        loss = -delta.where(delta < 0, 0).rolling(window=length).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    @staticmethod
    def _macd(close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
        ema_fast = close.ewm(span=fast, adjust=False).mean()
        ema_slow = close.ewm(span=slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        return pd.DataFrame({
            f"MACD_{fast}_{slow}_{signal}": macd_line,
            f"MACDh_{fast}_{slow}_{signal}": histogram,
            f"MACDs_{fast}_{slow}_{signal}": signal_line
        })

    @staticmethod
    def _atr(high: pd.Series, low: pd.Series, close: pd.Series, length: int = 14) -> pd.Series:
        tr0 = high - low
        tr1 = (high - close.shift()).abs()
        tr2 = (low - close.shift()).abs()
        tr = pd.concat([tr0, tr1, tr2], axis=1).max(axis=1)
        return tr.ewm(alpha=1/length, adjust=False).mean()

    @staticmethod
    def _bbands(close: pd.Series, length: int = 20, std: float = 2.0):
        sma = close.rolling(window=length).mean()
        std_dev = close.rolling(window=length).std()
        return pd.DataFrame({
            "BBU_20_2.0": sma + std * std_dev,
            "BBL_20_2.0": sma - std * std_dev
        })

    @staticmethod
    def _adx(high: pd.Series, low: pd.Series, close: pd.Series, length: int = 14):
        tr = pd.concat([
            high - low,
            (high - close.shift()).abs(),
            (low - close.shift()).abs()
        ], axis=1).max(axis=1)
        
        up = high - high.shift()
        down = low.shift() - low
        plus_dm = pd.Series(np.where((up > down) & (up > 0), up, 0), index=high.index)
        minus_dm = pd.Series(np.where((down > up) & (down > 0), down, 0), index=high.index)
        
        tr14 = tr.ewm(alpha=1/length, adjust=False).mean()
        plus_di = 100 * plus_dm.ewm(alpha=1/length, adjust=False).mean() / tr14
        minus_di = 100 * minus_dm.ewm(alpha=1/length, adjust=False).mean() / tr14
        
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.ewm(alpha=1/length, adjust=False).mean()
        
        return pd.DataFrame({"ADX_14": adx})