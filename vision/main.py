import sys
import time
import traceback

import cv2
import torch

from config import WINDOW_NAME, load_config
from detector import analyze_phone_posture, load_model, reset_camera
from lockdown import enforce_lockdown
from overlays import draw_calibration, draw_detections, draw_status
from trigger import TriggerState, update_trigger


def run() -> None:
    torch.set_num_threads(1)
    config = load_config()
    model = load_model(config)
    cap = cv2.VideoCapture(config["camera_index"])
    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    trigger_state = TriggerState(config)

    while True:
        try:
            if not cap.isOpened():
                time.sleep(0.05)
                cap = reset_camera(cap, config["camera_index"])
                continue

            ret, frame = cap.read()
            if not ret:
                print("Frame grab failed, retrying...")
                time.sleep(0.1)
                continue

            results = model.predict(source=frame, verbose=False, device=config["device"])[0]
            analysis = analyze_phone_posture(results, config)
            update_trigger(
                trigger_state,
                analysis["person_detected"],
                analysis["phone_detected"],
                analysis["looking_down_at_phone"],
                config,
            )
            enforce_lockdown(trigger_state, config)

            draw_detections(frame, results, config)
            if config["calibration_mode"]:
                draw_calibration(frame, analysis, config)
            draw_status(
                frame,
                analysis["person_detected"],
                analysis["phone_detected"],
                analysis["looking_down_at_phone"],
                trigger_state.start_time,
                trigger_state.cooldown_until,
                trigger_state.alert_until,
                trigger_state.lockdown_until,
                trigger_state.phone_uses_today,
                config,
            )

            if cv2.getWindowProperty(WINDOW_NAME, cv2.WND_PROP_VISIBLE) < 1:
                cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)

            cv2.imshow(WINDOW_NAME, frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("c"):
                config["calibration_mode"] = not config["calibration_mode"]
                print(f"Calibration mode: {config['calibration_mode']}")
            elif key == ord("q"):
                break
            time.sleep(config["frame_delay_seconds"])
        except KeyboardInterrupt:
            print("KeyboardInterrupt received, exiting loop.")
            break
        except Exception as exc:
            print(f"Loop error, recovering camera: {exc}", file=sys.stderr)
            traceback.print_exc()
            time.sleep(0.05)
            cap = reset_camera(cap, config["camera_index"])
            continue

    cap.release()
    cv2.destroyAllWindows()
    print("Exited main loop; resources released.")


if __name__ == "__main__":
    run()
