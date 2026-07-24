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
    looking_down_at_phone: bool,
    start_time: float | None,
    cooldown_until: float,
    alert_until: float,
    phone_uses_today: int,
    config: dict,
) -> None:
    now = time.time()
    elapsed = 0 if start_time is None else now - start_time
    trigger_remaining = max(config["trigger_seconds"] - elapsed, 0)
    cooldown_remaining = max(cooldown_until - now, 0)

    status_lines = [
        f"Person: {'yes' if person_detected else 'no'}",
        f"Phone: {'yes' if phone_detected else 'no'}",
        f"Looking down: {'yes' if looking_down_at_phone else 'no'}",
        f"Trigger in: {trigger_remaining:.1f}s",
        f"Cooldown: {cooldown_remaining:.0f}s",
        f"Phone uses today: {phone_uses_today}",
        f"Calibration: {'on' if config['calibration_mode'] else 'off'}",
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
            (20, 180),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 0, 255),
            2,
        )


def draw_calibration(frame, analysis: dict, config: dict) -> None:
    min_ratio = config["phone_min_person_y_ratio"]
    max_ratio = config["phone_max_person_y_ratio"]
    margin_ratio = config["phone_person_horizontal_margin_ratio"]

    for person in analysis["people"]:
        x1, y1, x2, y2 = map(int, person["box"])
        person_width = max(x2 - x1, 1)
        person_height = max(y2 - y1, 1)
        margin = int(person_width * margin_ratio)
        min_y = int(y1 + person_height * min_ratio)
        max_y = int(y1 + person_height * max_ratio)

        cv2.rectangle(frame, (x1 - margin, min_y), (x2 + margin, max_y), (255, 255, 0), 1)
        cv2.line(frame, (x1 - margin, min_y), (x2 + margin, min_y), (255, 255, 0), 2)
        cv2.line(frame, (x1 - margin, max_y), (x2 + margin, max_y), (255, 255, 0), 2)

    best_match = analysis["best_match"]
    if not best_match:
        return

    phone_cx, phone_cy = best_match["phone"]["center"]
    cv2.circle(frame, (int(phone_cx), int(phone_cy)), 5, (255, 255, 0), -1)
    details = [
        f"phone_y_ratio: {best_match['phone_y_ratio']:.2f}",
        f"required_y: {min_ratio:.2f}-{max_ratio:.2f}",
        f"horizontal: {'ok' if best_match['horizontally_near'] else 'no'}",
        f"zone: {'ok' if best_match['vertically_in_phone_zone'] else 'no'}",
    ]

    for index, line in enumerate(details):
        cv2.putText(
            frame,
            line,
            (20, 230 + index * 22),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 0),
            2,
        )
