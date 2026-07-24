import cv2


class PostureDetector:
    def __init__(self, config: dict) -> None:
        self.enabled = config["posture_detection_enabled"]
        self.available = False
        self.pose = None
        self.pose_landmark = None

        if not self.enabled:
            return

        try:
            import mediapipe as mp
        except ImportError:
            print("MediaPipe is not installed; posture detection will use phone-position fallback.")
            return

        self.available = True
        self.pose_landmark = mp.solutions.pose.PoseLandmark
        self.pose = mp.solutions.pose.Pose(
            static_image_mode=False,
            model_complexity=0,
            enable_segmentation=False,
            min_detection_confidence=config["pose_min_detection_confidence"],
            min_tracking_confidence=config["pose_min_tracking_confidence"],
        )

    def analyze(self, frame, config: dict) -> dict:
        default_analysis = {
            "enabled": self.enabled,
            "available": self.available,
            "detected": False,
            "head_down": False,
            "slouching": False,
            "head_down_score": 0,
            "shoulder_tilt": 0,
            "landmarks": {},
        }
        if not self.enabled or not self.available:
            return default_analysis

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb_frame)
        if not results.pose_landmarks:
            return default_analysis

        landmarks = results.pose_landmarks.landmark
        points = self._read_points(landmarks, frame.shape)
        head_down_score = self._head_down_score(points)
        shoulder_tilt = self._shoulder_tilt(points)

        return {
            "enabled": self.enabled,
            "available": self.available,
            "detected": True,
            "head_down": head_down_score >= config["head_down_score_threshold"],
            "slouching": shoulder_tilt >= config["slouch_shoulder_tilt_threshold"],
            "head_down_score": head_down_score,
            "shoulder_tilt": shoulder_tilt,
            "landmarks": points,
        }

    def close(self) -> None:
        if self.pose:
            self.pose.close()

    def _read_points(self, landmarks, frame_shape) -> dict:
        height, width = frame_shape[:2]
        names = {
            "nose": self.pose_landmark.NOSE,
            "left_eye": self.pose_landmark.LEFT_EYE,
            "right_eye": self.pose_landmark.RIGHT_EYE,
            "left_ear": self.pose_landmark.LEFT_EAR,
            "right_ear": self.pose_landmark.RIGHT_EAR,
            "left_shoulder": self.pose_landmark.LEFT_SHOULDER,
            "right_shoulder": self.pose_landmark.RIGHT_SHOULDER,
        }
        points = {}
        for name, landmark_id in names.items():
            landmark = landmarks[landmark_id.value]
            if landmark.visibility < 0.45:
                continue
            points[name] = {
                "x": int(landmark.x * width),
                "y": int(landmark.y * height),
                "visibility": landmark.visibility,
            }
        return points

    def _head_down_score(self, points: dict) -> float:
        if "nose" not in points:
            return 0

        reference_points = [
            points[name]
            for name in ("left_eye", "right_eye", "left_ear", "right_ear")
            if name in points
        ]
        if not reference_points:
            return 0

        face_reference_y = sum(point["y"] for point in reference_points) / len(reference_points)
        shoulder_width = self._shoulder_width(points)
        if shoulder_width <= 0:
            return 0
        return (points["nose"]["y"] - face_reference_y) / shoulder_width

    def _shoulder_tilt(self, points: dict) -> float:
        if "left_shoulder" not in points or "right_shoulder" not in points:
            return 0

        shoulder_width = self._shoulder_width(points)
        if shoulder_width <= 0:
            return 0
        return abs(points["left_shoulder"]["y"] - points["right_shoulder"]["y"]) / shoulder_width

    def _shoulder_width(self, points: dict) -> float:
        if "left_shoulder" not in points or "right_shoulder" not in points:
            return 0
        return abs(points["left_shoulder"]["x"] - points["right_shoulder"]["x"])


def combine_phone_and_posture(phone_analysis: dict, posture_analysis: dict, config: dict) -> bool:
    phone_position_ok = phone_analysis["looking_down_at_phone"]
    if not config["require_pose_head_down"]:
        return phone_position_ok

    if not posture_analysis["enabled"]:
        return phone_position_ok

    if not posture_analysis["available"] or not posture_analysis["detected"]:
        return phone_position_ok if config["fallback_to_phone_position_without_pose"] else False

    return phone_position_ok and posture_analysis["head_down"]
