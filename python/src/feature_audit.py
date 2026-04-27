import pandas as pd
import numpy as np
import os
from sklearn.feature_selection import mutual_info_classif

def get_feature_explanation(name):
    """Provides a human-readable description for technical features."""
    name_upper = name.upper()
    
    # Mapping Logic
    definitions = {
        "RSI": "Relative Strength Index: Momentum oscillator measuring the speed and change of price movements.",
        "MACD": "Moving Average Convergence Divergence: Trend-following momentum indicator showing the relationship between two EMAs.",
        "STOCH": "Stochastic Oscillator: Momentum indicator comparing a specific closing price to a range of its prices over time.",
        "ATR": "Average True Range: Volatility indicator showing how much an asset moves, on average, over a given timeframe.",
        "BBP": "Bollinger Band Percentage: Indicates where the current price is relative to the Bollinger Bands (Volatility).",
        "ADX": "Average Directional Index: Measures the overall strength of a trend (0-100).",
        "EMA": "Exponential Moving Average: A type of moving average that places a greater weight and significance on the most recent data points.",
        "CCI": "Commodity Channel Index: Used to identify cyclical trends and overbought/oversold levels.",
        "OBV": "On-Balance Volume: A momentum indicator that uses volume flow to predict changes in price.",
        "GEOM": "Price Action Geometry: Custom calculation measuring candle wick-to-body ratios and physical bar shape.",
        "STAT": "Statistical Derivative: Measures standard deviation or z-score of price relative to its recent mean.",
        "TIME": "Temporal Feature: Encodes the hour of day or day of week to capture market session cyclicality."
    }
    
    for key, desc in definitions.items():
        if key in name_upper:
            return desc
    return "Technical derivative used for identifying market patterns and trend exhaustion."

def run_feature_audit(input_csv, output_dictionary_csv):
    """Tests features for predictive power and generates documentation."""
    if not os.path.exists(input_csv):
        print(f"Error: {input_csv} not found. Run the feature_factory.py first.")
        return

    print(f"Starting Audit on {input_csv}...")
    df = pd.read_csv(input_csv, index_col=0)
    
    # 1. Ensure we have a Target for testing (Price direction 5 bars ahead)
    if 'target' not in df.columns:
        df['target'] = (df['close'].shift(-5) > df['close']).astype(int)
    
    # Clean data for statistical test
    df_clean = df.dropna().copy()
    
    if df_clean.empty:
        print("Audit Warning: Dataset is empty after dropna. Using dictionary mapping only.")
        X = df.drop(columns=['target'], errors='ignore')
        scores = [0.0] * len(X.columns)
    else:
        X = df_clean.drop(columns=['target'], errors='ignore')
        y = df_clean['target']
        print(f"Testing {len(X.columns)} features for Predictive Power...")
        # Mutual Information measures how much info a feature provides about the target
        scores = mutual_info_classif(X, y, random_state=42)

    # 2. Build the Audit/Dictionary Report
    audit_data = []
    for i, col in enumerate(X.columns):
        audit_data.append({
            "Feature Name": col,
            "Predictive Score": round(scores[i], 5),
            "Explanation": get_feature_explanation(col)
        })

    audit_df = pd.DataFrame(audit_data).sort_values(by="Predictive Score", ascending=False)
    
    # 3. Save the Report
    audit_df.to_csv(output_dictionary_csv, index=False)
    
    print("-" * 30)
    print(f"AUDIT COMPLETE")
    print(f"Dictionary saved to: {output_dictionary_csv}")
    print("-" * 30)
    print("TOP 5 PREDICTORS DISCOVERED:")
    print(audit_df.head(5)[["Feature Name", "Predictive Score"]])

if __name__ == "__main__":
    # Point this to your 'Massive' output file
    target_file = "python/data/features_added/COMP_FE_EURUSD_2022_5M.csv"
    dict_output = "python/data/feature_dictionary_explained.csv"
    
    run_feature_audit(target_file, dict_output)