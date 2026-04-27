import pandas as pd
import joblib
import json
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_recall_curve

def optimize_threshold():
    with open("python/config/baseline_3m.json", 'r') as f:
        cfg = json.load(f)
    
    df = pd.read_csv(f"{cfg['paths']['labeled']}MASTER_EURUSD_3M_2022_2025.csv", index_col='time', parse_dates=True)
    model = joblib.load(f"{cfg['paths']['models']}MASTER_FOREX_3M_v1.pkl")
    with open(f"{cfg['paths']['models']}feature_list.json", 'r') as f:
        features = json.load(f)

    X = df[features]
    y = df['target']
    _, X_test, _, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

    # Get raw probabilities
    probs = model.predict_proba(X_test)[:, 1]
    precision, recall, thresholds = precision_recall_curve(y_test, probs)
    
    # Find the absolute best precision we can get
    max_precision = np.max(precision)
    best_index = np.argmax(precision)
    
    # To avoid the IndexError, we'll pick the threshold that gives us the best balance
    # or at least the highest precision available.
    if max_precision < 0.50:
        print(f"!!! WARNING: Max Precision is {round(max_precision*100, 2)}%. Lower than 50% target.")
        actual_best_threshold = thresholds[best_index] if best_index < len(thresholds) else 0.8
    else:
        # If we CAN hit 50%, find the first time we do
        idx_50 = np.where(precision >= 0.50)[0][0]
        actual_best_threshold = thresholds[idx_50]

    print(f"\n--- OPTIMIZATION REPORT ---")
    print(f"Maximum Precision Achievable: {round(max_precision*100, 2)}%")
    print(f"Suggested Confidence Threshold: {round(actual_best_threshold, 4)}")
    print(f"Trades caught at this level: {round(recall[best_index]*100, 2)}% of all moves")

    # Update config
    cfg['labeling']['probability_threshold'] = float(actual_best_threshold)
    with open("python/config/baseline_3m.json", 'w') as f:
        json.dump(cfg, f, indent=4)
    print(f"\n[SUCCESS] Config updated with threshold: {actual_best_threshold}")

if __name__ == "__main__":
    optimize_threshold()