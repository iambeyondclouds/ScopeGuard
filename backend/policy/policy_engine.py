
from pathlib import PurePosixPath


class PolicyEngine:

    def check_activity(self, policy, event):
        action = event["action"]
        target = event["target"]

        # Match activity names with policy permissions
        if action == "read_file":
            permission = "read_files"
        elif action == "write_file":
            permission = "write_files"
        elif action == "run_command":
            permission = "run_tests"
        elif action == "send_data":
            permission = "send_data_externally"
        else:
            return {
                "decision": "BLOCKED",
                "reason": "Unknown activity."
            }

        # Check for sensitive files
        sensitive_files = [
            "credentials",
            "private_key",
            ".env"
        ]

        for name in sensitive_files:
            if name in target.lower():
                return {
                    "decision": "BLOCKED",
                    "reason": "Access to a sensitive resource is prohibited."
                }

        # Check explicitly blocked actions
        if permission in policy["blocked_actions"]:
            return {
                "decision": "BLOCKED",
                "reason": "This action is blocked by policy."
            }

        # Check network permission
        if permission == "send_data_externally":
            if not policy["allow_network"]:
                return {
                    "decision": "BLOCKED",
                    "reason": "Network access is not permitted."
                }

        # Check allowed actions
        if permission not in policy["allowed_actions"]:
            return {
                "decision": "BLOCKED",
                "reason": "This action is not allowed."
            }

        # Check file paths
        if action == "read_file" or action == "write_file":
            path = PurePosixPath(target)

            if path.is_absolute() or ".." in path.parts:
                return {
                    "decision": "BLOCKED",
                    "reason": "Unsafe file path."
                }

            if len(path.parts) < 2 or path.parts[0] != "project":
                return {
                    "decision": "BLOCKED",
                    "reason": "File is outside the project directory."
                }

        return {
            "decision": "ALLOWED",
            "reason": "Action is permitted by policy."
        }

