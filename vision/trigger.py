import random
import time

from browser import open_in_guest_window


class TriggerState:
    def __init__(self) -> None:
        self.start_time = None
        self.alert_until = 0
        self.cooldown_until = 0


def update_trigger(
    state: TriggerState,
    person_detected: bool,
    phone_detected: bool,
    config: dict,
) -> None:
    now = time.time()
    in_cooldown = now < state.cooldown_until

    if person_detected and phone_detected and not in_cooldown:
        if state.start_time is None:
            state.start_time = now
        elif now - state.start_time >= config["trigger_seconds"]:
            url_to_open = random.choice(config["job_sites"])
            print(f"Opening job site: {url_to_open}")
            open_in_guest_window(url_to_open)
            state.alert_until = now + config["alert_duration_seconds"]
            state.cooldown_until = now + config["cooldown_seconds"]
            state.start_time = None
    else:
        state.start_time = None
