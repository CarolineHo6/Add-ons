import time

import cv2


def draw_detections(frame, results, config: dict) -> None:
    for box in results.boxes:
        cls_id = int(box.cls)
        cls_name = results.names[cls_id]
        confidence = float(box.conf[0])
        if cls_name == "person" and confidence < config["person_confidence"]:
            continue
        if cls_name == "cell phone" and confidence < config["phone_confidence"]:
            continue

        x1, y1, x2, y2 = map(int, box.xyxy[0])
        color = (0, 255, 0) if cls_name == "person" else (0, 0, 255)
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(
            frame,
            f"{cls_name} {confidence:.2f}",
            (x1, max(y1 - 8, 20)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            color,
            2,
        )


def draw_status(
    frame,
    person_detected: bool,
    phone_detected: bool,
    start_time: float | None,
    cooldown_until: float,
    alert_until: float,
    config: dict,
) -> None:
    now = time.time()
    elapsed = 0 if start_time is None else now - start_time
    trigger_remaining = max(config["trigger_seconds"] - elapsed, 0)
    cooldown_remaining = max(cooldown_until - now, 0)

    status_lines = [
        f"Person: {'yes' if person_detected else 'no'}",
        f"Phone: {'yes' if phone_detected else 'no'}",
        f"Trigger in: {trigger_remaining:.1f}s",
        f"Cooldown: {cooldown_remaining:.0f}s",
    ]

    for index, line in enumerate(status_lines):
        cv2.putText(
            frame,
            line,
            (20, 28 + index * 24),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2,
        )

    if now < alert_until:
        cv2.putText(
            frame,
            config["alert_message"],
            (20, 140),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 0, 255),
            2,
        )
