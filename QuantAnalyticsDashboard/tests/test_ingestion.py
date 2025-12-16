import unittest
import asyncio
from src.ingestion.websocket_manager import WebSocketManager

class TestIngestion(unittest.TestCase):
    def test_ws_init(self):
        # Just testing initialization, not actual connection
        ws = WebSocketManager("ws://test", ["btcusdt"], None)
        self.assertEqual(ws.symbols, ["btcusdt"])

if __name__ == '__main__':
    unittest.main()
