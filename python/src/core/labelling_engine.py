import pandas as pd
import numpy as np

def apply_triple_barrier_labels(file_path, pt_level=0.0005, sl_level=0.0003, lookahead=10):
    """
    Creates high-probability targets for the 3M timeframe.
    pt_level: Take Profit (5 pips for EURUSD)
    sl_level: Stop Loss (3 pips for EURUSD)
    """
    print(f"Loading enriched data from {file_path}...")
    df = pd.read_csv(file_path, index_col='time', parse_dates=True)
    
    # Initialize labels to 0 (No Trade / Hold)
    df['target'] = 0
    
    close = df['close'].values
    labels = np.zeros(len(close))
    
    print("Generating Triple Barrier labels (this may take a moment)...")
    # Loop through data to find future barrier hits
    for i in range(len(close) - lookahead):
        entry_price = close[i]
        
        for j in range(1, lookahead):
            future_price = close[i + j]
            return_pct = (future_price - entry_price) / entry_price
            
            if return_pct >= pt_level:
                labels[i] = 1 # SUCCESSFUL BUY
                break
            elif return_pct <= -sl_level:
                labels[i] = 0 # STOPPED OUT
                break
                
    df['target'] = labels
    
    # Check balance
    buys = df['target'].sum()
    print(f"Labeling complete. Found {int(buys)} high-probability Buy signals.")
    return df

if __name__ == "__main__":
    input_csv = "python/data/features_added/EURUSD_2022_3M_ENRICHED.csv"
    output_csv = "python/data/processed/EURUSD_2022_3M_LABELED.csv"
    
    labeled_df = apply_triple_barrier_labels(input_csv)
    labeled_df.to_csv(output_csv)
    print(f"Saved labeled dataset to {output_csv}")