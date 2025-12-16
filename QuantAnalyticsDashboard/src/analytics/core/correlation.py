import pandas as pd

class RollingCorrelation:
    def calculate(self, series_a, series_b, window=20):
        return series_a.rolling(window=window).corr(series_b)
