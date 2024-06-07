import pandas as pd 
from stocktrends import Renko

def convert_to_renko(df,brick_size):
    df = df.copy()
    df.reset_index(inplace=True)
    renko_df = Renko(df)
    renko_df.brick_size = brick_size
    renko_df = renko_df.get_ohlc_data()
    return renko_df
