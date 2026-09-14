import cv2
import mediapipe as mp

class HandDetector:
    def __init__(self, max_hands=1, detection_con=0.7, track_con=0.7):
        """Initializes the MediaPipe Hands detection pipeline."""
        self.max_hands = max_hands
        self.detection_con = detection_con
        self.track_con = track_con

        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles

        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=self.max_hands,
            min_detection_confidence=self.detection_con,
            min_tracking_confidence=self.track_con
        )

    def find_hands(self, frame, draw=True):
        """Converts frame to RGB, processes hand landmarks, and draws landmarks."""
        if frame is None:
            return None, None

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)

        if results.multi_hand_landmarks and draw:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing_styles.get_default_hand_landmarks_style(),
                    self.mp_drawing_styles.get_default_hand_connections_style()
                )

        return frame, results

    def get_landmark_list(self, results, width, height):
        """Extracts landmark pixel coordinates from detection results."""
        landmark_list = []
        if results and results.multi_hand_landmarks:
            primary_hand = results.multi_hand_landmarks[0]
            for lm_id, lm in enumerate(primary_hand.landmark):
                cx, cy = int(lm.x * width), int(lm.y * height)
                landmark_list.append({
                    "id": lm_id,
                    "x": cx,
                    "y": cy,
                    "norm_x": lm.x,
                    "norm_y": lm.y,
                    "norm_z": lm.z
                })
        return landmark_list