import asyncio
import os
import sys
import yaml
import logging

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.ingestion.websocket_manager import WebSocketManager
from src.storage.sqlite_manager import SQLiteManager

# Config
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "../../config.yaml")
with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

db = SQLiteManager()

# Buffer to batch writes
TICK_BUFFER = []
BUFFER_SIZE = 1 # Set to 1 for immediate feedback in demo

async def process_tick(tick):
    global TICK_BUFFER, db
    TICK_BUFFER.append(tick)
    
    if len(TICK_BUFFER) >= BUFFER_SIZE:
        try:
            db.store_ticks(TICK_BUFFER)
            logging.info(f"Stored tick: {tick['symbol']} @ {tick['price']}")
            TICK_BUFFER = []
        except Exception as e:
            logging.error(f"Error storing ticks: {e}")

async def main():
    symbols = config['ingestion']['symbols']
    logging.info(f"Starting ingestion for: {symbols}")
    manager = WebSocketManager(None, symbols, process_tick)
    await manager.connect()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Stopping Ingestion Service...")
