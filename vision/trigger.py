import random
import time

from browser import open_in_guest_window
from phone_log import count_phone_uses_today, record_phone_use


class TriggerState:
    def __init__(self, config: dict) -> None:
        self.start_time = None
        self.alert_until = 0
        self.cooldown_until = 0
        self.phone_uses_today = count_phone_uses_today(config)


def update_trigger(
    state: TriggerState,
    person_detected: bool,
    phone_detected: bool,
    looking_down_at_phone: bool,
    config: dict,
) -> None:
    now = time.time()
    in_cooldown = now < state.cooldown_until
    if config["calibration_mode"] and not config["trigger_during_calibration"]:
        state.start_time = None
        return

    trigger_detected = person_detected and phone_detected
    if config["require_looking_down"]:
        trigger_detected = trigger_detected and looking_down_at_phone

    if trigger_detected and not in_cooldown:
        if state.start_time is None:
            state.start_time = now
        elif now - state.start_time >= config["trigger_seconds"]:
            url_to_open = random.choice(config["job_sites"])
            print(f"Opening job site: {url_to_open}")
            open_in_guest_window(url_to_open)
            state.phone_uses_today = record_phone_use(config, url_to_open)
            print(f"Phone uses today: {state.phone_uses_today}")
            state.alert_until = now + config["alert_duration_seconds"]
            state.cooldown_until = now + config["cooldown_seconds"]
            state.start_time = None
    else:
        state.start_time = None
