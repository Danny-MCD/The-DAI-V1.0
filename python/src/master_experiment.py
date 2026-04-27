import pandas as pd
import numpy as np
from sklearn.feature_selection import mutual_info_classif
import matplotlib.pyplot as plt
import os

def run_multi_experiment(input_file, configs):
    """
    Runs multiple feature audits based on different TP/SL targets.
    configs: List of dicts e.g., [{'tp': 5, 'sl': 3, 'name': 'scalp'}, ...]
    """
    df_base = pd.read_csv(input_file, index_col='time', parse_dates=True)
    all_results = []

    for cfg in configs:
        tp, sl, label = cfg['tp'], cfg['sl'], cfg['name']
        print(f"\n>>> Running Experiment: {label.upper()} ({tp} Pips TP)")
        
        # 1. Dynamic Labeling (Simulated for speed during audit)
        # In a full run, this mimics the triple barrier logic
        target_name = f"target_{label}"
        close = df_base['close'].values
        labels = np.zeros(len(close))
        
        # Simple high-speed labeling for MI testing
        pt_val = tp * 0.0001 # Converting pips to decimal
        for i in range(len(close) - 10):
            future_pct = (close[i+1:i+11] - close[i]) / close[i]
            if np.any(future_pct >= pt_val): labels[i] = 1
        
        # 2. Mutual Information
        X = df_base.drop(columns=['target'], errors='ignore')
        if 'volume' not in X.columns and 'tick_volume' in X.columns:
            X.rename(columns={'tick_volume': 'volume'}, inplace=True)
            
        scores = mutual_info_classif(X, labels, random_state=42)
        
        # 3. Store Results
        for i, col in enumerate(X.columns):
            all_results.append({
                "Feature": col,
                "Score": round(scores[i], 5),
                "Experiment": f"{tp} Pips ({label})"
            })
            
    # 4. Save Master CSV
    results_df = pd.DataFrame(all_results)
    os.makedirs("python/data/experiments", exist_ok=True)
    results_df.to_csv("python/data/experiments/master_comparison_results.csv", index=False)
    
    # 5. Generate Comparison Visual
    create_comparison_chart(results_df)

def create_comparison_chart(df):
    """Draws a grouped bar chart comparing top features across settings."""
    # Select top 8 features from the first experiment to keep the chart readable
    top_features = df.groupby("Feature")["Score"].mean().sort_values(ascending=False).head(8).index
    plot_df = df[df['Feature'].isin(top_features)]
    
    pivot_df = plot_df.pivot(index="Feature", columns="Experiment", values="Score")
    
    plt.figure(figsize=(12, 6))
    pivot_df.plot(kind='bar', ax=plt.gca())
    plt.title("Feature Predictive Power vs. Profit Targets (3M Timeframe)")
    plt.ylabel("Mutual Information Score")
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    os.makedirs("python/data/visuals", exist_ok=True)
    plt.savefig("python/data/visuals/feature_comparison.png")
    print("\n[SUCCESS] Comparison chart saved to: python/data/visuals/feature_comparison.png")

if __name__ == "__main__":
    # DEFINE YOUR EXPERIMENTS HERE
    my_configs = [
        {'tp': 5, 'sl': 3, 'name': 'scalp'},      # Current baseline
        {'tp': 10, 'sl': 5, 'name': 'mid_range'}, # Double the target
        {'tp': 20, 'sl': 10, 'name': 'trend'}     # Long-range intraday
    ]
    
    input_csv = "python/data/features_added/EURUSD_2022_3M_ENRICHED.csv"
    run_multi_experiment(input_csv, my_configs)