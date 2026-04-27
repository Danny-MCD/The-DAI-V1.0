import pandas as pd
import pandas_ta as ta

def apply_features(df):
    """
    Injects Advanced Price Action and Technical features.
    """
    # 1. Standard Technicals
    df.ta.macd(append=True)
    df.ta.rsi(append=True)
    df.ta.atr(append=True)
    df.ta.bbands(append=True)
    df.ta.ema(length=50, append=True)
    
    # 2. NEW: Price Action Injection
    # Body Size vs Total Range (1.0 = Strong Conviction)
    df['candle_strength'] = (df['close'] - df['open']).abs() / (df['high'] - df['low']).replace(0, 0.0001)
    
    # Distance from EMA_50 (Normalized by ATR)
    atr_col = 'ATRr_14' if 'ATRr_14' in df.columns else 'ATR_14'
    df['ema_dist'] = (df['close'] - df['EMA_50']) / df[atr_col]
    
    # Relative Volume (Current vs 20-period Average)
    df['rel_volume'] = df['volume'] / df['volume'].rolling(window=20).mean()
    
    # Price Momentum (5-bar Rate of Change)
    df['roc_5'] = df['close'].pct_change(periods=5)
    
    # Session Context
    df['hour'] = df.index.hour
    df['day_of_week'] = df.index.dayofweek

    return df.dropna()