import platform
from pathlib import Path
import shutil
import subprocess
import webbrowser


def open_in_guest_window(url: str) -> None:
    system = platform.system()
    guest_flags = ["--guest", "--new-window", "--no-first-run", "--no-default-browser-check"]

    try:
        if system == "Darwin":
            chrome_bin = (
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
                if Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome").exists()
                else shutil.which("google-chrome")
                or shutil.which("chrome")
            )
            if chrome_bin:
                subprocess.Popen([chrome_bin, *guest_flags, url])
            else:
                subprocess.Popen(["open", "-a", "Google Chrome", url])
        elif system == "Windows":
            subprocess.Popen(["cmd", "/c", "start", "", "chrome", *guest_flags, url])
        else:
            chrome_bin = (
                shutil.which("google-chrome")
                or shutil.which("chrome")
                or shutil.which("chromium-browser")
                or shutil.which("chromium")
            )
            if chrome_bin:
                subprocess.Popen([chrome_bin, *guest_flags, url])
            else:
                webbrowser.open_new(url)
    except Exception as exc:
        print(f"Browser launch failed, fallback: {exc}")
        try:
            webbrowser.open_new(url)
        except Exception as secondary_exc:
            print(f"Secondary fallback failed: {secondary_exc}")
