from statsmodels.tsa.stattools import adfuller

class ADFTest:
    def is_stationary(self, timeseries, significance_level=0.05):
        if len(timeseries) < 20: # arbitrary minimum
            return False, 0.0
        
        try:
            result = adfuller(timeseries)
            p_value = result[1]
            return p_value < significance_level, p_value
        except:
            return False, 1.0
