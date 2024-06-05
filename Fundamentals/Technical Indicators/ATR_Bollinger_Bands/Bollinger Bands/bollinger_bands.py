import pandas as pd

def compute_bollinger_bands(df,n):
    df['sma'] = df['close'].rolling(window=20).mean()
    df['upper_band'] = df['sma'] + (2*df['close'].rolling(window=20).std(ddof=0))
    df['lower_band'] = df['sma'] - (2*df['close'].rolling(window=20).std(ddof=0))
    df['band_width'] = df['upper_band'] - df['lower_band']
    return df
