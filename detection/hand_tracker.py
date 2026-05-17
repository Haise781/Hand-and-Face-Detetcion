import os
import urllib.request
import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

MODEL_URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
MODEL_PATH = "configs/hand_landmarker.task"

class HandDetector:
    def __init__(self, mode=False, max_hands=2, detection_con=0.8, track_con=0.8):
        self.mode = mode
        self.max_hands = max_hands
        self.detection_con = detection_con
        self.track_con = track_con
        
        # Download model if not exists
        if not os.path.exists(MODEL_PATH):
            os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
            print(f"[INFO] Downloading MediaPipe Hand Landmarker model to {MODEL_PATH}...")
            urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
            print("[INFO] Model downloaded successfully.")

        # Initialize detector - tuned for high accuracy
        base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.IMAGE,
            num_hands=self.max_hands,
            min_hand_detection_confidence=float(self.detection_con),
            min_hand_presence_confidence=float(self.track_con),
            min_tracking_confidence=float(self.track_con)
        )
        self.detector = vision.HandLandmarker.create_from_options(options)
        self.results = None
        
        # Smoothing History for landmark jitter-reduction (EMA)
        self.smoothed_landmarks = {"Left": {}, "Right": {}}
        
        # Alpha: 0.8 provides instant response (no delay) while removing micro-jitters
        self.smoothing_factor = 0.8 

    def find_hands(self, img, draw=True):
        """Processes the frame, runs landmarker, and optionally draws a clean tech skeleton"""
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
        
        self.results = self.detector.detect(mp_image)
        
        if draw and self.results.hand_landmarks:
            h, w, c = img.shape
            active_hands = self.get_active_hands(img)
            
            for idx, hand in enumerate(active_hands):
                # Professional Tech Red Styling
                line_color = (0, 0, 200)   # Deep Red lines
                node_color = (200, 200, 255) # Off-white nodes for high contrast
                
                connections = [
                    (0, 1), (1, 2), (2, 3), (3, 4),
                    (0, 5), (5, 6), (6, 7), (7, 8),
                    (5, 9), (9, 10), (10, 11), (11, 12),
                    (9, 13), (13, 14), (14, 15), (15, 16),
                    (13, 17), (17, 18), (18, 19), (19, 20),
                    (0, 17)
                ]
                
                # Draw sleek lines
                for start, end in connections:
                    x1, y1 = hand["lm_list"][start][1], hand["lm_list"][start][2]
                    x2, y2 = hand["lm_list"][end][1], hand["lm_list"][end][2]
                    cv2.line(img, (x1, y1), (x2, y2), line_color, 2, cv2.LINE_AA)

                # Draw minimal crisp nodes
                for id in range(21):
                    cx, cy = hand["lm_list"][id][1], hand["lm_list"][id][2]
                    cv2.circle(img, (cx, cy), 3, node_color, -1, cv2.LINE_AA)
                    
        return img

    def get_active_hands(self, img):
        """
        Returns structured telemetry lists of active hands with mirror-corrected handedness labels 
        and real-time exponential moving average (EMA) jitter reduction for maximum stability.
        """
        hands_list = []
        if self.results and self.results.hand_landmarks:
            h, w, c = img.shape
            
            for i, hand_landmarks in enumerate(self.results.hand_landmarks):
                raw_label = self.results.handedness[i][0].category_name if i < len(self.results.handedness) else "Unknown"
                physical_label = "Right" if raw_label == "Left" else "Left"
                
                smoothed_list = []
                prev_smoothed = self.smoothed_landmarks[physical_label]
                
                for id, lm in enumerate(hand_landmarks):
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    cz = lm.z
                    
                    if id in prev_smoothed:
                        prev_x, prev_y, prev_z = prev_smoothed[id]
                        # EMA Smoothing
                        sm_x = int(self.smoothing_factor * cx + (1.0 - self.smoothing_factor) * prev_x)
                        sm_y = int(self.smoothing_factor * cy + (1.0 - self.smoothing_factor) * prev_y)
                        sm_z = self.smoothing_factor * cz + (1.0 - self.smoothing_factor) * prev_z
                    else:
                        sm_x, sm_y, sm_z = cx, cy, cz
                        
                    prev_smoothed[id] = (sm_x, sm_y, sm_z)
                    smoothed_list.append([id, sm_x, sm_y])
                
                hands_list.append({
                    "index": i,
                    "label": physical_label,
                    "lm_list": smoothed_list,
                    "landmarks": hand_landmarks,
                    "depth_z": [prev_smoothed[id][2] for id in range(21)]
                })
                
        return hands_list

    def find_position(self, img, hand_no=0):
        lm_list = []
        active_hands = self.get_active_hands(img)
        if hand_no < len(active_hands):
            lm_list = active_hands[hand_no]["lm_list"]
        return lm_list

    def close(self):
        """Safely release MediaPipe resources to prevent Exception ignored in __del__ errors"""
        if hasattr(self, 'detector') and self.detector is not None:
            try:
                self.detector.close()
            except Exception:
                pass
