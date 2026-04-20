import MetaTrader5 as mt5

class RiskManager:
    def __init__(self):
        self.max_risk = 0.01
    
    def calculate_position_size(self, symbol: str, entry: float, sl: float, atr: float):
        account_info = mt5.account_info()
        risk_amount = account_info.equity * self.max_risk
        pip_value = mt5.symbol_info(symbol).trade_tick_value
        sl_distance = abs(entry - sl) / mt5.symbol_info(symbol).point
        lots = risk_amount / (sl_distance * pip_value * 10)
        return round(max(0.01, lots), 2)
    
    def get_atr_sl_tp(self, df: pd.DataFrame, is_long: bool):
        atr = df["atr"].iloc[-1]
        sl = atr * 1.5
        tp = atr * 3.0
        return sl, tp