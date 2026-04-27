import pandas as pd
import numpy as np
import xgboost as xgb
import joblib
import glob
from pathlib import Path
from sklearn.metrics import accuracy_score

def train_master():
    # Setup Paths
    script_dir = Path(__file__).resolve().parent
    root = script_dir.parent
    data_folder = root / "data" / "features_added"
    model_folder = root / "models"
    
    # 1. Collect only Comprehensive files
    all_files = glob.glob(str(data_folder / "COMP_FE_EURUSD_*.csv"))
    print(f"Found {len(all_files)} years of engineered data.")

    if not all_files:
        print("No COMP_FE files found. Run comprehensive_engineer.py first.")
        return

    li = [pd.read_csv(f) for f in all_files]
    full_df = pd.concat(li, axis=0, ignore_index=True)
    full_df['time'] = pd.to_datetime(full_df['time'])
    full_df = full_df.sort_values('time')
    
    # 2. Features and Target
    exclude = ['time','open','high','low','close','tick_volume','volume','target_label']
    features = [c for c in full_df.columns if c not in exclude]
    X, y = full_df[features], full_df['target_label']

    # 3. Split & Train
    split_idx = int(len(full_df) * 0.9)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

    model = xgb.XGBClassifier(
        n_estimators=1000,
        max_depth=6,
        learning_rate=0.01,
        tree_method='hist',
        eval_metric='logloss',
        early_stopping_rounds=50
    )

    model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=100)

    # 4. Evaluation
    probs = model.predict_proba(X_test)[:, 1]
    threshold = 0.60
    mask = (probs > threshold) | (probs < (1 - threshold))
    
    if mask.any():
        conf_acc = accuracy_score(y_test[mask], (probs[mask] > 0.5).astype(int))
        print(f"\nMASTER HIGH CONFIDENCE ACCURACY: {conf_acc:.2%}")
    
    # 5. Save
    model_folder.mkdir(exist_ok=True)
    joblib.dump(model, model_folder / "master_model_v2.pkl")
    joblib.dump(features, model_folder / "master_features_list.pkl")
    print(f"Model and features saved to {model_folder}")

if __name__ == "__main__":
    train_master()