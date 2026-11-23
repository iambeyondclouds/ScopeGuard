
from datetime import datetime


class RuntimeMonitor:
    def __init__(self):
        self.events = []

    def record_activity(self, action, target):
        event = {
            "action": action,
            "target": target,
            "timestamp": datetime.now().isoformat(),
            "status": "recorded"
        }

        self.events.append(event)
        return event

    def get_events(self):
        return self.events

