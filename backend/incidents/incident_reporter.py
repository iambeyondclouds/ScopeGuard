
import uuid


class IncidentReporter:

    def __init__(self):
        self.incidents = []

    def report_incident(self, task, event, result):

        if result["decision"] != "BLOCKED":
            return None

        # Assign an ID to each incident
        incident_id = str(uuid.uuid4())[:8]

        # Classify the incident
        if any(name in event["target"].lower()
               for name in ["credentials", "private_key", ".env"]):
            severity = "HIGH"
        else:
            severity = "MEDIUM"

        incident = {
            "incident_id": incident_id,
            "task": task,
            "action": event["action"],
            "target": event["target"],
            "timestamp": event["timestamp"],
            "decision": result["decision"],
            "reason": result["reason"],
            "severity": severity,
            "status": "OPEN"
        }

        self.incidents.append(incident)

        return incident

    def get_incidents(self):
        return self.incidents

