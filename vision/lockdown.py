import platform
import subprocess
import time


def start_lockdown(state, config: dict, now: float | None = None) -> None:
    if not config["lockdown_enabled"]:
        return

    current_time = time.time() if now is None else now
    duration_seconds = get_lockdown_duration(config, state.phone_uses_today)
    state.current_lockdown_duration_seconds = duration_seconds
    state.lockdown_until = current_time + duration_seconds
    state.last_lockdown_enforced = 0
    print(
        f"Lockdown active for {duration_seconds:.0f} seconds "
        f"after {state.phone_uses_today} phone use(s) today."
    )


def get_lockdown_duration(config: dict, phone_uses_today: int) -> float:
    if not config["daily_limit_mode_enabled"]:
        return config["lockdown_duration_seconds"]

    duration_seconds = config["lockdown_duration_seconds"]
    sorted_tiers = sorted(config["daily_lockdown_tiers"], key=lambda tier: tier["uses"])
    for tier in sorted_tiers:
        if phone_uses_today >= tier["uses"]:
            duration_seconds = tier["duration_seconds"]
    return duration_seconds


def lockdown_remaining(state) -> float:
    return max(state.lockdown_until - time.time(), 0)


def enforce_lockdown(state, config: dict) -> None:
    if not config["lockdown_enabled"] or lockdown_remaining(state) <= 0:
        return

    now = time.time()
    if now - state.last_lockdown_enforced < config["lockdown_check_interval_seconds"]:
        return

    state.last_lockdown_enforced = now
    if platform.system() == "Darwin":
        enforce_macos_lockdown(config)
    else:
        print("Lockdown enforcement is currently implemented for macOS only.")


def enforce_macos_lockdown(config: dict) -> None:
    for app_name in config["blocked_apps"]:
        subprocess.Popen(
            ["osascript", "-e", f'tell application "{app_name}" to quit'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    close_blocked_browser_tabs("Google Chrome", config["blocked_site_keywords"])
    close_blocked_browser_tabs("Safari", config["blocked_site_keywords"])


def close_blocked_browser_tabs(browser_name: str, blocked_keywords: list[str]) -> None:
    if not blocked_keywords:
        return

    keyword_checks = " or ".join(
        f'pageUrl contains "{escape_applescript_text(keyword)}"'
        for keyword in blocked_keywords
    )
    script = f"""
tell application "{browser_name}"
    if it is running then
        repeat with browserWindow in windows
            repeat with browserTab in tabs of browserWindow
                set pageUrl to URL of browserTab
                if {keyword_checks} then close browserTab
            end repeat
        end repeat
    end if
end tell
"""
    subprocess.Popen(
        ["osascript", "-e", script],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def escape_applescript_text(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')
