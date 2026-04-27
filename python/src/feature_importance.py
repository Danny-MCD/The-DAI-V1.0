import pandas as pd
import numpy as np
from sklearn.feature_selection import mutual_info_classif
import matplotlib.pyplot as plt

def analyze_3m_predictive_power(file_path):
    print(f"Analyzing feature importance for: {file_path}")
    df = pd.read_csv(file_path, index_col='time', parse_dates=True)
    
    # 1. Clean data: The model can't analyze NaNs or the 'target' itself
    X = df.drop(columns=['target'])
    y = df['target']
    
    # 2. Calculate Mutual Information
    # discrete_features=False because our technical indicators are continuous numbers
    print("Calculating Mutual Information scores... (this may take a minute)")
    importances = mutual_info_classif(X, y, discrete_features=False, random_state=42)
    
    # 3. Organize results
    feature_scores = pd.Series(importances, index=X.columns).sort_values(ascending=False)
    
    print("\n--- TOP 10 PREDICTIVE FEATURES ---")
    print(feature_scores.head(10))
    
    # 4. Export for your records
    feature_scores.to_csv("python/data/feature_importance_scores.csv")
    return feature_scores

if __name__ == "__main__":
    labeled_data = "python/data/processed/EURUSD_2022_3M_LABELED.csv"
    scores = analyze_3m_predictive_power(labeled_data)