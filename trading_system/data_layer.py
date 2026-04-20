import MetaTrader5 as mt5
import pandas as pd
import pytz
import time
import logging

class DataEngine:
    def __init__(self, account: int, password: str, server: str):
        self.account = account
        self.password = password
        self.server = server
        self.timezone = pytz.timezone("UTC")
        self.reconnect()

    def reconnect(self):
        if not mt5.initialize(login=self.account, password=self.password, server=self.server):
            raise ConnectionError(f"MT5 init failed: {mt5.last_error()}")
        logging.info("MT5 connected successfully")

    def get_multi_tf_data(self, symbol: str, tf_list: list, bars: int = 500):
        mt5.symbol_select(symbol, True)
        data = {}
        for tf in tf_list:
            timeframe = getattr(mt5, f"TIMEFRAME_{tf}")
            rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, bars)
            df = pd.DataFrame(rates)
            df["time"] = pd.to_datetime(df["time"], unit="s", utc=True)
            df.set_index("time", inplace=True)
            data[tf] = df
        return data

    def get_tick(self, symbol: str):
        return mt5.symbol_info_tick(symbol)