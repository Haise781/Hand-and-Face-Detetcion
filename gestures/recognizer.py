import math
import time
import numpy as np

class GestureRecognizer:
    def __init__(self):
        # MediaPipe landmark IDs for finger tips
        self.tip_ids = [4, 8, 12, 16, 20]
        self.path_history = {"Left": [], "Right": []}
        self.max_history_len = 30
        self.hand_states = {
            "Left": {"pinched_middle": False, "pinch_time": 0},
            "Right": {"pinched_middle": False, "pinch_time": 0}
        }

    def fingers_up(self, lm_list):
        """Returns active finger states: [thumb, index, middle, ring, pinky] (1 if extended, 0 if folded)
        Uses Euclidean distance to make it perfectly accurate regardless of hand rotation."""
        if len(lm_list) < 21:
            return [0, 0, 0, 0, 0]
        
        fingers = []
        
        # Reference coordinates
        wrist_x, wrist_y = lm_list[0][1], lm_list[0][2]
        
        # 1. Thumb Logic (Robust for rotations): 
        # Check distance from Thumb Tip (4) to Pinky MCP (17) vs Thumb IP (3) to Pinky MCP (17)
        # If tip is further away from the other side of the hand, it is open.
        thumb_tip_dist = math.hypot(lm_list[4][1] - lm_list[17][1], lm_list[4][2] - lm_list[17][2])
        thumb_ip_dist = math.hypot(lm_list[3][1] - lm_list[17][1], lm_list[3][2] - lm_list[17][2])
        if thumb_tip_dist > thumb_ip_dist:
            fingers.append(1)
        else:
            fingers.append(0)
            
        # 2. Four Fingers Logic (Index, Middle, Ring, Pinky)
        # Distance from Wrist (0) to Tip must be greater than distance from Wrist to PIP joint
        for id in range(1, 5):
            tip_id = self.tip_ids[id]
            pip_id = tip_id - 2
            
            dist_tip = math.hypot(lm_list[tip_id][1] - wrist_x, lm_list[tip_id][2] - wrist_y)
            dist_pip = math.hypot(lm_list[pip_id][1] - wrist_x, lm_list[pip_id][2] - wrist_y)
            
            # If tip is further from the wrist than the PIP joint, the finger is open!
            if dist_tip > dist_pip:
                fingers.append(1)
            else:
                fingers.append(0)
                
        return fingers

    def recognize_pose(self, lm_list):
        """Static pose classifier utilizing ultra-accurate finger states"""
        if len(lm_list) < 21:
            return "None", 0.0
            
        fingers = self.fingers_up(lm_list)
        total_fingers = fingers.count(1)
        
        x4, y4 = lm_list[4][1], lm_list[4][2]
        x8, y8 = lm_list[8][1], lm_list[8][2]
        dist_index_thumb = math.hypot(x8 - x4, y8 - y4)
        
        x12, y12 = lm_list[12][1], lm_list[12][2]
        
        if total_fingers == 0:
            return "Fist", 0.95
        elif total_fingers == 5:
            return "Open Palm", 0.98
        elif fingers == [0, 1, 1, 0, 0]:
            return "Peace", 0.90
        elif fingers == [1, 0, 0, 0, 0]:
            # Thumbs Up/Down
            is_up = lm_list[4][2] < lm_list[3][2]
            return "Thumbs Up" if is_up else "Thumbs Down", 0.92
        elif fingers == [0, 1, 0, 0, 0] or fingers == [1, 1, 0, 0, 0]:
            return "Pointing", 0.95
        elif dist_index_thumb < 35 and fingers[2] == 1 and fingers[3] == 1 and fingers[4] == 1:
            return "OK Sign", 0.88
        elif dist_index_thumb < 35 and fingers[2] == 0:
            return "Pinch", 0.85
            
        return "Unknown", 0.50

    def detect_snap(self, hand_label, lm_list):
        if len(lm_list) < 21:
            return False

        x4, y4 = lm_list[4][1], lm_list[4][2]
        x12, y12 = lm_list[12][1], lm_list[12][2]
        dist = math.hypot(x12 - x4, y12 - y4)
        
        state = self.hand_states[hand_label]
        now = time.time()
        
        if dist < 25:
            if not state["pinched_middle"]:
                state["pinched_middle"] = True
                state["pinch_time"] = now
        elif dist > 85:
            if state["pinched_middle"]:
                time_elapsed = now - state["pinch_time"]
                state["pinched_middle"] = False
                if time_elapsed < 0.4:
                    return True
        
        if state["pinched_middle"] and (now - state["pinch_time"] > 1.0):
            state["pinched_middle"] = False

        return False

    def track_and_detect_dynamics(self, hand_label, lm_list):
        if len(lm_list) < 21:
            return "None"

        x, y = lm_list[8][1], lm_list[8][2]
        now = time.time()
        
        self.path_history[hand_label].append((x, y, now))
        if len(self.path_history[hand_label]) > self.max_history_len:
            self.path_history[hand_label].pop(0)
            
        pts = self.path_history[hand_label]
        if len(pts) < 10:
            return "None"
            
        recent_pts = pts[-6:]
        dx = recent_pts[-1][0] - recent_pts[0][0]
        dy = recent_pts[-1][1] - recent_pts[0][1]
        dt = recent_pts[-1][2] - recent_pts[0][2]
        
        if dt > 0 and dt < 0.35:
            speed_x = dx / dt
            if abs(speed_x) > 700 and abs(dy) < 80:
                self.path_history[hand_label].clear()
                return "Swipe Right" if speed_x > 0 else "Swipe Left"

        if len(pts) >= 18:
            xs = [p[0] for p in pts[-18:]]
            ys = [p[1] for p in pts[-18:]]
            
            width = max(xs) - min(xs)
            height = max(ys) - min(ys)
            
            if width > 70 and height > 70:
                cx, cy = np.mean(xs), np.mean(ys)
                radii = [math.hypot(p[0] - cx, p[1] - cy) for p in pts[-18:]]
                if np.std(radii) / np.mean(radii) < 0.22:
                    angles = [math.atan2(p[1] - cy, p[0] - cx) for p in pts[-18:]]
                    diffs = np.diff(np.sort(angles))
                    if (np.max(diffs) if len(diffs) > 0 else 2.0) < 1.4:
                        self.path_history[hand_label].clear()
                        return "Circular Command"

        return "None"

    def detect_two_hand_combo(self, active_hands):
        if len(active_hands) < 2:
            return "None"

        left_hand = next((h for h in active_hands if h["label"] == "Left"), None)
        right_hand = next((h for h in active_hands if h["label"] == "Right"), None)
        
        if not left_hand or not right_hand:
            return "None"

        left_pose, _ = self.recognize_pose(left_hand["lm_list"])
        right_pose, _ = self.recognize_pose(right_hand["lm_list"])
        
        lx, ly = left_hand["lm_list"][9][1], left_hand["lm_list"][9][2]
        rx, ry = right_hand["lm_list"][9][1], right_hand["lm_list"][9][2]
        dist = math.hypot(lx - rx, ly - ry)
        
        if left_pose == "Open Palm" and right_pose == "Open Palm":
            if dist > 320:
                return "Energy Blast"
            elif dist < 120:
                return "Dual Magic Shield"
                
        return "None"
