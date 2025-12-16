import time
import pandas as pd
import os
import sys
import yaml
import logging
from datetime import datetime, timedelta

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
from src.storage.sqlite_manager import SQLiteManager

# Config & Logging
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "../../../config.yaml")
with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

db = SQLiteManager()
# FIX: Normalize to Uppercase because Binance stores as BTCUSDT
symbols = [s.upper() for s in config['ingestion']['symbols']]

def resample_and_store():
    conn = db.get_connection()
    
    # Process each symbol independently
    for symbol in symbols:
        try:
            # 1. Fetch raw ticks
            query = "SELECT timestamp, price, quantity FROM ticks WHERE symbol = ? ORDER BY id DESC LIMIT 20000"
            df = pd.read_sql(query, conn, params=(symbol,))
            
            if df.empty:
                continue

            # 2. Normalize Timestamp
            # Use format='mixed' to handle varied SQLite timestamp strings (ISO8601, etc.)
            df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True, format='mixed') 
            df.set_index('timestamp', inplace=True)
            df.sort_index(inplace=True)

            # 3. Resample
            # We process 3 timeframes
            for tf, rule in [('1s', '1S'), ('1m', '1T'), ('5m', '5T')]:
                ohlcv = df['price'].resample(rule).ohlc()
                volume = df['quantity'].resample(rule).sum()
                ohlcv['volume'] = volume
                ohlcv['symbol'] = symbol
                
                # Drop incomplete (NaN) intervals if any, though OHLC handles it.
                ohlcv.dropna(inplace=True)
                
                if ohlcv.empty:
                    continue
                    
                ohlcv.reset_index(inplace=True)
                
                # 4. Atomic Upsert/Replace
                cutoff = datetime.utcnow() - timedelta(minutes=10) # Safe buffer
                # Ensure cutoff is offset-aware UTC
                if ohlcv['timestamp'].dt.tz is None:
                     ohlcv['timestamp'] = ohlcv['timestamp'].dt.tz_localize('UTC')
                cutoff = cutoff.replace(tzinfo=ohlcv['timestamp'].dt.tz)
                
                ohlcv_to_write = ohlcv[ohlcv['timestamp'] >= cutoff]
                
                if not ohlcv_to_write.empty:
                    min_ts = ohlcv_to_write['timestamp'].min()
                    
                    # Transaction
                    cursor = conn.cursor()
                    table = f"ohlcv_{tf}"
                    cursor.execute(f"DELETE FROM {table} WHERE symbol = ? AND timestamp >= ?", (symbol, str(min_ts)))
                    ohlcv_to_write.to_sql(table, conn, if_exists='append', index=False)
                    conn.commit()
                    
        except Exception as e:
            logging.error(f"Error processing {symbol}: {e}")

    conn.close()

if __name__ == "__main__":
    logging.info("Starting Production-Grade Resampler (Mixed Date Format Fixed)...")
    while True:
        try:
            resample_and_store()
        except Exception as e:
            logging.error(f"Resampler loop crashed: {e}")
        time.sleep(0.5) 
