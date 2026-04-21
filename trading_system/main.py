import yaml
import time
import logging
from datetime import datetime
import os

from data_layer import DataEngine
from feature_engineering import FeatureEngineer
from ai_models.regime_detector import RegimeDetector
from ai_models.ensemble import HybridPredictor
from risk_manager import RiskManager
from execution_engine import ExecutionEngine
from utils.logger import setup_logger
from utils.helpers import create_directories, send_telegram_alert, validate_data

create_directories()

class TradingSystem:
    def __init__(self):
        setup_logger()
        logging.info("=== AI Hybrid MT5 Trading System v2 Started ===")
        
        with open("config.yaml", "r") as f:
            self.config = yaml.safe_load(f)
        
        self.data = DataEngine(
            account=int(self.config["mt5"]["account"]),
            password=self.config["mt5"]["password"],
            server=self.config["mt5"]["server"]
        )
        
        self.features = FeatureEngineer()
        self.regime_detector = RegimeDetector()
        self.predictor = HybridPredictor()
        self.risk = RiskManager(self.data.mt5)
        self.execution = ExecutionEngine(self.data.mt5)
        
        self.symbol = self.config["trading"]["symbol"]
        self.current_regime = None
        self.loss_streak = 0

    def _get_direction(self, prediction, regime: str):
        up = prediction["up_prob"] > 0.5
        if regime == "TRENDING":
            # Trend-following
            return "BUY" if up else "SELL"
        elif regime == "RANGING":
            # Mean-reversion (reverse the signal)
            return "SELL" if up else "BUY"
        return "BUY" if up else "SELL"  # fallback

    def run(self):
        while True:
            try:
                data_dict = self.data.get_multi_tf_data(self.symbol, ["M5", "M15", "H1"], bars=500)
                df_m5 = data_dict["M5"]
                df_h1 = data_dict["H1"]
                
                if not validate_data(df_m5) or len(df_m5) < 200:
                    time.sleep(60)
                    continue
                
                features_m5 = self.features.generate_features(df_m5)
                if len(features_m5) < 100:
                    logging.warning("Insufficient bars after feature engineering")
                    time.sleep(60)
                    continue
                features_h1 = self.features.generate_features(df_h1)
                
                # Regime detection (H1)
                self.current_regime = self.regime_detector.detect(features_h1)
                logging.info(f"Market regime: {self.current_regime}")
                
                if self.current_regime == "HIGH_VOLATILITY":
                    send_telegram_alert(f"🚨 HIGH VOLATILITY detected on {self.symbol} – pausing", 
                                      self.config.get("alerts", {}).get("token"),
                                      self.config.get("alerts", {}).get("chat_id"))
                    time.sleep(60)
                    continue
                
                # AI Prediction
                prediction = self.predictor.predict(features_m5)
                
                if prediction["confidence"] < self.config["trading"]["confidence_threshold"]:
                    time.sleep(5)
                    continue
                
                # Regime-aware direction
                direction = self._get_direction(prediction, self.current_regime)
                
                # Risk & execution
                entry_price = df_m5["close"].iloc[-1]
                sl, tp = self.risk.get_atr_sl_tp(features_m5, prediction["up_prob"] > 0.5)
                lots = self.risk.calculate_position_size(self.symbol, entry_price, sl, features_m5["atr"].iloc[-1])
                
                success = self.execution.place_trade(self.symbol, direction, lots, sl, tp)
                
                if success:
                    msg = f"✅ TRADE EXECUTED: {direction} {lots} lots | Regime: {self.current_regime} | Conf: {prediction['confidence']:.2f}"
                    logging.info(msg)
                    send_telegram_alert(msg, self.config.get("alerts", {}).get("token"), self.config.get("alerts", {}).get("chat_id"))
                else:
                    logging.warning("Trade skipped due to spread/slippage")
                
                time.sleep(5)
                
            except Exception as e:
                err_msg = f"Critical error: {e}. Reconnecting..."
                logging.error(err_msg)
                send_telegram_alert(err_msg, self.config.get("alerts", {}).get("token"), self.config.get("alerts", {}).get("chat_id"))
                time.sleep(10)
                self.data.reconnect()

if __name__ == "__main__":
    system = TradingSystem()
    system.run()