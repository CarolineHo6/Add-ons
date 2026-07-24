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
    posture_analysis: dict,
    start_time: float | None,
    cooldown_until: float,
    alert_until: float,
    lockdown_until: float,
    current_lockdown_duration_seconds: float,
    phone_uses_today: int,
    config: dict,
) -> None:
    now = time.time()
    elapsed = 0 if start_time is None else now - start_time
    trigger_remaining = max(config["trigger_seconds"] - elapsed, 0)
    cooldown_remaining = max(cooldown_until - now, 0)
    lockdown_remaining = max(lockdown_until - now, 0)

    status_lines = [
        f"Person: {'yes' if person_detected else 'no'}",
        f"Phone: {'yes' if phone_detected else 'no'}",
        f"Looking down: {'yes' if looking_down_at_phone else 'no'}",
        f"Pose head down: {format_pose_status(posture_analysis)}",
        f"Trigger in: {trigger_remaining:.1f}s",
        f"Cooldown: {cooldown_remaining:.0f}s",
        f"Lockdown: {lockdown_remaining:.0f}s",
        f"Lockdown tier: {current_lockdown_duration_seconds:.0f}s",
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
            (20, 280),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 0, 255),
            2,
        )


def draw_calibration(frame, analysis: dict, posture_analysis: dict, config: dict) -> None:
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
        draw_posture_calibration(frame, posture_analysis, config)
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
            (20, 330 + index * 22),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 0),
            2,
        )

    draw_posture_calibration(frame, posture_analysis, config)


def draw_posture_calibration(frame, posture_analysis: dict, config: dict) -> None:
    landmarks = posture_analysis["landmarks"]
    for point in landmarks.values():
        cv2.circle(frame, (point["x"], point["y"]), 4, (255, 0, 255), -1)

    for first, second in [
        ("left_eye", "right_eye"),
        ("left_ear", "right_ear"),
        ("left_shoulder", "right_shoulder"),
        ("nose", "left_eye"),
        ("nose", "right_eye"),
    ]:
        if first in landmarks and second in landmarks:
            cv2.line(
                frame,
                (landmarks[first]["x"], landmarks[first]["y"]),
                (landmarks[second]["x"], landmarks[second]["y"]),
                (255, 0, 255),
                1,
            )

    details = [
        f"pose_available: {'yes' if posture_analysis['available'] else 'no'}",
        f"pose_detected: {'yes' if posture_analysis['detected'] else 'no'}",
        f"head_score: {posture_analysis['head_down_score']:.2f}",
        f"head_required: {config['head_down_score_threshold']:.2f}",
        f"slouch_score: {posture_analysis['shoulder_tilt']:.2f}",
    ]

    for index, line in enumerate(details):
        cv2.putText(
            frame,
            line,
            (20, 430 + index * 22),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 0, 255),
            2,
        )


def format_pose_status(posture_analysis: dict) -> str:
    if not posture_analysis["enabled"]:
        return "off"
    if not posture_analysis["available"]:
        return "unavailable"
    if not posture_analysis["detected"]:
        return "no pose"
    return "yes" if posture_analysis["head_down"] else "no"
