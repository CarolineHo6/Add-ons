# Add-ons

A webcam-based phone-use detector that watches for a person looking down at a phone, opens a random job/career site when phone use is detected, logs each trigger, sends a notification, and temporarily locks down distracting apps and websites.

## Features

- Detects people and cell phones in the webcam feed with YOLOv8.
- Uses phone position relative to the detected person to decide whether the phone is likely being used.
- Optionally uses MediaPipe pose landmarks to require a head-down posture before triggering.
- Shows a live OpenCV window with detection boxes and status information.
- Provides calibration mode for tuning phone-zone and posture thresholds.
- Opens a random configured job/career site in a Chrome guest window after a trigger.
- Tracks daily phone-use triggers in `logs/phone_usage.jsonl`.
- Supports escalating lockdown durations based on how many times the detector has triggered today.
- Sends macOS notifications with the trigger count and lockdown duration.
- On macOS, quits configured distracting apps and closes Chrome/Safari tabs matching blocked site keywords during lockdown.
- Falls back gracefully when MediaPipe is not installed or pose detection is unavailable.

## Requirements

- Python 3.10 or newer recommended.
- A working webcam.
- macOS for app/tab lockdown enforcement and desktop notifications.
- Google Chrome recommended for guest-window job-site launches.
- Python packages:
  - `opencv-python`
  - `torch`
  - `ultralytics`
  - `mediapipe` optional, but recommended for posture detection

The model file `yolov8n.pt` is intentionally ignored by git because it is a large weight file. After cloning the repo, download or copy that file into the project root, or update `vision/config.json` to point at another YOLO model.

## Copy The Repo

Clone from GitHub:

```bash
git clone https://github.com/CarolineHo6/Add-ons.git
cd Add-ons
```

If you are copying the current local folder instead of cloning it, copy the whole `Add-ons` folder. Keep the same structure:

```text
Add-ons/
  assets/
  vision/
  yolov8n.pt
```

If `yolov8n.pt` is missing after cloning, download it with:

```bash
curl -L -o yolov8n.pt https://github.com/ultralytics/assets/releases/download/v8.3.0/yolov8n.pt
```

## Install

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install opencv-python torch ultralytics mediapipe
```

On macOS, allow Terminal, iTerm, VS Code, or whatever app you run this from to access the camera when prompted.

## Run

From the repo root:

```bash
source .venv/bin/activate
python vision/main.py
```

Alternative launcher:

```bash
python vision/Vision.py
```

Keyboard controls in the detector window:

- `c`: toggle calibration mode.
- `q`: quit.

## Configuration

Edit `vision/config.json` to customize behavior.

Important options:

- `model_path`: YOLO model path, relative to the repo root unless absolute.
- `camera_index`: webcam index. Use `0` for the default camera, or try `1`, `2`, etc. for other cameras.
- `device`: inference device, usually `cpu`. Use a supported accelerator only if your PyTorch install supports it.
- `person_confidence` and `phone_confidence`: detection confidence thresholds.
- `require_looking_down`: requires the phone/person geometry check before triggering.
- `posture_detection_enabled`: enables MediaPipe pose analysis.
- `require_pose_head_down`: requires pose-based head-down detection when pose is available.
- `fallback_to_phone_position_without_pose`: lets the app keep working if pose detection is unavailable.
- `trigger_seconds`: how long the trigger condition must stay true before action is taken.
- `cooldown_seconds`: delay before another trigger can happen.
- `job_sites`: URLs that can be opened after a trigger.
- `lockdown_enabled`: turns lockdown enforcement on or off.
- `blocked_apps`: macOS apps to quit during lockdown.
- `blocked_site_keywords`: browser URL keywords to close in Chrome/Safari tabs.
- `daily_lockdown_tiers`: lockdown durations based on the number of triggers today.
- `log_path`: JSONL file where phone-use events are recorded.

## Logs

Phone-use events are written to:

```text
logs/phone_usage.jsonl
```

Each line is a JSON object with a timestamp and the job site that was opened.

## Troubleshooting

- If the camera window is blank, check camera permissions and try a different `camera_index`.
- If `yolov8n.pt` cannot be found, put the model file in the repo root or update `model_path`.
- If posture detection says unavailable, install `mediapipe` or set `posture_detection_enabled` to `false`.
- If lockdown does not close apps or browser tabs, make sure you are on macOS and that automation permissions allow AppleScript control.
- If PyTorch installation fails, install the PyTorch build recommended for your machine from the official PyTorch install selector, then rerun the remaining package installs.
