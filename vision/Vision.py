import random
import cv2
from ultralytics import YOLO
import time
import webbrowser

# Load YOLOv8 small model (pretrained on COCO)
model = YOLO("yolov8n.pt")  

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

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame, verbose=False)[0]  # run YOLO detection on the frame
    detected_classes = [results.names[int(box.cls)] for box in results.boxes]
    
    # Check if both a person (for face) and a phone are detected
    face_detected = "person" in detected_classes
    phone_detected = "cell phone" in detected_classes

    if face_detected and phone_detected:
        if not start_time:
            start_time = time.time()
        elif time.time() - start_time >= threshold_seconds:
            alert_until = time.time() + alert_duration
            start_time = None  # reset timer

            # Open job application URLs
            #for site in job_sites:
            webbrowser.open_new(job_sites[random.randint(0,10)])
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

