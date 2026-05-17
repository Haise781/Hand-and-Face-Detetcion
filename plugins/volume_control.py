import time
import ctypes
from plugins.base_plugin import BasePlugin

class VolumeControlPlugin(BasePlugin):
    def __init__(self):
        super().__init__()
        self.last_triggered = 0
        self.cooldown = 0.25 # seconds cooldown to prevent massive volume jumps

    @property
    def name(self) -> str:
        return "Volume Control"

    @property
    def description(self) -> str:
        return "Thumbs Up raises volume, Thumbs Down lowers volume."

    @property
    def gesture_trigger(self):
        return "Thumbs Up"  # We can handle Thumbs Down manually in the execute since it's closely related

    def execute(self, hand_index: int, lm_list: list, frame, results) -> str:
        now = time.time()
        if now - self.last_triggered < self.cooldown:
            return ""

        # We can double check if we need Thumbs Up or Thumbs Down
        # Since we registered for "Thumbs Up", let's check the actual state from y-coords
        # In case the gesture is "Thumbs Down", we will also execute
        # Wait, the manager might pass either gesture here.
        # Let's inspect thumb coordinates: lm_list[4] (tip) vs lm_list[3] (joint)
        is_up = lm_list[4][2] < lm_list[3][2]
        
        VK_VOLUME_UP = 0xAF
        VK_VOLUME_DOWN = 0xAE
        
        try:
            if is_up:
                # Press Volume Up
                ctypes.windll.user32.keybd_event(VK_VOLUME_UP, 0, 0, 0)
                ctypes.windll.user32.keybd_event(VK_VOLUME_UP, 0, 2, 0)
                self.last_triggered = now
                return "Increased System Volume (+2%)"
            else:
                # Press Volume Down
                ctypes.windll.user32.keybd_event(VK_VOLUME_DOWN, 0, 0, 0)
                ctypes.windll.user32.keybd_event(VK_VOLUME_DOWN, 0, 2, 0)
                self.last_triggered = now
                return "Decreased System Volume (-2%)"
        except Exception as e:
            return f"Volume Control Error: {str(e)}"
