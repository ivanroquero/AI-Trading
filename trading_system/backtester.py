import pandas as pd
import numpy as np
from feature_engineering import FeatureEngineer
from ai_models.ensemble import HybridPredictor
from utils.helpers import load_historical_data, calculate_performance_metrics

class WalkForwardBacktester:
    def run(self, symbol: str = "EURUSD", timeframe: str = "M5"):
        historical_df = load_historical_data(symbol, timeframe)
        if historical_df.empty:
            print("No historical data – train or collect first")
            return
        
        features = FeatureEngineer().generate_features(historical_df)
        predictor = HybridPredictor()
        
        signals = []
        for i in range(60, len(features)):
            window = features.iloc[i-60:i]
            pred = predictor.predict(window)
            if pred["confidence"] > 0.70:
                signals.append(1 if pred["up_prob"] > 0.5 else -1)
            else:
                signals.append(0)
        
        returns = historical_df["close"].pct_change().iloc[60:].values
        strategy_returns = np.array(signals) * returns
        
        metrics = calculate_performance_metrics(pd.Series(np.cumsum(strategy_returns)))
        print(f"Walk-Forward Results → Win Rate: {metrics['win_rate']:.1%} | "
              f"Sharpe: {metrics['sharpe']:.2f} | Max DD: {metrics['max_drawdown']:.1%} | "
              f"Profit Factor: {metrics['profit_factor']:.2f}")

if __name__ == "__main__":
    WalkForwardBacktester().run()