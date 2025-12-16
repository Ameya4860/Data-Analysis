import unittest
from src.analytics.core.ols_hedge import OLSHedgeRatio
import pandas as pd
import numpy as np

class TestAnalytics(unittest.TestCase):
    def test_ols_hedge(self):
        ols = OLSHedgeRatio()
        series_x = pd.Series(np.arange(10))
        series_y = pd.Series(np.arange(10) * 2 + 1) # y = 2x + 1
        beta = ols.calculate(series_y, series_x)
        self.assertAlmostEqual(beta, 2.0, places=5)

if __name__ == '__main__':
    unittest.main()
