#!/usr/bin/env python3
"""
RPyC Server for mt5linux (runs inside Wine Python)
Exposes the full MetaTrader5 API to the client on port 8001.
"""
import rpyc
from rpyc.utils.server import ThreadedServer
from MetaTrader5 import MetaTrader5
import logging
import time

class MT5Service(rpyc.Service):
    def on_connect(self, conn):
        logging.info("🔌 Client connected to MT5 RPyC server")
        self.mt5_instance = MetaTrader5()

    def on_disconnect(self, conn):
        logging.info("🔌 Client disconnected")
        if hasattr(self, 'mt5_instance'):
            self.mt5_instance.shutdown()

    # Expose all methods used by your DataEngine + ExecutionEngine
    def exposed_initialize(self, login=None, password=None, server=None):
        return self.mt5_instance.initialize(login=login, password=password, server=server)

    def exposed_shutdown(self):
        return self.mt5_instance.shutdown()

    def exposed_symbol_select(self, symbol, enable):
        return self.mt5_instance.symbol_select(symbol, enable)

    def exposed_copy_rates_from_pos(self, symbol, timeframe, start_pos, count):
        return self.mt5_instance.copy_rates_from_pos(symbol, timeframe, start_pos, count)

    def exposed_order_send(self, request):
        return self.mt5_instance.order_send(request)

    def exposed_account_info(self):
        return self.mt5_instance.account_info()

    def exposed_symbol_info(self, symbol):
        return self.mt5_instance.symbol_info(symbol)

    def exposed_symbol_info_tick(self, symbol):
        return self.mt5_instance.symbol_info_tick(symbol)

    def exposed_last_error(self):
        return self.mt5_instance.last_error()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info("🚀 Starting RPyC MT5 Server on port 8001 (Wine Python)")
    server = ThreadedServer(
        MT5Service,
        port=8001,
        protocol_config={"allow_public_attrs": True, "allow_pickle": True}
    )
    server.start()