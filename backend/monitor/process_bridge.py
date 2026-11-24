
import json
import subprocess
from pathlib import Path


def get_process_info(pid):

    # Find the compiled C++ program
    project_root = Path(__file__).resolve().parents[2]
    monitor_path = project_root / "backend/monitor/cpp/process_monitor"

    try:
        result = subprocess.run(
            [str(monitor_path), str(pid)],
            capture_output=True,
            text=True,
            check=True
        )

        # Convert C++ JSON output into a Python dictionary
        process_info = json.loads(result.stdout)

        return process_info

    except subprocess.CalledProcessError as error:
        return {
            "error": error.stderr.strip()
        }

    except (OSError, json.JSONDecodeError) as error:
        return {
            "error": str(error)
        }

