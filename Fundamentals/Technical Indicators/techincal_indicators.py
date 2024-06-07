import pandas as pd 
import numpy as np

def compute_ema(df,n,column_name):
    df['sma'] = df['close'].rolling(n).mean()
    multiplier = 2 / (n + 1)
    df.dropna(inplace=True)
    for i in range(1,len(df)):
        if i == 1:
            df.loc[df.index[i],column_name] = df.loc[df.index[i - 1],'sma']
        else:
            df.loc[df.index[i],column_name] = (df.loc[df.index[i],'close'] - df.loc[df.index[i - 1],column_name]) * multiplier + df.loc[df.index[i - 1],column_name]
    return df

def compute_signal(df,n):
    df['signal_sma'] = df['macd'].rolling(n).mean()
    multiplier = 2 / (n + 1)
    df.dropna(inplace=True)
    for i in range(1,len(df)):
        if i == 1:
            df.loc[df.index[i],'signal_ma'] = df.loc[df.index[i - 1],'signal_sma']
        else:
            df.loc[df.index[i],'signal_ma'] = (df.loc[df.index[i],'macd'] - df.loc[df.index[i - 1],'signal_ma']) * multiplier + df.loc[df.index[i - 1],'signal_ma']
    return df


def compute_bollinger_bands(df,n):
    df['sma'] = df['close'].rolling(window=20).mean()
    df['upper_band'] = df['sma'] + (2*df['close'].rolling(window=20).std(ddof=0))
    df['lower_band'] = df['sma'] - (2*df['close'].rolling(window=20).std(ddof=0))
    df['band_width'] = df['upper_band'] - df['lower_band']
    return df


def compute_true_range(df,n):
    df['high-low'] = df['high'] - df['low']
    df['high-prev_close'] = abs(df['high'] - df['close'].shift(1))
    df['low-prev_close'] = abs(df['low'] - df['close'].shift(1))
    df['true_range'] = df[['high-low','high-prev_close','low-prev_close']].max(axis=1,skipna=False)
    # df['atr'] = df['true_range'].rolling(n).mean()
    return df


def compute_atr(df,n):
    alpha = 1/n
    df['temp_ma_init'] = df['true_range'].rolling(n).mean()
    df.dropna(inplace=True)
    for i in range(1,len(df)):
        if i == 1:
            df.loc[df.index[i],'atr'] = df.loc[df.index[i],'temp_ma_init']
        else:
            df.loc[df.index[i],'atr'] = alpha*df.loc[df.index[i],'true_range'] + (1 - alpha)*df.loc[df.index[i-1],'atr']
    return df

def compute_rsi(df,n):
    df['close_diff'] = df['close'].diff().dropna()
    df.dropna(inplace=True)
    df['gain'] = df['close_diff'].apply(lambda x: x if x > 0 else 0)
    df['loss'] = df['close_diff'].apply(lambda x: -x if x < 0 else 0)
    alpha = 1/n
    
    for i in range(n,len(df)):
        if i == n:
            df.loc[df.index[i],'avg_gain'] = df['gain'].rolling(window=n,min_periods=n).mean().iloc[n-1]
            df.loc[df.index[i],'avg_loss'] = df['loss'].rolling(window=n,min_periods=n).mean().iloc[n-1]
        else:
            df.loc[df.index[i],'avg_gain'] = (alpha * df.loc[df.index[i],'gain']) + (1 - alpha)*(df.loc[df.index[i-1],'avg_gain'])
            df.loc[df.index[i],'avg_loss'] = (alpha * df.loc[df.index[i],'loss']) + (1 - alpha)*(df.loc[df.index[i-1],'avg_loss'])
    
    df['rs'] = df['avg_gain'] / df['avg_loss']
    df['rsi'] = 100 - (100/(1 + df['rs']))
    return df


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
