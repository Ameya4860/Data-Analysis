import asyncio
import websockets
import json
import logging
from datetime import datetime

class WebSocketManager:
    def __init__(self, urls, symbols, callback):
        self.urls = urls # List of URLs or single URL? Binance usually single stream URL
        self.symbols = symbols
        self.callback = callback
        self.running = False
        self.ws = None

    async def connect(self):
        self.running = True
        # Construct stream URL
        # fstream.binance.com/stream?streams=btcusdt@aggTrade/ethusdt@aggTrade
        base_url = "wss://fstream.binance.com/stream?streams="
        streams = [f"{s.lower()}@aggTrade" for s in self.symbols]
        url = base_url + "/".join(streams)
        
        while self.running:
            try:
                async with websockets.connect(url) as ws:
                    self.ws = ws
                    logging.info("Connected to Binance WebSocket")
                    while self.running:
                        msg = await ws.recv()
                        data = json.loads(msg)
                        if 'data' in data:
                            # Parse aggTrade
                            # {"e":"aggTrade","E":123456789,"s":"BTCUSDT","p":"0.001","q":"100",...}
                             payload = data['data']
                             tick = {
                                 'timestamp': datetime.utcfromtimestamp(payload['E'] / 1000.0), # Force UTC for consistency
                                 'symbol': payload['s'],
                                 'price': float(payload['p']),
                                 'quantity': float(payload['q'])
                             }
                             if self.callback:
                                 await self.callback(tick)
            except Exception as e:
                logging.error(f"WebSocket Connection Error: {e}")
                await asyncio.sleep(5) # Reconnect delay

    def stop(self):
        self.running = False
        if self.ws:
            asyncio.create_task(self.ws.close())
