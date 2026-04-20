import pandas as pd
import pytz
import time
import logging
from mt5linux import MetaTrader5 as mt5   # ← mt5linux client

class DataEngine:
    def __init__(self, account: int, password: str, server: str):
        self.account = account
        self.password = password
        self.server = server
        self.timezone = pytz.timezone("UTC")
        self.mt5 = None
        self.reconnect()

    def reconnect(self):
        if self.mt5 is None:
            self.mt5 = mt5(host="localhost", port=8001)  # RPyC port from Docker image
        
        if not self.mt5.initialize(login=self.account, password=self.password, server=self.server):
            raise ConnectionError(f"MT5 init failed: {self.mt5.last_error()}")
        logging.info("✅ MT5 connected successfully via mt5linux (localhost:8001)")

    def get_multi_tf_data(self, symbol: str, tf_list: list, bars: int = 500):
        self.mt5.symbol_select(symbol, True)
        data = {}
        for tf in tf_list:
            timeframe = getattr(mt5, f"TIMEFRAME_{tf}")
            rates = self.mt5.copy_rates_from_pos(symbol, timeframe, 0, bars)
            df = pd.DataFrame(rates)
            df["time"] = pd.to_datetime(df["time"], unit="s", utc=True)
            df.set_index("time", inplace=True)
            data[tf] = df
        return data

    def get_tick(self, symbol: str):
        return self.mt5.symbol_info_tick(symbol)