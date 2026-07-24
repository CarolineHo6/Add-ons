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
    "require_looking_down": True,
    "calibration_mode": False,
    "trigger_during_calibration": False,
    "phone_person_horizontal_margin_ratio": 0.15,
    "phone_min_person_y_ratio": 0.35,
    "phone_max_person_y_ratio": 1.08,
    "posture_detection_enabled": True,
    "require_pose_head_down": True,
    "fallback_to_phone_position_without_pose": True,
    "pose_min_detection_confidence": 0.5,
    "pose_min_tracking_confidence": 0.5,
    "head_down_score_threshold": 0.08,
    "slouch_shoulder_tilt_threshold": 0.12,
    "trigger_seconds": 1.0,
    "cooldown_seconds": 45.0,
    "alert_message": "Stop doomscrolling u bum bum",
    "alert_duration_seconds": 2.0,
    "frame_delay_seconds": 0.005,
    "log_path": "logs/phone_usage.jsonl",
    "lockdown_enabled": True,
    "lockdown_duration_seconds": 300.0,
    "daily_limit_mode_enabled": True,
    "daily_lockdown_tiers": [
        {"uses": 1, "duration_seconds": 300.0},
        {"uses": 2, "duration_seconds": 600.0},
        {"uses": 3, "duration_seconds": 1200.0},
    ],
    "lockdown_check_interval_seconds": 3.0,
    "blocked_apps": [
        "YouTube",
        "Instagram",
        "TikTok",
        "Discord",
        "Steam",
        "Spotify",
    ],
    "blocked_site_keywords": [
        "youtube.com",
        "youtu.be",
        "instagram.com",
        "tiktok.com",
        "twitter.com",
        "x.com",
        "reddit.com",
        "netflix.com",
        "twitch.tv",
        "discord.com",
    ],
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
