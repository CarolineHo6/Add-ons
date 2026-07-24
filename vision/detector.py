import cv2
from ultralytics import YOLO

from config import resolve_project_path


def load_model(config: dict) -> YOLO:
    return YOLO(resolve_project_path(config["model_path"]))


def reset_camera(cap, camera_index: int):
    cap.release()
    return cv2.VideoCapture(camera_index)


def extract_target_boxes(results, config: dict) -> tuple[list[dict], list[dict]]:
    people = []
    phones = []

    for box in results.boxes:
        cls_name = results.names[int(box.cls)]
        confidence = float(box.conf[0])
        if cls_name == "person" and confidence < config["person_confidence"]:
            continue
        if cls_name == "cell phone" and confidence < config["phone_confidence"]:
            continue
        if cls_name not in {"person", "cell phone"}:
            continue

        x1, y1, x2, y2 = map(float, box.xyxy[0])
        item = {
            "class_name": cls_name,
            "confidence": confidence,
            "box": (x1, y1, x2, y2),
            "center": ((x1 + x2) / 2, (y1 + y2) / 2),
        }
        if cls_name == "person":
            people.append(item)
        else:
            phones.append(item)

    return people, phones


def analyze_phone_posture(results, config: dict) -> dict:
    people, phones = extract_target_boxes(results, config)
    best_match = None

    for person in people:
        px1, py1, px2, py2 = person["box"]
        person_width = max(px2 - px1, 1)
        person_height = max(py2 - py1, 1)
        margin = person_width * config["phone_person_horizontal_margin_ratio"]

        for phone in phones:
            phone_cx, phone_cy = phone["center"]
            y_ratio = (phone_cy - py1) / person_height
            horizontally_near = px1 - margin <= phone_cx <= px2 + margin
            vertically_in_phone_zone = (
                config["phone_min_person_y_ratio"]
                <= y_ratio
                <= config["phone_max_person_y_ratio"]
            )
            qualifies = horizontally_near and vertically_in_phone_zone
            score = abs(y_ratio - config["phone_min_person_y_ratio"])

            candidate = {
                "person": person,
                "phone": phone,
                "phone_y_ratio": y_ratio,
                "horizontally_near": horizontally_near,
                "vertically_in_phone_zone": vertically_in_phone_zone,
                "qualifies": qualifies,
                "score": score,
            }
            if best_match is None:
                best_match = candidate
            elif qualifies and not best_match["qualifies"]:
                best_match = candidate
            elif qualifies == best_match["qualifies"] and score < best_match["score"]:
                best_match = candidate

    looking_down_at_phone = bool(best_match and best_match["qualifies"])
    return {
        "person_detected": bool(people),
        "phone_detected": bool(phones),
        "looking_down_at_phone": looking_down_at_phone,
        "people": people,
        "phones": phones,
        "best_match": best_match,
    }
