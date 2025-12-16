import pandas as pd
import numpy as np

class SpreadAnalysis:
    def calculate_spread(self, series_y, series_x, hedge_ratio):
        return series_y - (hedge_ratio * series_x)

    def calculate_zscore(self, spread, window=20):
        mean = spread.rolling(window=window).mean()
        std = spread.rolling(window=window).std()
        zscore = (spread - mean) / std
        return zscore
