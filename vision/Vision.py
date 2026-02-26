import random
import cv2
from ultralytics import YOLO
import time
import webbrowser
import subprocess
import platform
import shutil
import simpleaudio as sa
import sys
import torch
import traceback


torch.set_num_threads(1)

# Load YOLOv8 small model (pretrained on COCO)
model = YOLO("yolov8n.pt")  

alert_wave = sa.WaveObject.from_wave_file("assets/alert.wav")
cv2.namedWindow("YOLO Phone Detector", cv2.WINDOW_NORMAL)
cap = cv2.VideoCapture(0)  # webcam
start_time = None
threshold_seconds = 1  # how long face+phone must persist before alerting
alert_message = "You've been on your phone too long! Check job applications!"
alert_duration = 2  # seconds the on-screen alert stays visible
alert_until = 0
triggered = False  # ensure URLs open only once per session
chrome_bin = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
guest_flags = ["--guest", "--new-window", "--no-first-run", "--no-default-browser-check"]


def reset_camera():
    """Release and reopen the default camera, returns a fresh capture."""
    cap.release()
    time.sleep(0.05)
    return cv2.VideoCapture(0)

# Add your job application URLs here
job_sites = [
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
    "https://mollyteaca.com/career/"
]

def launch_url_in_thread(url, chrome_bin, guest_flags):
    """Launch a URL in Chrome asynchronously in a separate thread."""
    subprocess.Popen(
        [chrome_bin, *guest_flags, url],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True
    )

# dont need anymore cause im using threading
def open_in_guest_window(url: str) -> None:
    """Open the URL in a guest-profile Chrome window without the profile chooser."""

    system = platform.system()
    guest_flags = ["--guest", "--new-window", "--no-first-run", "--no-default-browser-check"]

    try:
        if system == "Darwin":
            chrome_bin = (
                shutil.which("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
                or shutil.which("google-chrome")
                or shutil.which("chrome")
            )
            if chrome_bin:
                subprocess.Popen([chrome_bin, *guest_flags, url])
            else:
                subprocess.Popen(["open", "-a", "Google Chrome", url])
        elif system == "Windows":
            subprocess.Popen([
                "cmd", "/c", "start", "", "chrome", *guest_flags, url
            ])
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
        except Exception as e:
            print(f"Secondary fallback failed: {e}")


while True:
    try:
        if not cap.isOpened():
            cap = reset_camera()
            continue

        ret, frame = cap.read()
        if not ret:
            print("Frame grab failed, retrying...")
            time.sleep(0.1)
            continue

        results = model.predict(source=frame, verbose=False, device='cpu')[0]  # run YOLO detection on the frame
        detected_classes = [results.names[int(box.cls)] for box in results.boxes]
        
        # Check if both a person (for face) and a phone are detected
        face_detected = "person" in detected_classes
        phone_detected = "cell phone" in detected_classes

        if face_detected and phone_detected and not triggered:
            if not start_time:
                start_time = time.time()
            elif time.time() - start_time >= threshold_seconds:
                alert_until = time.time() + alert_duration
                start_time = None  # reset timer

                try:
                    alert_wave.play()   # plays sound without blocking
                except Exception as exc:
                    print(f"Audio play failed: {exc}")

                # Open job application URL in a new guest-profile Chrome window
                url_to_open = job_sites[random.randint(0, 10)]
                print(f"Opening job site: {url_to_open}")
                try:
                    open_in_guest_window(url_to_open)
                except Exception as exc:
                    print(f"Browser launch failed: {exc}")
                triggered = True  # mark as triggered for this session
        else:
            start_time = None
            triggered = False  # reset so it can trigger next time

        # Draw bounding boxes
        for box in results.boxes:
            cls_id = int(box.cls)
            cls_name = results.names[cls_id]
            conf = float(box.conf[0])  # <-- get confidence

            x1, y1, x2, y2 = map(int, box.xyxy[0])
            color = (0, 255, 0) if cls_name == "person" else (0, 0, 255)

            # Draw rectangle
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

            # Draw class name only
            cv2.putText(frame, cls_name, (x1, y1 - 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

            # Draw class name + confidence
            cv2.putText(frame, f"{cls_name} {conf:.2f}", (x1, y1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # Show the alert text on the frame
        if time.time() < alert_until:
            cv2.putText(
                frame,
                alert_message,
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 255),
                2,
            )

        if cv2.getWindowProperty("YOLO Phone Detector", cv2.WND_PROP_VISIBLE) < 1:
            cv2.namedWindow("YOLO Phone Detector", cv2.WINDOW_NORMAL)

        cv2.imshow("YOLO Phone Detector", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        time.sleep(0.005)
    except KeyboardInterrupt:
        print("KeyboardInterrupt received, exiting loop.")
        break
    except Exception as exc:
        print(f"Loop error, recovering camera: {exc}", file=sys.stderr)
        traceback.print_exc()
        cap = reset_camera()
        continue

cap.release()
cv2.destroyAllWindows()
print("Exited main loop; resources released.")
