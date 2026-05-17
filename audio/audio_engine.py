import threading
import sys
import time

# Winsound is Windows-only, so we import it conditionally and fail-safe on other OS
_PLATFORM_WINDOWS = sys.platform.startswith("win")
if _PLATFORM_WINDOWS:
    import winsound
else:
    winsound = None

class AudioEngine:
    def __init__(self):
        self.enabled = True
        self.lock = threading.Lock()

    def set_enabled(self, enabled: bool):
        self.enabled = enabled

    def _play_sweep(self, freqs, duration_ms):
        if not self.enabled or not _PLATFORM_WINDOWS:
            return
        
        # Run beeps sequentially in this thread (which is spawned in background)
        for freq in freqs:
            try:
                winsound.Beep(int(freq), int(duration_ms))
            except Exception:
                break

    def play_sound_async(self, sound_type: str):
        """Spawns a daemon thread to synthesize audio beeps without blocking the main loop"""
        if not self.enabled or not _PLATFORM_WINDOWS:
            return

        thread_target = None
        
        if sound_type == "spell_cast":
            # Fast rising magical frequency sweep
            freqs = [300, 450, 600, 800, 1100, 1500]
            thread_target = lambda: self._play_sweep(freqs, 30)
            
        elif sound_type == "energy_blast":
            # Deep descending explosion rumble
            freqs = [250, 180, 120, 90, 60]
            thread_target = lambda: self._play_sweep(freqs, 80)
            
        elif sound_type == "snap":
            # High pitched rapid click
            freqs = [1800, 2200]
            thread_target = lambda: self._play_sweep(freqs, 15)
            
        elif sound_type == "ui_nav":
            # Two-tone fast confirmation beep
            freqs = [800, 1200]
            thread_target = lambda: self._play_sweep(freqs, 40)
            
        elif sound_type == "error":
            # low growl beep
            freqs = [180, 130]
            thread_target = lambda: self._play_sweep(freqs, 150)

        if thread_target:
            t = threading.Thread(target=thread_target, daemon=True)
            t.start()
