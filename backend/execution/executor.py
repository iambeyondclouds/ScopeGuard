
from pathlib import Path


class ControlledExecutor:

    def __init__(self, policy, monitor, policy_engine):
        self.policy = policy
        self.monitor = monitor
        self.policy_engine = policy_engine

        project_root = Path(__file__).resolve().parents[2]
        self.workspace = project_root / "workspace"

    def execute(self, action, target, content=None):

        # Record the attempted activity
        event = self.monitor.record_activity(action, target)

        # Check the security policy
        result = self.policy_engine.check_activity(
            self.policy, event
        )

        if result["decision"] == "BLOCKED":
            event["status"] = "blocked"
            return result

        # Only file operations are supported
        if action not in ["read_file", "write_file"]:
            event["status"] = "blocked"
            return {
                "decision": "BLOCKED",
                "reason": "Unsupported operation."
            }

        # Validate the file path
        file_path = (self.workspace / target).resolve()

        if not file_path.is_relative_to(self.workspace.resolve()):
            event["status"] = "blocked"
            return {
                "decision": "BLOCKED",
                "reason": "File access outside workspace is prohibited."
            }

        try:
            if action == "read_file":
                file_content = file_path.read_text()

                event["status"] = "allowed"

                return {
                    "decision": "ALLOWED",
                    "reason": "File read successfully.",
                    "content": file_content
                }

            if action == "write_file":

                if not isinstance(content, str):
                    return {
                        "decision": "ERROR",
                        "reason": "File content must be text."
                    }

                if not file_path.parent.is_dir():
                    return {
                        "decision": "ERROR",
                        "reason": "Target directory does not exist."
                    }

                file_path.write_text(content)

                event["status"] = "allowed"

                return {
                    "decision": "ALLOWED",
                    "reason": "File written successfully."
                }

        except OSError as error:
            event["status"] = "error"

            return {
                "decision": "ERROR",
                "reason": str(error)
            }

