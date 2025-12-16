import pandas as pd
import numpy as np

class BacktestEngine:
    def run_mean_reversion(self, series_spread, zscore, entry_threshold=2.0, exit_threshold=0.0):
        """
        Simulate trading:
        Short Spread when Z > entry
        Exit when Z crosses exit (0)
        Long Spread when Z < -entry
        Exit when Z crosses exit (0)
        
        Returns: PnL Series
        """
        positions = pd.Series(0, index=zscore.index)
        
        # 1 = Long Spread, -1 = Short Spread
        current_pos = 0
        
        for i in range(1, len(zscore)):
            z = zscore.iloc[i]
            
            if current_pos == 0:
                if z > entry_threshold:
                    current_pos = -1 # Short
                elif z < -entry_threshold:
                    current_pos = 1 # Long
            elif current_pos == 1:
                # Long position, exit if Z >= 0
                if z >= exit_threshold:
                    current_pos = 0
            elif current_pos == -1:
                # Short position, exit if Z <= 0
                if z <= -exit_threshold:
                    current_pos = 0
            
            positions.iloc[i] = current_pos
        
        # Calculate PnL
        # PnL = Position * Change in Spread
        # Position is established at Close[i], so return affects Close[i+1].
        # We shift position by 1 to align with returns.
        spread_ret = series_spread.diff()
        pnl = positions.shift(1) * spread_ret
        cumulative_pnl = pnl.cumsum()
        
        return cumulative_pnl.fillna(0)
