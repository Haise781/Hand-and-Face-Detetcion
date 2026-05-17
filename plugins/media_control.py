import time
import ctypes
from plugins.base_plugin import BasePlugin

class MediaControlPlugin(BasePlugin):
    def __init__(self):
        super().__init__()
        self.last_triggered = 0
        self.cooldown = 1.0 # 1 second cooldown to avoid toggling too rapidly

    @property
    def name(self) -> str:
        return "Media Play/Pause"

    @property
    def description(self) -> str:
        return "OK Sign toggles media play/pause."

    @property
    def gesture_trigger(self) -> str:
        return "OK Sign"

    def execute(self, hand_index: int, lm_list: list, frame, results) -> str:
        now = time.time()
        if now - self.last_triggered < self.cooldown:
            return ""

        VK_MEDIA_PLAY_PAUSE = 0xB3
        try:
            # Simulate Media Play/Pause key press
            ctypes.windll.user32.keybd_event(VK_MEDIA_PLAY_PAUSE, 0, 0, 0)
            ctypes.windll.user32.keybd_event(VK_MEDIA_PLAY_PAUSE, 0, 2, 0)
            self.last_triggered = now
            return "Toggled Media Playback (Play/Pause)"
        except Exception as e:
            return f"Media Control Error: {str(e)}"
