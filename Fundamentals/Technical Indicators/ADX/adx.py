import pandas as pd 
import numpy as np

def compute_adx(df,n):
    
    df['tr'] = np.maximum.reduce([df['high'] - df['low'],
                  abs(df['high'] - df['close'].shift(1)),
                  abs(df['low'] - df['close'].shift(1))])
    df['+DM'] = np.where((df['high'] - df['high'].shift(1)) > (df['low'].shift(1) - df['low']),
                    np.maximum(df['high'] - df['high'].shift(1), 0),
                    0)

    df['-DM'] = np.where((df['low'].shift(1) - df['low']) > (df['high'] - df['high'].shift(1)),
                        np.maximum(df['low'].shift(1) - df['low'], 0),
                        0)
    
    for i in range(len(df)):
        if i == n:
            df.loc[df.index[i-1], 'tr_smoothed'] = df['tr'][:i].sum()
            df.loc[df.index[i-1], '+DM_smoothed'] = df['+DM'][:i].sum()
            df.loc[df.index[i-1], '-DM_smoothed'] = df['-DM'][:i].sum()

    for i in range(n,len(df)):
        df.loc[df.index[i], 'tr_smoothed'] = (df.loc[df.index[i-1], 'tr_smoothed'] - (df.loc[df.index[i-1], 'tr_smoothed'] / n)) + df.loc[df.index[i], 'tr'] 
        df.loc[df.index[i], '+DM_smoothed'] = (df.loc[df.index[i-1], '+DM_smoothed'] - (df.loc[df.index[i-1], '+DM_smoothed'] / n)) + df.loc[df.index[i], '+DM'] 
        df.loc[df.index[i], '-DM_smoothed'] = (df.loc[df.index[i-1], '-DM_smoothed'] - (df.loc[df.index[i-1], '-DM_smoothed'] / n)) + df.loc[df.index[i], '-DM']

    df['DI+'] = 100*(df['+DM_smoothed'] / df['tr_smoothed'])
    df['DI-'] = 100*(df['-DM_smoothed'] / df['tr_smoothed']) 
    df['DX'] = (abs(df['DI+'] - df['DI-']) / (df['DI+'] + df['DI-'])) * 100
    df.loc[df.index[n*2-1], 'ADX'] = df['DX'][n:n*2].mean()

    for i in range(n*2, len(df)):
        df.loc[df.index[i], 'ADX'] = (
            (df.loc[df.index[i-1], 'ADX'] * (n - 1) + df.loc[df.index[i], 'DX']) / n
        )

    return df
