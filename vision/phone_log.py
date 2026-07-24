import json
from datetime import datetime
from pathlib import Path

from config import resolve_project_path


def get_log_path(config: dict) -> Path:
    return Path(resolve_project_path(config["log_path"]))


def record_phone_use(config: dict, opened_url: str) -> int:
    log_path = get_log_path(config)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    event = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "opened_url": opened_url,
    }

    with log_path.open("a", encoding="utf-8") as log_file:
        log_file.write(json.dumps(event) + "\n")

    return count_phone_uses_today(config)


def count_phone_uses_today(config: dict) -> int:
    log_path = get_log_path(config)
    if not log_path.exists():
        return 0

    today = datetime.now().date()
    count = 0
    with log_path.open("r", encoding="utf-8") as log_file:
        for line in log_file:
            try:
                event = json.loads(line)
                event_time = datetime.fromisoformat(event["timestamp"])
            except (json.JSONDecodeError, KeyError, ValueError):
                continue
            if event_time.date() == today:
                count += 1
    return count
