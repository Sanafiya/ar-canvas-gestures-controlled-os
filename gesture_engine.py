import math

class GestureEngine:
    def __init__(self):
        # Tip IDs: Thumb: 4, Index: 8, Middle: 12, Ring: 16, Pinky: 20
        # PIP IDs: Index: 6, Middle: 10, Ring: 14, Pinky: 18
        self.tip_ids = [4, 8, 12, 16, 20]
        self.pip_ids = [2, 6, 10, 14, 18]

    def _get_fingers_up(self, landmarks):
        """Determines which of the four fingers (Index, Middle, Ring, Pinky) are extended vertically."""
        if len(landmarks) < 21:
            return [0, 0, 0, 0, 0]

        fingers = [0, 0, 0, 0, 0]

        # Check 4 non-thumb fingers (Index, Middle, Ring, Pinky)
        for idx in range(1, 5):
            tip_y = landmarks[self.tip_ids[idx]]['y']
            pip_y = landmarks[self.pip_ids[idx]]['y']
            if tip_y < pip_y:
                fingers[idx] = 1

        return fingers

    def detect_gesture(self, landmarks):
        """Detects strictly 1 of 5 supported gestures or returns NO_GESTURE."""
        if not landmarks or len(landmarks) < 21:
            return "NO_GESTURE"

        fingers = self._get_fingers_up(landmarks)
        
        # Landmark extractions
        thumb_tip = landmarks[4]
        thumb_ip = landmarks[3]
        thumb_mcp = landmarks[2]
        
        index_tip = landmarks[8]
        middle_tip = landmarks[12]

        # Distance calculation for PINCH (Thumb tip to Index tip)
        pinch_distance = math.hypot(
            thumb_tip['x'] - index_tip['x'],
            thumb_tip['y'] - index_tip['y']
        )

        # 1. PINCH (Distance between thumb tip & index tip < 35px)
        if pinch_distance < 35:
            return "PINCH"

        # Check finger states
        index_up = (fingers[1] == 1)
        middle_up = (fingers[2] == 1)
        ring_up = (fingers[3] == 1)
        pinky_up = (fingers[4] == 1)

        # 2. TWO FINGERS (Index & Middle UP, Ring & Pinky DOWN)
        if index_up and middle_up and not ring_up and not pinky_up:
            return "TWO_FINGERS"

        # 3. INDEX FINGER (Index UP, Middle, Ring, Pinky DOWN)
        if index_up and not middle_up and not ring_up and not pinky_up:
            return "INDEX_FINGER"

        # Check if all four fingers are folded for Thumb gestures
        all_other_fingers_closed = (not index_up and not middle_up and not ring_up and not pinky_up)

        if all_other_fingers_closed:
            # 4. THUMBS UP (Thumb pointing upwards relative to MCP joint)
            if thumb_tip['y'] < thumb_ip['y'] < thumb_mcp['y']:
                return "THUMBS_UP"

            # 5. THUMBS DOWN (Thumb pointing downwards relative to MCP joint)
            if thumb_tip['y'] > thumb_ip['y'] > thumb_mcp['y']:
                return "THUMBS_DOWN"

        return "NO_GESTURE"