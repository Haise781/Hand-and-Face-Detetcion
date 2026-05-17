import sys
import cv2
import numpy as np
from PyQt6.QtWidgets import (
    QMainWindow, QLabel, QVBoxLayout, 
    QHBoxLayout, QWidget, QPushButton, QFrame
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QImage, QPixmap, QFont
from detection.hand_tracker import HandDetector
from gestures.recognizer import GestureRecognizer
from utils.fps_counter import FPSCounter
from ui.styles import CYBERPUNK_STYLESHEET

class CameraThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)
    update_stats_signal = pyqtSignal(str, str, int) # gesture, hand_count, fps

    def __init__(self, camera_id=0):
        super().__init__()
        self.camera_id = camera_id
        self._run_flag = True
        self.detector = HandDetector(max_hands=2, detection_con=0.7, track_con=0.5)
        self.recognizer = GestureRecognizer()
        self.fps_counter = FPSCounter()

    def run(self):
        cap = cv2.VideoCapture(self.camera_id)
        while self._run_flag:
            ret, frame = cap.read()
            if ret:
                # Mirror effect
                frame = cv2.flip(frame, 1)
                
                # Detect hands
                frame = self.detector.find_hands(frame, draw=True)
                
                # Recognition logic
                lm_list = self.detector.find_position(frame, hand_no=0)
                gesture = self.recognizer.recognize(lm_list) if lm_list else "None"
                
                # Updated for the Tasks API: self.detector.results.hand_landmarks
                hand_count = len(self.detector.results.hand_landmarks) if self.detector.results and self.detector.results.hand_landmarks else 0
                
                # Update FPS
                fps = self.fps_counter.update()
                
                self.update_stats_signal.emit(gesture, str(hand_count), fps)
                self.change_pixmap_signal.emit(frame)

        cap.release()

    def stop(self):
        self._run_flag = False
        self.wait()


class MainWindow(QMainWindow):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.setWindowTitle(config.get("app_name", "Nexus Hand AI"))
        self.setGeometry(100, 100, 1024, 720)
        self.setStyleSheet(CYBERPUNK_STYLESHEET)
        
        self.init_ui()
        
        # Start Camera Thread
        self.thread = CameraThread(camera_id=self.config.get("camera_id", 0))
        self.thread.change_pixmap_signal.connect(self.update_image)
        self.thread.update_stats_signal.connect(self.update_stats)
        self.thread.start()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        
        # Left Panel (Video feed)
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setStyleSheet("border: 2px solid #00FFFF; background-color: #000000; border-radius: 10px;")
        main_layout.addWidget(self.video_label, stretch=3)
        
        # Right Panel (Controls & Stats)
        right_panel = QFrame()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Title
        title_label = QLabel("NEURAL VISION\nSYSTEM v1.0")
        title_label.setFont(QFont("Consolas", 22, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #FF00FF; margin-bottom: 20px; border: none;")
        right_layout.addWidget(title_label)
        
        # Stats Group
        stats_frame = QFrame()
        stats_frame.setStyleSheet("border: 1px solid #00FFFF; background-color: transparent;")
        stats_layout = QVBoxLayout(stats_frame)
        
        self.fps_label = QLabel("FPS: 0")
        self.hands_label = QLabel("Hands Detected: 0")
        self.gesture_label = QLabel("Current Gesture: None")
        self.gesture_label.setStyleSheet("color: #00FF00; font-weight: bold; font-size: 18px;")
        
        for lbl in [self.fps_label, self.hands_label, self.gesture_label]:
            lbl.setFont(QFont("Consolas", 14))
            stats_layout.addWidget(lbl)
            
        right_layout.addWidget(stats_frame)
        right_layout.addSpacing(40)
        
        # Buttons
        self.btn_toggle_cam = QPushButton("CALIBRATE SENSORS")
        self.btn_exit = QPushButton("SYSTEM EXIT")
        self.btn_exit.setStyleSheet("border-color: #FF0055; color: #FF0055;")
        self.btn_exit.clicked.connect(self.close)
        
        right_layout.addWidget(self.btn_toggle_cam)
        right_layout.addSpacing(10)
        right_layout.addWidget(self.btn_exit)
        
        main_layout.addWidget(right_panel, stretch=1)

    @pyqtSlot(np.ndarray)
    def update_image(self, cv_img):
        h, w, ch = cv_img.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(cv_img.data, w, h, bytes_per_line, QImage.Format.Format_BGR888)
        p = convert_to_Qt_format.scaled(640, 480, Qt.AspectRatioMode.KeepAspectRatio)
        self.video_label.setPixmap(QPixmap.fromImage(p))

    @pyqtSlot(str, str, int)
    def update_stats(self, gesture, hand_count, fps):
        self.gesture_label.setText(f"Gesture: {gesture}")
        self.hands_label.setText(f"Entities: {hand_count}")
        self.fps_label.setText(f"FPS: {fps}")

    def closeEvent(self, event):
        self.thread.stop()
        event.accept()
