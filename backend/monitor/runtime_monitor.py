
from datetime import datetime


class RuntimeMonitor:

    def __init__(self):
        self.events = []

    def record_activity(self, action, target, process_info=None):

        event = {
            "action": action,
            "target": target,
            "timestamp": datetime.now().isoformat(),
            "status": "recorded",
            "process": process_info
        }

        self.events.append(event)

        return event

    def get_events(self):
        return self.events

