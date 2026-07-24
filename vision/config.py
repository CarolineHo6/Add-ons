import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = Path(__file__).with_name("config.json")
WINDOW_NAME = "YOLO Phone Detector"
DEFAULT_CONFIG = {
    "model_path": "yolov8n.pt",
    "camera_index": 0,
    "device": "cpu",
    "person_confidence": 0.45,
    "phone_confidence": 0.45,
    "trigger_seconds": 1.0,
    "cooldown_seconds": 45.0,
    "alert_message": "Stop doomscrolling u bum bum",
    "alert_duration_seconds": 2.0,
    "frame_delay_seconds": 0.005,
    "job_sites": [
        "https://apply.starbucks.com/careers",
        "https://careers.baskinrobbins.com",
        "https://botcamp.org/jobs/",
        "https://www.realfruitbubbletea.com/career.html",
        "https://chatime.ca/careers/",
        "https://corp.cineplex.com/careers",
        "https://careers.popeyes.com",
        "https://www.bingzcanada.com/join",
        "https://careers.mcdonalds.com",
        "https://www.uniqlo.com/my/en/spl/careers",
        "https://mollyteaca.com/career/",
    ],
}


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        return DEFAULT_CONFIG.copy()

    with CONFIG_PATH.open("r", encoding="utf-8") as config_file:
        loaded_config = json.load(config_file)

    config = DEFAULT_CONFIG.copy()
    config.update(loaded_config)
    if not config["job_sites"]:
        raise ValueError("config.json must include at least one job site.")
    return config


def resolve_project_path(path_value: str) -> str:
    path = Path(path_value)
    if path.is_absolute():
        return str(path)
    return str(BASE_DIR / path)
