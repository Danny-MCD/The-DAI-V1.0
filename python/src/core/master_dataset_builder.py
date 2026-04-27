import pandas as pd
import os
import json

def build_master_dataset():
    with open("python/config/baseline_3m.json", 'r') as f:
        cfg = json.load(f)
    
    all_files = []
    enriched_path = cfg['paths']['enriched']
    
    print(f"Reading enriched data from: {enriched_path}")
    for file in os.listdir(enriched_path):
        if file.endswith("_ENRICHED.csv"):
            print(f"Adding {file}...")
            all_files.append(pd.read_csv(os.path.join(enriched_path, file), index_col='time', parse_dates=True))
    
    if not all_files:
        print("Error: No enriched files found. Run mass_producer.py first!")
        return

    master_df = pd.concat(all_files).sort_index()
    
    # Labelling logic from your JSON
    tp_pips = cfg['labeling']['tp_pips'] * 0.0001
    sl_pips = cfg['labeling']['sl_pips'] * 0.0001
    lookahead = cfg['labeling']['lookahead']
    
    def get_label(current_idx):
        try:
            future_data = master_df['close'].iloc[current_idx+1 : current_idx + lookahead]
            entry_price = master_df['close'].iloc[current_idx]
            for price in future_data:
                if price >= entry_price + tp_pips: return 1.0
                if price <= entry_price - sl_pips: return 0.0
            return 0.0
        except: return 0.0

    print(f"Applying Triple Barrier (Lookahead: {lookahead}) to {len(master_df)} rows...")
    master_df['target'] = [get_label(i) for i in range(len(master_df))]
    
    output_dir = cfg['paths']['labeled']
    os.makedirs(output_dir, exist_ok=True)
    output_path = f"{output_dir}MASTER_EURUSD_3M_2022_2025.csv"
    
    master_df.to_csv(output_path)
    print(f"\n[BUILD COMPLETE] Master File: {output_path}")

if __name__ == "__main__":
    build_master_dataset()