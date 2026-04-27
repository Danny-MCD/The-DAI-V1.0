import pandas as pd
import pandas_ta as ta
import os
import json

def load_config(config_path):
    with open(config_path, 'r') as f:
        return json.load(f)

def process_year(year, config):
    input_file = f"{config['paths']['raw']}EURUSD_{year}.csv"
    output_file = f"{config['paths']['enriched']}EURUSD_{year}_{config['timeframe']}_ENRICHED.csv"
    
    if not os.path.exists(input_file):
        print(f"Skipping {year}: File not found at {input_file}")
        return

    print(f"--- Processing {year} ---")
    
    # 1. Load & Resample
    df = pd.read_csv(input_file, parse_dates=['time'], index_col='time')
    df_resampled = df.resample(config['timeframe']).agg({
        'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'tick_volume': 'sum'
    }).dropna()
    df_resampled.rename(columns={'tick_volume': 'volume'}, inplace=True)
    
    # 2. Add Features (Factory)
    df_resampled.columns = [x.lower() for x in df_resampled.columns]
    
    # Momentum
    df_resampled.ta.rsi(length=14, append=True)
    df_resampled.ta.macd(append=True)
    
    # Volatility
    df_resampled.ta.atr(append=True)
    df_resampled.ta.bbands(length=20, append=True)
    
    # Trend
    df_resampled.ta.ema(length=20, append=True)
    df_resampled.ta.ema(length=50, append=True)
    df_resampled.ta.adx(append=True)
    
    # 3. Save
    final_df = df_resampled.dropna()
    final_df.to_csv(output_file)
    print(f"Successfully saved {len(final_df)} rows to {output_file}")

if __name__ == "__main__":
    config_file = "python/config/baseline_3m.json"
    cfg = load_config(config_file)
    
    # Ensure output directory exists
    os.makedirs(cfg['paths']['enriched'], exist_ok=True)
    
    # Run the loop for the years defined in your JSON
    for y in cfg['years']:
        process_year(y, cfg)

    print("\n[ALL YEARS PROCESSED] Your 'features_added' folder is now fully populated.")