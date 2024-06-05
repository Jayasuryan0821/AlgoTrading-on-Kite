from auto_login import get_curr_path,get_credentials,auto_login,generate_access_token
import os 
import logging 
from kiteconnect import KiteConnect
import datetime as dt
import pandas as pd 
import matplotlib.pyplot as plt
import numpy as np 
import ta

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