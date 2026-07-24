import cv2
from ultralytics import YOLO

from config import resolve_project_path


def load_model(config: dict) -> YOLO:
    return YOLO(resolve_project_path(config["model_path"]))


def reset_camera(cap, camera_index: int):
    cap.release()
    return cv2.VideoCapture(camera_index)


def read_detections(results, config: dict) -> tuple[bool, bool]:
    person_detected = False
    phone_detected = False

    for box in results.boxes:
        cls_name = results.names[int(box.cls)]
        confidence = float(box.conf[0])
        if cls_name == "person" and confidence >= config["person_confidence"]:
            person_detected = True
        elif cls_name == "cell phone" and confidence >= config["phone_confidence"]:
            phone_detected = True

    return person_detected, phone_detected
