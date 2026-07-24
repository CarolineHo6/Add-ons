import platform
import subprocess


def send_notification(config: dict, phone_uses_today: int, lockdown_seconds: float) -> None:
    if not config["notifications_enabled"]:
        return

    title = config["notification_title"]
    message = config["notification_message"].format(
        phone_uses_today=phone_uses_today,
        lockdown_minutes=round(lockdown_seconds / 60),
        lockdown_seconds=round(lockdown_seconds),
    )

    if platform.system() == "Darwin":
        send_macos_notification(title, message)
    else:
        print(f"{title}: {message}")


def send_macos_notification(title: str, message: str) -> None:
    script = (
        f'display notification "{escape_applescript_text(message)}" '
        f'with title "{escape_applescript_text(title)}"'
    )
    subprocess.Popen(
        ["osascript", "-e", script],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def escape_applescript_text(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')
