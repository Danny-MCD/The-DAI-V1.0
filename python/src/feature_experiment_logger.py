import pandas as pd
import numpy as np
from sklearn.feature_selection import mutual_info_classif
import datetime

def run_logged_experiment(input_file, timeframe, year, pt_pips, sl_pips, lookahead):
    """
    Runs a feature importance experiment and exports full documentation.
    """
    print(f"\n--- Running Experiment: {timeframe} | {pt_pips} Pips TP ---")
    df = pd.read_csv(input_file, index_col='time', parse_dates=True)
    
    # 1. Define the Experiment Metadata
    metadata = {
        "Timeframe": timeframe,
        "Dataset_Year": year,
        "TP_Pips": pt_pips,
        "SL_Pips": sl_pips,
        "Max_Hold_Bars": lookahead,
        "Timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    }

    # 2. Run the Statistical Test (Mutual Information)
    X = df.drop(columns=['target'])
    y = df['target']
    
    print("Calculating Predictive Scores...")
    scores = mutual_info_classif(X, y, random_state=42)
    
    # 3. Create the Explanation Mapping
    def explain_score(s):
        if s > 0.03: return "Strong Predictor: High statistical dependency."
        if s > 0.01: return "Moderate Predictor: Useful as a supporting filter."
        return "Weak Predictor: High noise-to-signal ratio for this specific target."

    # 4. Compile the Report
    report_data = []
    for i, col in enumerate(X.columns):
        report_data.append({
            "Feature_Name": col,
            "MI_Score": round(scores[i], 5),
            "Evaluation": explain_score(scores[i]),
            **metadata # Adds the TP/SL settings to every row for comparison
        })

    report_df = pd.DataFrame(report_data).sort_values(by="MI_Score", ascending=False)
    
    # 5. Export
    filename = f"python/data/audit_results_{timeframe}_{pt_pips}pips.csv"
    report_df.to_csv(filename, index=False)
    print(f"Full Audit Report saved to: {filename}")
    
    return report_df

if __name__ == "__main__":
    # Current Baseline Settings
    run_logged_experiment(
        input_file="python/data/processed/EURUSD_2022_3M_LABELED.csv",
        timeframe="3M",
        year="2022",
        pt_pips=5,
        sl_pips=3,
        lookahead=10
    )