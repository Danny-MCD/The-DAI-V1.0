import pandas as pd
import json
import os
from sklearn.feature_selection import mutual_info_classif
import matplotlib.pyplot as plt

def run_final_master_audit():
    with open("python/config/baseline_3m.json", 'r') as f:
        cfg = json.load(f)
    
    master_file = f"{cfg['paths']['labeled']}MASTER_EURUSD_3M_2022_2025.csv"
    print(f"Loading Master Dataset: {master_file}")
    df = pd.read_csv(master_file, index_col='time', parse_dates=True)
    
    # 1. Clean for analysis
    X = df.drop(columns=['target'])
    y = df['target']
    
    print("Calculating final predictive scores across 4 years of data...")
    # This may take 2-3 minutes due to the 500k row size
    importances = mutual_info_classif(X, y, random_state=42)
    
    # 2. Organize Results
    feature_scores = pd.Series(importances, index=X.columns).sort_values(ascending=False)
    
    # 3. Save Report
    os.makedirs("python/experiments/results/", exist_ok=True)
    report_path = "python/experiments/results/FINAL_MASTER_IMPORTANCE.csv"
    feature_scores.to_csv(report_path)
    
    print("\n--- FINAL MULTI-YEAR TOP 10 ---")
    print(feature_scores.head(10))
    
    # 4. Save Final Visual
    plt.figure(figsize=(10, 6))
    feature_scores.head(15).plot(kind='barh').invert_yaxis()
    plt.title("Robust Predictive Features (2022-2025 Combined)")
    plt.xlabel("Predictive Power Score")
    plt.tight_layout()
    plt.savefig("python/experiments/visuals/final_robust_features.png")
    
    print(f"\n[AUDIT SUCCESS] Results saved to {report_path}")

if __name__ == "__main__":
    run_final_master_audit()