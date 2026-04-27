import pandas as pd
import numpy as np
import time
import os
import getpass
from datetime import datetime

# --- SETTINGS ---
username = getpass.getuser()
COMMON_PATH = rf"C:\Users\{username}\AppData\Roaming\MetaQuotes\Terminal\Common\Files"
MARKET_DATA = os.path.join(COMMON_PATH, "live_market_data.csv")
SIGNAL_FILE = os.path.join(COMMON_PATH, "ai_signal.txt")

# STRATEGY
BUY_THRESHOLD, SELL_THRESHOLD = 0.60, 0.40
EXIT_BUY, EXIT_SELL = 0.48, 0.52
MIN_HOLD_SECONDS = 60

# STATE TRACKING
current_state = "NONE"
last_sent_action = "0"
trade_start_time = None
conf_history = []

def is_data_fresh():
    """Checks if MT5 has updated the market data in the last 30 seconds"""
    if not os.path.exists(MARKET_DATA): return False
    file_age = time.time() - os.path.getmtime(MARKET_DATA)
    return file_age < 30

def determine_signal(conf, state):
    global trade_start_time
    if state == "NONE":
        if conf >= BUY_THRESHOLD: 
            trade_start_time = datetime.now()
            return "1"
        if conf <= SELL_THRESHOLD: 
            trade_start_time = datetime.now()
            return "-1"
        return "0"
    
    # Hold Time Check
    if trade_start_time:
        if (datetime.now() - trade_start_time).total_seconds() < MIN_HOLD_SECONDS:
            return "0"

    # Exit Logic
    if state == "BUY" and conf < EXIT_BUY: return "EXIT"
    if state == "SELL" and conf > EXIT_SELL: return "EXIT"
    return "0"

def run_bridge():
    global current_state, last_sent_action, conf_history
    print("--- PRO BRIDGE ACTIVE ---")
    
    while True:
        if is_data_fresh():
            try:
                raw_conf = np.random.uniform(0.35, 0.65) # Replace with model.predict()
                conf_history.append(raw_conf)
                if len(conf_history) > 3: conf_history.pop(0)
                smooth_conf = sum(conf_history) / len(conf_history)

                action = determine_signal(smooth_conf, current_state)
                
                # Only write to file if the action is a NEW command
                if action != "0" and action != last_sent_action:
                    with open(SIGNAL_FILE, "w") as f:
                        f.write(action)
                    last_sent_action = action
                    
                    if action == "1": current_state = "BUY"
                    elif action == "-1": current_state = "SELL"
                    elif action == "EXIT": 
                        current_state = "NONE"
                        last_sent_action = "0" # Reset for next trade
                
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Smooth: {smooth_conf:.2%} | State: {current_state}")
                
            except Exception as e:
                print(f"Loop Error: {e}")
        else:
            print("WAITING: Market data is stale or MT5 is closed...")
            
        time.sleep(3)

if __name__ == "__main__":
    run_bridge()