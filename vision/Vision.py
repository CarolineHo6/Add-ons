import random
import cv2
from ultralytics import YOLO
import time
import webbrowser
import subprocess
import platform
import shutil
import simpleaudio as sa

# Load YOLOv8 small model (pretrained on COCO)
model = YOLO("yolov8n.pt")  

alert_wave = sa.WaveObject.from_wave_file("assets/alert.wav")
cap = cv2.VideoCapture(0)  # webcam
start_time = None
threshold_seconds = 2  # how long face+phone must persist before alerting
alert_message = "You've been on your phone too long! Check job applications!"
alert_duration = 2  # seconds the on-screen alert stays visible
alert_until = 0
triggered = False  # ensure URLs open only once per session

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
    except Exception:
        webbrowser.open_new(url)


while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame, verbose=False)[0]  # run YOLO detection on the frame
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
            try:
                open_in_guest_window(job_sites[random.randint(0,10)])
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

    cv2.imshow("YOLO Phone Detector", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
