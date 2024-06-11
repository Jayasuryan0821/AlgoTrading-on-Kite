import pandas as pd 
import numpy as np 


def compute_super_trend(df,n,multiplier):
    df['hl2'] = (df['high'] + df['low'])/2
    df['tr'] = np.maximum.reduce([df['high'] - df['low'],
                  abs(df['high'] - df['close'].shift(1)),
                  abs(df['low'] - df['close'].shift(1))])
    alpha = 1/n
    
    df.loc[df.index[n-1], 'atr'] = df['tr'][:n].mean()
    for i in range(n, len(df)):
        df.loc[df.index[i], 'atr'] = alpha * df.loc[df.index[i], 'tr'] + (1 - alpha) * df.loc[df.index[i-1], 'atr']

    df['basic_ub'] = df['hl2'] + (multiplier*df['atr'])
    df['basic_lb'] = df['hl2'] - (multiplier*df['atr'])
    df.loc[df.index[n-1], 'ub'] = df.loc[df.index[n-1],'basic_ub'] 
    df.loc[df.index[n-1], 'lb'] = df.loc[df.index[n-1],'basic_lb'] 

    for i in range(n,len(df)):
        if ((df.loc[df.index[i],'basic_ub'] < df.loc[df.index[i-1],'ub']) or 
        (df.loc[df.index[i-1],'close'] > df.loc[df.index[i-1],'ub'])):
            df.loc[df.index[i],'ub'] = df.loc[df.index[i],'basic_ub']
        else:
            df.loc[df.index[i],'ub'] = df.loc[df.index[i-1],'ub']
        
        if ((df.loc[df.index[i],'basic_lb'] > df.loc[df.index[i-1],'lb']) or 
        (df.loc[df.index[i-1],'close'] < df.loc[df.index[i-1],'ub'])):
            df.loc[df.index[i],'lb'] = df.loc[df.index[i],'basic_lb']
        else:
            df.loc[df.index[i],'lb'] = df.loc[df.index[i-1],'lb']

    isUpTrend,isDownTrend = 'up','down'
    init_trend_dir = isDownTrend
    df['trend_direction'] = init_trend_dir
    df['super_trend'] = pd.Series(dtype=float)
    for i in range(len(df)):
        if i < n:
            df.loc[df.index[i], 'trend_direction'] = init_trend_dir
        else:
            prev_super_trend = df.loc[df.index[i-1], 'super_trend'] if i > n else None
            prev_upper_band = df.loc[df.index[i-1], 'ub']
            prev_lower_band = df.loc[df.index[i-1], 'lb']
            
            if prev_super_trend == prev_upper_band:
                if df.loc[df.index[i], 'close'] > df.loc[df.index[i], 'ub']:
                    df.loc[df.index[i], 'trend_direction'] = isUpTrend
                else:
                    df.loc[df.index[i], 'trend_direction'] = isDownTrend
            else:
                if df.loc[df.index[i], 'close'] < df.loc[df.index[i], 'lb']:
                    df.loc[df.index[i], 'trend_direction'] = isDownTrend
                else:
                    df.loc[df.index[i], 'trend_direction'] = isUpTrend
            
            if df.loc[df.index[i], 'trend_direction'] == isUpTrend:
                df.loc[df.index[i], 'super_trend'] = df.loc[df.index[i], 'lb']
            else:
                df.loc[df.index[i], 'super_trend'] = df.loc[df.index[i], 'ub']

    return df
