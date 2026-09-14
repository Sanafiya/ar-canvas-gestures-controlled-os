try:
    import pyautogui
except ImportError:
    pyautogui = None

import time
import numpy as np

if pyautogui is not None:
            pyautogui.FAILSAFE = False

class OSController:
    def __init__(self, frame_w=640, frame_h=480):
        if pyautogui is not None:
            self.screen_w, self.screen_h = pyautogui.size()
        else:
            self.screen_w, self.screen_h = 1920, 1080
        self.frame_w = frame_w
        self.frame_h = frame_h

        # Smoothing & Padding configuration
        self.margin = 80  # Active area padding inside frame
        self.smooth_factor = 4
        self.prev_x, self.prev_y = self.screen_w // 2, self.screen_h // 2

        # Debounce / Cooldown timestamps
        self.last_click_time = 0
        self.click_cooldown = 0.4  # seconds

        self.last_volume_time = 0
        self.volume_cooldown = 0.15  # seconds

        self.prev_scroll_y = None
        self.last_scroll_time = 0
        self.scroll_cooldown = 0.05  # seconds

    def execute_action(self, gesture, landmarks, frame_w, frame_h):
        """Maps detected gesture to OS actions with smoothing and debouncing."""
        if not landmarks or gesture == "NO_GESTURE":
            self.prev_scroll_y = None
            return

        self.frame_w = frame_w
        self.frame_h = frame_h
        current_time = time.time()

        # 1. INDEX FINGER -> Move Mouse Cursor
        if gesture == "INDEX_FINGER":
            self.prev_scroll_y = None
            index_x = landmarks[8]['x']
            index_y = landmarks[8]['y']

            # Map camera frame coordinates to full screen size with margin clipping
            mapped_x = np.interp(index_x, [self.margin, self.frame_w - self.margin], [0, self.screen_w])
            mapped_y = np.interp(index_y, [self.margin, self.frame_h - self.margin], [0, self.screen_h])

            # Apply Exponential Moving Average (EMA) smoothing
            curr_x = self.prev_x + (mapped_x - self.prev_x) / self.smooth_factor
            curr_y = self.prev_y + (mapped_y - self.prev_y) / self.smooth_factor

            pyautogui.moveTo(curr_x, curr_y)
            self.prev_x, self.prev_y = curr_x, curr_y

        # 2. PINCH -> Left Click (with cooldown debounce)
        elif gesture == "PINCH":
            self.prev_scroll_y = None
            if current_time - self.last_click_time > self.click_cooldown:
                pyautogui.click()
                self.last_click_time = current_time

        # 3. TWO FINGERS -> Scroll Up / Down based on vertical movement
        elif gesture == "TWO_FINGERS":
            current_y = landmarks[8]['y']
            if self.prev_scroll_y is not None:
                delta_y = current_y - self.prev_scroll_y
                if current_time - self.last_scroll_time > self.scroll_cooldown:
                    if delta_y < -8:  # Moving fingers UP -> Scroll UP
                        pyautogui.scroll(250)
                        self.last_scroll_time = current_time
                    elif delta_y > 8:  # Moving fingers DOWN -> Scroll DOWN
                        pyautogui.scroll(-250)
                        self.last_scroll_time = current_time
            self.prev_scroll_y = current_y

        # 4. THUMBS UP -> Increase Volume
        elif gesture == "THUMBS_UP":
            self.prev_scroll_y = None
            if current_time - self.last_volume_time > self.volume_cooldown:
                pyautogui.press('volumeup')
                self.last_volume_time = current_time

        # 5. THUMBS DOWN -> Decrease Volume
        elif gesture == "THUMBS_DOWN":
            self.prev_scroll_y = None
            if current_time - self.last_volume_time > self.volume_cooldown:
                pyautogui.press('volumedown')
                self.last_volume_time = current_time
