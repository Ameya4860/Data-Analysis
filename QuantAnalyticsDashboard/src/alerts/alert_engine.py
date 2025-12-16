from datetime import datetime

class AlertEngine:
    def __init__(self, threshold=2.0):
        self.threshold = threshold
        self.alerts = []

    def check_zscore(self, symbol_pair, zscore_value):
        if abs(zscore_value) > self.threshold:
            alert = {
                'timestamp': datetime.now(),
                'pair': symbol_pair,
                'value': zscore_value,
                'message': f"Z-Score deviation: {zscore_value:.2f} > {self.threshold}"
            }
            self.alerts.append(alert)
            return alert
        return None

    def get_latest_alerts(self, limit=5):
        return self.alerts[-limit:]
