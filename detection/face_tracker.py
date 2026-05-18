import cv2
import numpy as np
import mediapipe as mp
import math

class FaceDetector:
    def __init__(self, max_faces=1, min_detection_con=0.5, min_tracking_con=0.5):
        self.max_faces = max_faces
        self.min_detection_con = min_detection_con
        self.min_tracking_con = min_tracking_con
        
        # Initialize MediaPipe Face Mesh
        self.mp_face_mesh = mp.solutions.face_mesh
        try:
            self.face_mesh = self.mp_face_mesh.FaceMesh(
                max_num_faces=self.max_faces,
                refine_landmarks=True,
                min_detection_confidence=float(self.min_detection_con),
                min_tracking_confidence=float(self.min_tracking_con)
            )
        except Exception:
            # Fallback if refine_landmarks is not supported in an older mediapipe version
            self.face_mesh = self.mp_face_mesh.FaceMesh(
                max_num_faces=self.max_faces,
                min_detection_confidence=float(self.min_detection_con),
                min_tracking_confidence=float(self.min_tracking_con)
            )
            
        self.results = None
        
        # Exponential Moving Average (EMA) smoothing for face landmarks to prevent visual jitter
        self.smoothed_landmarks = {}
        self.smoothing_factor = 0.75 # Quick reaction with sleek dampening
        self.closed_frames_history = {}
        self.left_wink_frames = {}
        self.right_wink_frames = {}
        self.yawn_frames_history = {}

    def find_faces(self, img):
        """Processes the frame and returns smoothed face landmark coordinates and stats"""
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.face_mesh.process(img_rgb)
        
        faces_list = []
        if self.results and self.results.multi_face_landmarks:
            h, w, c = img.shape
            
            for face_idx, face_landmarks in enumerate(self.results.multi_face_landmarks):
                lm_list = []
                
                # Setup smoothed dict for this face if not exists
                if face_idx not in self.smoothed_landmarks:
                    self.smoothed_landmarks[face_idx] = {}
                prev_smoothed = self.smoothed_landmarks[face_idx]
                
                for id, lm in enumerate(face_landmarks.landmark):
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    cz = lm.z
                    
                    if id in prev_smoothed:
                        prev_x, prev_y, prev_z = prev_smoothed[id]
                        # Apply Exponential Moving Average (EMA)
                        sm_x = int(self.smoothing_factor * cx + (1.0 - self.smoothing_factor) * prev_x)
                        sm_y = int(self.smoothing_factor * cy + (1.0 - self.smoothing_factor) * prev_y)
                        sm_z = self.smoothing_factor * cz + (1.0 - self.smoothing_factor) * prev_z
                    else:
                        sm_x, sm_y, sm_z = cx, cy, cz
                        
                    prev_smoothed[id] = (sm_x, sm_y, sm_z)
                    lm_list.append([id, sm_x, sm_y, sm_z])
                
                # Extract key features for cyberHUD overlays and eye telemetry
                # Eyelid landmark indices
                # Left eye vertical: 159 (upper) to 145 (lower)
                # Right eye vertical: 386 (upper) to 374 (lower)
                # Left eye horizontal: 33 to 133
                # Right eye horizontal: 362 to 263
                
                left_blink = False
                right_blink = False
                
                if len(lm_list) > 386:
                    # Left eye vertical distance
                    l_v_dist = math.hypot(lm_list[159][1] - lm_list[145][1], lm_list[159][2] - lm_list[145][2])
                    l_h_dist = math.hypot(lm_list[33][1] - lm_list[133][1], lm_list[33][2] - lm_list[133][2])
                    l_ratio = l_v_dist / max(1.0, l_h_dist)
                    left_blink = l_ratio < 0.15
                    
                    # Right eye vertical distance
                    r_v_dist = math.hypot(lm_list[386][1] - lm_list[374][1], lm_list[386][2] - lm_list[374][2])
                    r_h_dist = math.hypot(lm_list[362][1] - lm_list[263][1], lm_list[362][2] - lm_list[263][2])
                    r_ratio = r_v_dist / max(1.0, r_h_dist)
                    right_blink = r_ratio < 0.15
                
                # Drowsiness / Fatigue Tracking: check if both eyes are closed consecutively
                if left_blink and right_blink:
                    self.closed_frames_history[face_idx] = self.closed_frames_history.get(face_idx, 0) + 1
                else:
                    self.closed_frames_history[face_idx] = 0
                
                drowsy = self.closed_frames_history[face_idx] >= 12 # Closed for ~0.4s consecutively
                
                # Wink Detection: one eye closed, one eye open
                left_wink = left_blink and not right_blink
                right_wink = right_blink and not left_blink
                
                if left_wink:
                    self.left_wink_frames[face_idx] = self.left_wink_frames.get(face_idx, 0) + 1
                else:
                    self.left_wink_frames[face_idx] = 0
                    
                if right_wink:
                    self.right_wink_frames[face_idx] = self.right_wink_frames.get(face_idx, 0) + 1
                else:
                    self.right_wink_frames[face_idx] = 0
                
                # Trigger exactly once when wink duration reaches 5 frames
                left_wink_triggered = (self.left_wink_frames[face_idx] == 5)
                right_wink_triggered = (self.right_wink_frames[face_idx] == 5)
                
                # Mouth Yawn Detection
                yawning = False
                yawn_ratio = 0.0
                if len(lm_list) > 308:
                    # Vertical distance: landmark 13 (upper inner lip) to 14 (lower inner lip)
                    v_lip_dist = math.hypot(lm_list[13][1] - lm_list[14][1], lm_list[13][2] - lm_list[14][2])
                    # Horizontal width: landmark 78 (left corner) to 308 (right corner)
                    h_lip_dist = math.hypot(lm_list[78][1] - lm_list[308][1], lm_list[78][2] - lm_list[308][2])
                    yawn_ratio = v_lip_dist / max(1.0, h_lip_dist)
                    
                    if yawn_ratio > 0.55:
                        self.yawn_frames_history[face_idx] = self.yawn_frames_history.get(face_idx, 0) + 1
                    else:
                        self.yawn_frames_history[face_idx] = 0
                        
                    yawning = self.yawn_frames_history[face_idx] >= 15 # Yawning held for ~0.5s consecutively
                
                # Check for pupil tracking (iris landmarks: 468-472 for left iris, 473-477 for right iris)
                left_pupil = None
                right_pupil = None
                if len(lm_list) > 477:
                    # Average the 4 points of iris to find center
                    left_pupil = (
                        int(np.mean([lm_list[idx][1] for idx in range(468, 472)])),
                        int(np.mean([lm_list[idx][2] for idx in range(468, 472)]))
                    )
                    right_pupil = (
                        int(np.mean([lm_list[idx][1] for idx in range(473, 477)])),
                        int(np.mean([lm_list[idx][2] for idx in range(473, 477)]))
                    )
                
                faces_list.append({
                    "index": face_idx,
                    "lm_list": lm_list,
                    "left_blink": left_blink,
                    "right_blink": right_blink,
                    "left_pupil": left_pupil,
                    "right_pupil": right_pupil,
                    "drowsy": drowsy,
                    "drowsy_frames": self.closed_frames_history[face_idx],
                    "left_wink_triggered": left_wink_triggered,
                    "right_wink_triggered": right_wink_triggered,
                    "yawning": yawning,
                    "yawn_ratio": yawn_ratio
                })
                
        return faces_list

    def close(self):
        """Safely release MediaPipe face mesh resources"""
        if hasattr(self, 'face_mesh') and self.face_mesh is not None:
            try:
                self.face_mesh.close()
            except Exception:
                pass
