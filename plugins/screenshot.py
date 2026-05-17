import os
import time
import cv2
from datetime import datetime
from plugins.base_plugin import BasePlugin

class ScreenshotPlugin(BasePlugin):
    def __init__(self):
        super().__init__()
        self.last_triggered = 0
        self.cooldown = 2.0 # 2 seconds cooldown to prevent flooding
        self.output_dir = "screenshots"

    @property
    def name(self) -> str:
        return "Camera Snapshot"

    @property
    def description(self) -> str:
        return "Fist gesture captures and saves the current camera feed."

    @property
    def gesture_trigger(self) -> str:
        return "Fist"

    def execute(self, hand_index: int, lm_list: list, frame, results) -> str:
        now = time.time()
        if now - self.last_triggered < self.cooldown:
            return ""

        try:
            if not os.path.exists(self.output_dir):
                os.makedirs(self.output_dir, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(self.output_dir, f"snapshot_{timestamp}.png")
            
            # Save the frame
            cv2.imwrite(filename, frame)
            self.last_triggered = now
            return f"Saved Snapshot: {filename}"
        except Exception as e:
            return f"Snapshot Error: {str(e)}"
