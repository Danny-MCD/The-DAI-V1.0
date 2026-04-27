import pandas as pd
import numpy as np
import os
import glob
from pathlib import Path

try:
    import pandas_ta as ta
except ImportError:
    print("Run: pip install pandas_ta")
    exit()

def get_comprehensive_features(df):
    if 'tick_volume' in df.columns:
        df['volume'] = df['tick_volume']
    df['time'] = pd.to_datetime(df['time'])
    df = df.sort_values('time').reset_index(drop=True)

    # Transformations
    df['log_ret'] = np.log(df['close'] / df['close'].shift(1))
    df['vol_ret'] = df['tick_volume'].pct_change()
    
    # Cyclical Time
    df['hour'] = df['time'].dt.hour
    df['day'] = df['time'].dt.dayofweek
    df['sin_hour'] = np.sin(2 * np.pi * df['hour']/24)
    df['cos_hour'] = np.cos(2 * np.pi * df['hour']/24)

    # Technical Indicators
    for span in [9, 21, 50, 100, 200]:
        df[f'ema_{span}'] = ta.ema(df['close'], length=span)
        df[f'dist_ema_{span}'] = (df['close'] - df[f'ema_{span}']) / (df[f'ema_{span}'] + 1e-9)

    df.ta.macd(append=True)
    df.ta.rsi(length=14, append=True)
    df.ta.rsi(length=2, append=True)
    df.ta.bbands(length=20, std=2, append=True)
    df.ta.atr(length=14, append=True)
    
    # Volume & Stats
    df['vol_z'] = (df['tick_volume'] - df['tick_volume'].rolling(20).mean()) / (df['tick_volume'].rolling(20).std() + 1e-9)
    df['rolling_skew'] = df['log_ret'].rolling(30).skew()
    df['rolling_kurt'] = df['log_ret'].rolling(30).kurt()

    # Target: 15-bar lookahead
    df['target_label'] = (df['close'].shift(-15) > df['close']).astype(int)
    return df.dropna()

def main():
    # Setup Paths relative to this file (python/src/...)
    script_dir = Path(__file__).resolve().parent
    root = script_dir.parent # This is the 'python' folder
    
    input_path = root / "data" / "historical_years"
    output_path = root / "data" / "features_added"
    
    output_path.mkdir(parents=True, exist_ok=True)
    files = glob.glob(str(input_path / "EURUSD_*.csv"))
    
    if not files:
        print(f"No files found in {input_path}")
        return

    for f in files:
        fname = os.path.basename(f)
        print(f"Processing: {fname}")
        raw_df = pd.read_csv(f)
        full_df = get_comprehensive_features(raw_df)
        
        save_to = output_path / f"COMP_FE_{fname}"
        full_df.to_csv(save_to, index=False)
        print(f"Saved to: {save_to.name} (Features: {len(full_df.columns)})")

if __name__ == "__main__":
    main()