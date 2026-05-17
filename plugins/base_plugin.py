import abc

class BasePlugin(abc.ABC):
    def __init__(self):
        self.enabled = True

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Name of the plugin"""
        pass

    @property
    @abc.abstractmethod
    def description(self) -> str:
        """Brief description of the plugin's action"""
        pass

    @property
    @abc.abstractmethod
    def gesture_trigger(self) -> str:
        """The gesture that triggers this plugin (e.g. 'Peace', 'Thumbs Up', 'OK Sign')"""
        pass

    @abc.abstractmethod
    def execute(self, hand_index: int, lm_list: list, frame, results) -> str:
        """
        Execute the action when the gesture is detected.
        Args:
            hand_index: Index of the hand triggering the plugin (0, 1, etc.)
            lm_list: List of landmarks [id, cx, cy]
            frame: The current OpenCV image frame
            results: Full MediaPipe hand landmarker results for advanced processing
        Returns:
            A status string describing the action taken, to be displayed in the logs.
        """
        pass
