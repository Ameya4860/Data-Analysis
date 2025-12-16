import sqlite3
import pandas as pd
import os
import yaml

# Config
CONFIG_PATH = os.path.join("QuantAnalyticsDashboard", "config.yaml")
with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

DB_PATH = os.path.join("QuantAnalyticsDashboard", config["database"]["db_path"])

def check_db():
    if not os.path.exists(DB_PATH):
        print(f"DB not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    
    # Check Ticks
    try:
        df_ticks = pd.read_sql("SELECT * FROM ticks ORDER BY id DESC LIMIT 5", conn)
        print("\n--- Last 5 Ticks ---")
        print(df_ticks)
        print(f"Total Ticks: {pd.read_sql('SELECT COUNT(*) FROM ticks', conn).iloc[0,0]}")
    except Exception as e:
        print(f"Error reading ticks: {e}")

    # Check OHLCV 1s
    try:
        df_1s = pd.read_sql("SELECT * FROM ohlcv_1s ORDER BY timestamp DESC LIMIT 5", conn)
        print("\n--- Last 5 1s Bars ---")
        print(df_1s)
        print(f"Total 1s Bars: {pd.read_sql('SELECT COUNT(*) FROM ohlcv_1s', conn).iloc[0,0]}")
    except Exception as e:
        print(f"Error reading 1s: {e}")

    conn.close()

if __name__ == "__main__":
    check_db()
