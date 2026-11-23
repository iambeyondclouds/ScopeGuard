
def analyze_task(user_task):
    user_task = user_task.strip().lower()

    policy = {
        "task": user_task,
        "allowed_actions": [],
        "blocked_actions": [
            "read_credentials",
            "access_private_keys",
            "send_data_externally"
        ],
        "allowed_paths": ["project/"],
        "allow_network": False
    }

    if "fix" in user_task or "edit" in user_task:
        policy["allowed_actions"] = [
            "read_files",
            "write_files",
            "run_tests"
        ]

    elif "read" in user_task or "analyse" in user_task:
        policy["allowed_actions"] = [
            "read_files"
        ]

    else:
        policy["allowed_actions"] = [
            "read_files"
        ]

    return policy

