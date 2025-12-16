import pandas as pd
from collections import defaultdict
import threading

class InMemoryBuffer:
    def __init__(self, max_size=10000):
        self.max_size = max_size
        self._buffers = defaultdict(list)
        self._lock = threading.Lock()

    def add_tick(self, tick):
        """
        tick: dict with keys timestamp, symbol, price, quantity
        """
        symbol = tick['symbol']
        with self._lock:
            self._buffers[symbol].append(tick)
            if len(self._buffers[symbol]) > self.max_size:
                self._buffers[symbol].pop(0)

    def get_dataframe(self, symbol):
        with self._lock:
            data = list(self._buffers.get(symbol, []))
        
        if not data:
            return pd.DataFrame(columns=['timestamp', 'symbol', 'price', 'quantity'])
        
        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['price'] = df['price'].astype(float)
        df['quantity'] = df['quantity'].astype(float)
        return df

    def get_all_symbols(self):
        with self._lock:
            return list(self._buffers.keys())
