import pandas as pd 
import numpy as np 
import time 


def doji(ohlc_df):
    """returns dataframe with doji candle column"""
    df = ohlc_df.copy()
    avg_candle_size = abs(df["close"] - df["open"]).median()
    df["doji"] = abs(df["close"] - df["open"]).iloc[-1] <= (0.05 * avg_candle_size)
    return df

def maru_bozu(ohlc_df):
    """returns dataframe with maru bozu candle column"""
    df = ohlc_df.copy()
    avg_candle_size = abs(df["close"] - df["open"]).median()
    df["h-c"] = df["high"] - df["close"]
    df["l-o"] = df["low"] - df["open"]
    df["h-o"] = df["high"] - df["open"]
    df["l-c"] = df["low"] - df["close"]
    df["maru_bozu"] = np.where(
        (df["close"] - df["open"] > 2 * avg_candle_size) &
        (df[["h-c", "l-o"]].max(axis=1) < 0.005 * avg_candle_size), "maru_bozu_green",
        np.where(
            (df["open"] - df["close"] > 2 * avg_candle_size) &
            (abs(df[["h-o", "l-c"]]).max(axis=1) < 0.005 * avg_candle_size), "maru_bozu_red", False
        )
    )
    df.drop(["h-c", "l-o", "h-o", "l-c"], axis=1, inplace=True)
    return df

def hammer(ohlc_df):
    """returns dataframe with hammer candle column"""
    df = ohlc_df.copy()
    df["hammer"] = (
        ((df["high"] - df["low"]) > 3 * (df["open"] - df["close"])) &
        ((df["close"] - df["low"]) / (.001 + df["high"] - df["low"]) > 0.6) &
        ((df["open"] - df["low"]) / (.001 + df["high"] - df["low"]) > 0.6) &
        (abs(df["close"] - df["open"]) > 0.1 * (df["high"] - df["low"]))
    ).iloc[-1]
    return df

def shooting_star(ohlc_df):
    """returns dataframe with shooting star candle column"""
    df = ohlc_df.copy()
    df["sstar"] = (
        ((df["high"] - df["low"]) > 3 * (df["open"] - df["close"])) &
        ((df["high"] - df["close"]) / (.001 + df["high"] - df["low"]) > 0.6) &
        ((df["high"] - df["open"]) / (.001 + df["high"] - df["low"]) > 0.6) &
        (abs(df["close"] - df["open"]) > 0.1 * (df["high"] - df["low"]))
    ).iloc[-1]
    return df

def levels(ohlc_day):
    """returns pivot point and support/resistance levels"""
    high = round(ohlc_day["high"].iloc[-1], 2)
    low = round(ohlc_day["low"].iloc[-1], 2)
    close = round(ohlc_day["close"].iloc[-1], 2)
    pivot = round((high + low + close) / 3, 2)
    r1 = round((2 * pivot - low), 2)
    r2 = round((pivot + (high - low)), 2)
    r3 = round((high + 2 * (pivot - low)), 2)
    s1 = round((2 * pivot - high), 2)
    s2 = round((pivot - (high - low)), 2)
    s3 = round((low - 2 * (high - pivot)), 2)
    return (pivot, r1, r2, r3, s1, s2, s3)

def trend(ohlc_df, n):
    """Function to assess the trend by analyzing each candle"""
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
    
def res_sup(ohlc_df, ohlc_day):
    """calculates closest resistance and support levels for a given candle"""
    level = (
        ((ohlc_df["close"].iloc[-1] + ohlc_df["open"].iloc[-1]) / 2) +
        ((ohlc_df["high"].iloc[-1] + ohlc_df["low"].iloc[-1]) / 2)
    ) / 2
    p, r1, r2, r3, s1, s2, s3 = levels(ohlc_day)
    l_r1 = level - r1
    l_r2 = level - r2
    l_r3 = level - r3
    l_p = level - p
    l_s1 = level - s1
    l_s2 = level - s2
    l_s3 = level - s3
    lev_ser = pd.Series([l_p, l_r1, l_r2, l_r3, l_s1, l_s2, l_s3], index=["p", "r1", "r2", "r3", "s1", "s2", "s3"])
    sup = lev_ser[lev_ser > 0].idxmin()
    res = lev_ser[lev_ser < 0].idxmax()
    return (eval('{}'.format(res)), eval('{}'.format(sup)))

def candle_type(ohlc_df):
    """returns the candle type of the last candle of an OHLC DF"""
    candle = None
    if doji(ohlc_df)["doji"].iloc[-1] == True:
        candle = "doji"
    if maru_bozu(ohlc_df)["maru_bozu"].iloc[-1] == "maru_bozu_green":
        candle = "maru_bozu_green"
    if maru_bozu(ohlc_df)["maru_bozu"].iloc[-1] == "maru_bozu_red":
        candle = "maru_bozu_red"
    if shooting_star(ohlc_df)["sstar"].iloc[-1] == True:
        candle = "shooting_star"
    if hammer(ohlc_df)["hammer"].iloc[-1] == True:
        candle = "hammer"
    return candle

def candle_pattern(ohlc_df, ohlc_day):
    """returns the candle pattern identified"""
    pattern = None
    signi = "low"
    avg_candle_size = abs(ohlc_df["close"] - ohlc_df["open"]).median()
    sup, res = res_sup(ohlc_df, ohlc_day)

    # Check if the last close price is near the support or resistance levels
    if (sup - 1.5 * avg_candle_size) < ohlc_df["close"].iloc[-1] < (sup + 1.5 * avg_candle_size):
        signi = "HIGH"
    if (res - 1.5 * avg_candle_size) < ohlc_df["close"].iloc[-1] < (res + 1.5 * avg_candle_size):
        signi = "HIGH"

    # Determine the pattern based on the last candle type and other conditions
    if candle_type(ohlc_df) == 'doji' \
            and ohlc_df["close"].iloc[-1] > ohlc_df["close"].iloc[-2] \
            and ohlc_df["close"].iloc[-1] > ohlc_df["open"].iloc[-1]:
        pattern = "doji_bullish"

    if candle_type(ohlc_df) == 'doji' \
            and ohlc_df["close"].iloc[-1] < ohlc_df["close"].iloc[-2] \
            and ohlc_df["close"].iloc[-1] < ohlc_df["open"].iloc[-1]:
        pattern = "doji_bearish"

    if candle_type(ohlc_df) == "maru_bozu_green":
        pattern = "maru_bozu_bullish"

    if candle_type(ohlc_df) == "maru_bozu_red":
        pattern = "maru_bozu_bearish"

    if trend(ohlc_df.iloc[:-1, :], 7) == "uptrend" and candle_type(ohlc_df) == "hammer":
        pattern = "hanging_man_bearish"

    if trend(ohlc_df.iloc[:-1, :], 7) == "downtrend" and candle_type(ohlc_df) == "hammer":
        pattern = "hammer_bullish"

    if trend(ohlc_df.iloc[:-1, :], 7) == "uptrend" and candle_type(ohlc_df) == "shooting_star":
        pattern = "shooting_star_bearish"

    if trend(ohlc_df.iloc[:-1, :], 7) == "uptrend" \
            and candle_type(ohlc_df) == "doji" \
            and ohlc_df["high"].iloc[-1] < ohlc_df["close"].iloc[-2] \
            and ohlc_df["low"].iloc[-1] > ohlc_df["open"].iloc[-2]:
        pattern = "harami_cross_bearish"

    if trend(ohlc_df.iloc[:-1, :], 7) == "downtrend" \
            and candle_type(ohlc_df) == "doji" \
            and ohlc_df["high"].iloc[-1] < ohlc_df["open"].iloc[-2] \
            and ohlc_df["low"].iloc[-1] > ohlc_df["close"].iloc[-2]:
        pattern = "harami_cross_bullish"

    if trend(ohlc_df.iloc[:-1, :], 7) == "uptrend" \
            and candle_type(ohlc_df) != "doji" \
            and ohlc_df["open"].iloc[-1] > ohlc_df["high"].iloc[-2] \
            and ohlc_df["close"].iloc[-1] < ohlc_df["low"].iloc[-2]:
        pattern = "engulfing_bearish"

    if trend(ohlc_df.iloc[:-1, :], 7) == "downtrend" \
            and candle_type(ohlc_df) != "doji" \
            and ohlc_df["close"].iloc[-1] > ohlc_df["high"].iloc[-2] \
            and ohlc_df["open"].iloc[-1] < ohlc_df["low"].iloc[-2]:
        pattern = "engulfing_bullish"

    return "Significance - {}, Pattern - {}".format(signi, pattern)
