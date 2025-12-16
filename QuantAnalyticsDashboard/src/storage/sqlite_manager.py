import sqlite3
import pandas as pd
from datetime import datetime
import os
import yaml

# Load config
CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config.yaml")
with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), config["database"]["db_path"])

class SQLiteManager:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Enable WAL mode for concurrency
        try:
            cursor.execute("PRAGMA journal_mode=WAL;")
        except:
            pass
        
        # Ticks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ticks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                symbol TEXT,
                price REAL,
                quantity REAL
            )
        """)
        
        # Resampled OHLCV tables for different timeframes
        for tf in ["1s", "1m", "5m"]:
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS ohlcv_{tf} (
                    timestamp DATETIME,
                    symbol TEXT,
                    open REAL,
                    high REAL,
                    low REAL,
                    close REAL,
                    volume REAL,
                    PRIMARY KEY (timestamp, symbol)
                )
            """)
        
        conn.commit()
        conn.close()

    def store_ticks(self, ticks: list):
        if not ticks:
            return
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.executemany("""
            INSERT INTO ticks (timestamp, symbol, price, quantity)
            VALUES (?, ?, ?, ?)
        """, [(t['timestamp'], t['symbol'], t['price'], t['quantity']) for t in ticks])
        conn.commit()
        conn.close()

    def store_ohlcv(self, df: pd.DataFrame, timeframe: str):
        if df.empty:
            return
        conn = self.get_connection()
        table_name = f"ohlcv_{timeframe}"
        try:
             df.to_sql(table_name, conn, if_exists='append', index=False)
        except Exception:
            pass 
        conn.close()

    def fetch_recent_data(self, symbol, timeframe="1m", limit=1000):
        conn = self.get_connection()
        table_name = f"ohlcv_{timeframe}" if timeframe != "tick" else "ticks"
        
        try:
            cursor = conn.cursor()
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
            if not cursor.fetchone():
                conn.close()
                return pd.DataFrame(columns=['timestamp', 'symbol', 'price', 'quantity', 'open', 'high', 'low', 'close', 'volume'])
        except:
             conn.close()
             return pd.DataFrame()

        query = f"SELECT * FROM {table_name} WHERE symbol = ? ORDER BY timestamp DESC LIMIT ?"
        df = pd.read_sql(query, conn, params=(symbol, limit))
        conn.close()
        
        if not df.empty and 'timestamp' in df.columns:
            # Robust datetime conversion
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            
        return df.iloc[::-1] # Return chronological

if __name__ == "__main__":
    db = SQLiteManager()
    print(f"Database initialized at {db.db_path}")
