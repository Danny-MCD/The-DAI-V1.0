import pandas as pd
import joblib
import json
import os
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from imblearn.over_sampling import SMOTE
from sklearn.ensemble import ExtraTreesClassifier

def train_production_model():
    with open("python/config/baseline_3m.json", 'r') as f:
        cfg = json.load(f)
    
    data_path = f"{cfg['paths']['labeled']}MASTER_EURUSD_3M_2022_2025.csv"
    if not os.path.exists(data_path):
        print(f"Error: {data_path} not found.")
        return

    df = pd.read_csv(data_path, index_col='time', parse_dates=True)
    
    features = ['ATRr_14', 'volume', 'BBB_20_2.0_2.0', 'MACD_12_26_9', 'EMA_50', 
                'candle_strength', 'ema_dist', 'rel_volume', 'roc_5', 'hour', 'day_of_week']
    
    df = df.dropna(subset=features)
    X, y = df[features], df['target']
    X_train_raw, X_test, y_train_raw, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
    
    print("Balancing training data...")
    X_train, y_train = SMOTE(random_state=42).fit_resample(X_train_raw, y_train_raw)

    model = ExtraTreesClassifier(n_estimators=1000, max_depth=25, bootstrap=True, n_jobs=-1, random_state=42)
    print("Training Ultra-Brain...")
    model.fit(X_train, y_train)
    
    probs = model.predict_proba(X_test)[:, 1]
    print("\n--- ELITE PERFORMANCE (70% Filter) ---")
    print(classification_report(y_test, (probs > 0.70).astype(int)))
    
    os.makedirs(cfg['paths']['models'], exist_ok=True)
    joblib.dump(model, f"{cfg['paths']['models']}MASTER_FOREX_3M_v1.pkl")
    print("\n[SUCCESS] Model Saved.")

if __name__ == "__main__":
    train_production_model()