from mt5linux import MetaTrader5 as mt5
import logging

class ExecutionEngine:
    def __init__(self, mt5_client):
        self.mt5 = mt5_client
        self.max_spread = 3.0
    
    def place_trade(self, symbol: str, direction: str, lots: float, sl: float, tp: float):
        tick = self.mt5.symbol_info_tick(symbol)
        spread = (tick.ask - tick.bid) / self.mt5.symbol_info(symbol).point
        
        if spread > self.max_spread:
            logging.warning(f"Spread too high: {spread:.1f} pips")
            return False
        
        price = tick.ask if direction == "BUY" else tick.bid
        order_type = self.mt5.ORDER_TYPE_BUY if direction == "BUY" else self.mt5.ORDER_TYPE_SELL
        
        request = {
            "action": self.mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lots,
            "type": order_type,
            "price": price,
            "sl": price - sl if direction == "BUY" else price + sl,
            "tp": price + tp if direction == "BUY" else price - tp,
            "deviation": 10,
            "magic": 987654,
            "comment": "AI_Hybrid_v1",
            "type_time": self.mt5.ORDER_TIME_GTC,
            "type_filling": self.mt5.ORDER_FILLING_IOC,
        }
        result = self.mt5.order_send(request)
        return result.retcode == self.mt5.TRADE_RETCODE_DONE