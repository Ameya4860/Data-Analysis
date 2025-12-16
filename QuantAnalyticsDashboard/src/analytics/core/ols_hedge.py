import statsmodels.api as sm
import pandas as pd
import numpy as np

class OLSHedgeRatio:
    def calculate(self, series_y, series_x):
        """
        Calculates Hedge Ratio using OLS: Y = beta * X + alpha
        Returns beta (hedge ratio).
        """
        if len(series_y) != len(series_x) or len(series_y) < 2:
            return 0.0
        
        X = sm.add_constant(series_x)
        model = sm.OLS(series_y, X).fit()
        return model.params.iloc[1] # beta
