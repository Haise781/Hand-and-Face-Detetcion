import ctypes
import numpy as np
import math

class VirtualMouse:
    def __init__(self, smoothening=5):
        self.enabled = False
        self.smoothening = smoothening
        
        # Get screen size in pixels
        try:
            self.screen_width = ctypes.windll.user32.GetSystemMetrics(0)
            self.screen_height = ctypes.windll.user32.GetSystemMetrics(1)
        except Exception:
            self.screen_width = 1920
            self.screen_height = 1080
            
        self.prev_x, self.prev_y = 0, 0
        self.curr_x, self.curr_y = 0, 0
        self.clicked = False
        
        # Trackpad boundaries in camera frame (for easier reaching of screen edges)
        self.margin_x = 100
        self.margin_y = 80

    def set_enabled(self, enabled: bool):
        self.enabled = enabled
        if not enabled:
            # Release click if we disable it while clicking
            self.release_left_click()

    def press_left_click(self):
        if not self.clicked:
            # MOUSEEVENTF_LEFTDOWN = 0x0002
            ctypes.windll.user32.mouse_event(2, 0, 0, 0, 0)
            self.clicked = True

    def release_left_click(self):
        if self.clicked:
            # MOUSEEVENTF_LEFTUP = 0x0004
            ctypes.windll.user32.mouse_event(4, 0, 0, 0, 0)
            self.clicked = False

    def update(self, lm_list, frame_w, frame_h, fingers) -> str:
        """
        Updates cursor position and clicks based on hand landmarks.
        Args:
            lm_list: List of landmarks [id, cx, cy]
            frame_w: Camera frame width
            frame_h: Camera frame height
            fingers: List of [thumb, index, middle, ring, pinky] (1 if extended, 0 if folded)
        Returns:
            A string log indicating the mouse state
        """
        if not self.enabled or not lm_list:
            return ""

        # Index tip (8) and Middle tip (12)
        # Thumb tip (4)
        x1, y1 = lm_list[8][1], lm_list[8][2]
        
        status = ""
        
        # Moving mode: Index is up, Middle is down (or both up for clicking)
        # We allow moving if Index is up (fingers[1] == 1)
        if fingers[1] == 1:
            # Map index finger coordinate to screen coordinate (using custom trackpad margin)
            # This ensures comfort so you don't have to reach the absolute edge of your webcam
            rx = np.interp(x1, (self.margin_x, frame_w - self.margin_x), (0, self.screen_width))
            ry = np.interp(y1, (self.margin_y, frame_h - self.margin_y), (0, self.screen_height))
            
            # Smooth cursor position using exponential moving average
            self.curr_x = self.prev_x + (rx - self.prev_x) / self.smoothening
            self.curr_y = self.prev_y + (ry - self.prev_y) / self.smoothening
            
            # Move cursor on screen
            ctypes.windll.user32.SetCursorPos(int(self.curr_x), int(self.curr_y))
            self.prev_x, self.prev_y = self.curr_x, self.curr_y
            status = f"Moving ({int(self.curr_x)}, {int(self.curr_y)})"

            # Click Mode: Both Index and Middle fingers are up
            if fingers[2] == 1:
                # Find distance between index tip (8) and middle tip (12)
                x2, y2 = lm_list[12][1], lm_list[12][2]
                distance = math.hypot(x2 - x1, y2 - y1)
                
                # If distance is small, trigger left click (simulate pinch)
                if distance < 35:
                    self.press_left_click()
                    status = "Pinch Click (L-Down)"
                else:
                    self.release_left_click()
            else:
                self.release_left_click()
        else:
            self.release_left_click()
            
        return status
