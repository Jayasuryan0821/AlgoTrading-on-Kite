import pandas as pd

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
