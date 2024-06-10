import pandas as pd 
import numpy as np 
import statsmodels.api as sm


def compute_pivot_point(df):
    h = round(df.loc[df.index[-1],'high'],2)
    l = round(df.loc[df.index[-1],'low'],2) 
    c = round(df.loc[df.index[-1],'close'],2)
    p = round((h + l + c) / 3,2) 
    s1 = round((2*p) - h,2) 
    s2 = round(p - (h - l),2)
    s3 = round(p - (2*(h-l)),2)
    r1 = round((2 * p) - l,2) 
    r2 = round(p + (h - l),2)
    r3 = round(p + 2*(h - l),2)
    return (p,s1,s2,s3,r1,r2,r3)

def doji(df):
    df = df.copy()
    avg_candle_size = abs(df['close'] - df['open']).median()
    df['doji'] = abs(df['close'] - df['open']) <= (0.05*avg_candle_size)
    return df

def hammer(df):    
    """returns dataframe with hammer candle column"""
    df = df.copy()
    df["hammer"] = (((df["high"] - df["low"])>3*(df["open"] - df["close"])) & \
                   ((df["close"] - df["low"])/(.001 + df["high"] - df["low"]) > 0.6) & \
                   ((df["open"] - df["low"])/(.001 + df["high"] - df["low"]) > 0.6)) & \
                   (abs(df["close"] - df["open"]) > 0.1* (df["high"] - df["low"]))
    return df

def shooting_star(df):    
    """returns dataframe with shooting star candle column"""
    df = df.copy()
    df["shooting_star"] = (((df["high"] - df["low"])>3*(df["open"] - df["close"])) & \
                   ((df["high"] - df["close"])/(.001 + df["high"] - df["low"]) > 0.6) & \
                   ((df["high"] - df["open"])/(.001 + df["high"] - df["low"]) > 0.6)) & \
                   (abs(df["close"] - df["open"]) > 0.1* (df["high"] - df["low"]))
    return df

def maru_bozu(ohlc_df):    
    """returns dataframe with maru bozu candle column"""
    df = ohlc_df.copy()
    avg_candle_size = abs(df["close"] - df["open"]).median()
    df["h-c"] = df["high"]-df["close"]
    df["l-o"] = df["low"]-df["open"]
    df["h-o"] = df["high"]-df["open"]
    df["l-c"] = df["low"]-df["close"]
    df["maru_bozu"] = np.where((df["close"] - df["open"] > 2*avg_candle_size) & \
                               (df[["h-c","l-o"]].max(axis=1) < 0.005*avg_candle_size),"maru_bozu_green",
                               np.where((df["open"] - df["close"] > 2*avg_candle_size) & \
                               (abs(df[["h-o","l-c"]]).max(axis=1) < 0.005*avg_candle_size),"maru_bozu_red",False))
    df.drop(["h-c","l-o","h-o","l-c"],axis=1,inplace=True)
    return df

def slope(ohlc_df,n):
    "function to calculate the slope of regression line for n consecutive points on a plot"
    df = ohlc_df.iloc[-1*n:,:]
    y = ((df["open"] + df["close"])/2).values
    x = np.array(range(n))
    y_scaled = (y - y.min())/(y.max() - y.min())
    x_scaled = (x - x.min())/(x.max() - x.min())
    x_scaled = sm.add_constant(x_scaled)
    model = sm.OLS(y_scaled,x_scaled)
    results = model.fit()
    slope = np.rad2deg(np.arctan(results.params[-1]))
    return slope

def trend(ohlc_df, n):
    "function to assess the trend by analyzing each candle"
    df = ohlc_df.copy()
    df["up"] = np.where(df["low"] >= df["low"].shift(1), 1, 0)
    df["dn"] = np.where(df["high"] <= df["high"].shift(1), 1, 0)
    
    if df["close"].iloc[-1] > df["open"].iloc[-1]:
        if df["up"].iloc[-n:].sum() >= 0.7 * n:
            return "uptrend"
    elif df["open"].iloc[-1] > df["close"].iloc[-1]:
        if df["dn"].iloc[-n:].sum() >= 0.7 * n:
            return "downtrend"
    else:
        return None