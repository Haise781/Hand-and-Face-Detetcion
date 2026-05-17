import time
import webbrowser
from plugins.base_plugin import BasePlugin

class WebBrowserPlugin(BasePlugin):
    def __init__(self):
        super().__init__()
        self.enabled = False # Disabled by default to prevent stealing focus with browser tabs
        self.last_triggered = 0
        self.cooldown = 5.0 # 5 seconds cooldown
        self.url = "https://github.com/Haise781/Hand-and-Face-Detetcion"

    @property
    def name(self) -> str:
        return "Web Browser Launcher"

    @property
    def description(self) -> str:
        return f"Open Palm opens the project Github repository: {self.url}"

    @property
    def gesture_trigger(self) -> str:
        return "Open Palm"

    def execute(self, hand_index: int, lm_list: list, frame, results) -> str:
        now = time.time()
        if now - self.last_triggered < self.cooldown:
            return ""

        try:
            webbrowser.open(self.url)
            self.last_triggered = now
            return f"Opened browser: {self.url}"
        except Exception as e:
            return f"Web Launcher Error: {str(e)}"
