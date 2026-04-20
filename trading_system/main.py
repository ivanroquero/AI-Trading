import yaml
import time
import logging
from datetime import datetime
from data_layer import DataEngine
from feature_engineering import FeatureEngineer
from ai_models.regime_detector import RegimeDetector
from ai_models.ensemble import HybridPredictor
from risk_manager import RiskManager
from execution_engine import ExecutionEngine
from utils.logger import setup_logger
from utils.helpers import create_directories
create_directories()

class TradingSystem:
    def __init__(self):
        setup_logger()
        logging.info("=== AI Hybrid MT5 Trading System Started ===")
        
        with open("config.yaml", "r") as f:
            self.config = yaml.safe_load(f)
        
        # Initialize components
        self.data = DataEngine(account=12345678, password="your_password", server="your_broker_server")
        self.features = FeatureEngineer()
        self.regime_detector = RegimeDetector()
        self.predictor = HybridPredictor()
        self.risk = RiskManager()
        self.execution = ExecutionEngine()
        
        self.symbol = self.config["trading"]["symbol"]
        self.current_regime = None
        self.loss_streak = 0

    def run(self):
        while True:
            try:
                # 1. Fetch multi-timeframe data
                data_dict = self.data.get_multi_tf_data(self.symbol, 
                    tf_list=["M5", "M15", "H1"], bars=500)
                
                df_m5 = data_dict["M5"]
                df_h1 = data_dict["H1"]
                
                # 2. Features
                features_m5 = self.features.generate_features(df_m5)
                features_h1 = self.features.generate_features(df_h1)
                
                # 3. Regime detection (on H1)
                self.current_regime = self.regime_detector.detect(features_h1)
                logging.info(f"Market regime: {self.current_regime}")
                
                if self.current_regime == "HIGH_VOLATILITY":
                    time.sleep(60)
                    continue
                
                # 4. AI Prediction (on M5)
                prediction = self.predictor.predict(features_m5)
                
                if prediction["confidence"] < self.config["trading"]["confidence_threshold"]:
                    time.sleep(5)
                    continue
                
                # 5. Risk & position sizing
                entry_price = df_m5["close"].iloc[-1]
                sl, tp = self.risk.get_atr_sl_tp(features_m5, prediction["up_prob"] > 0.5)
                lots = self.risk.calculate_position_size(
                    self.symbol, entry_price, sl, features_m5["atr"].iloc[-1]
                )
                
                # 6. Execute
                direction = "BUY" if prediction["up_prob"] > 0.5 else "SELL"
                success = self.execution.place_trade(self.symbol, direction, lots, sl, tp)
                
                if success:
                    logging.info(f"TRADE EXECUTED: {direction} {lots} lots | Confidence: {prediction['confidence']:.2f}")
                else:
                    logging.warning("Trade skipped due to spread/slippage")
                
                time.sleep(5)  # 5-second heartbeat
                
            except Exception as e:
                logging.error(f"Critical error: {e}. Reconnecting in 10s...")
                time.sleep(10)
                self.data.reconnect()

if __name__ == "__main__":
    system = TradingSystem()
    system.run()