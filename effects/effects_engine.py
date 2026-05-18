import cv2
import numpy as np
import math
import time
from utils.overlays import HolographicOverlays

class ProfessionalOverlayEngine:
    def __init__(self):
        # Interactive Theme Palettes
        self.themes = {
            "Red Alert": {
                "primary": (0, 0, 255),       # Neon Crimson Red
                "accent": (0, 75, 255),       # Scarlet Red
                "highlight": (200, 200, 255), # High contrast core
                "text": (255, 255, 255)
            },
            "Matrix Green": {
                "primary": (0, 255, 102),     # Glowing Lime Green
                "accent": (0, 200, 0),        # Deep Matrix Green
                "highlight": (220, 255, 220), # Light Green Core
                "text": (255, 255, 255)
            },
            "Synthwave": {
                "primary": (255, 255, 0),     # Cyber Cyan
                "accent": (255, 0, 255),      # Synth Magenta
                "highlight": (255, 255, 255), # Pure White
                "text": (255, 255, 255)
            }
        }
        self.current_theme = "Red Alert"
        self.holo_renderer = HolographicOverlays()
        
        # Facemesh Connection Indices for Futuristic Sci-Fi Wireframe Mesh
        self.face_oval = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136, 172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109]
        self.left_eyebrow = [70, 63, 105, 66, 107]
        self.right_eyebrow = [336, 296, 334, 293, 300]
        self.left_eye_ring = [33, 160, 158, 133, 153, 144]
        self.right_eye_ring = [263, 387, 385, 362, 380, 373]

    def set_theme(self, theme_name):
        if theme_name in self.themes:
            self.current_theme = theme_name

    def get_colors(self):
        return self.themes[self.current_theme]

    def draw_hud_brackets(self, img, bbox, color, thickness=2, length=20):
        """Draws professional sci-fi target brackets around a bounding box"""
        x, y, w, h = bbox
        
        # Top-left corner
        cv2.line(img, (x, y), (x + length, y), color, thickness)
        cv2.line(img, (x, y), (x, y + length), color, thickness)
        
        # Top-right corner
        cv2.line(img, (x + w, y), (x + w - length, y), color, thickness)
        cv2.line(img, (x + w, y), (x + w, y + length), color, thickness)
        
        # Bottom-left corner
        cv2.line(img, (x, y + h), (x + length, y + h), color, thickness)
        cv2.line(img, (x, y + h), (x, y + h - length), color, thickness)
        
        # Bottom-right corner
        cv2.line(img, (x + w, y + h), (x + w - length, y + h), color, thickness)
        cv2.line(img, (x + w, y + h), (x + w, y + h - length), color, thickness)

    def draw_tracking_reticle(self, img, center, radius=15):
        """Draws a clean, professional tracking crosshair/reticle"""
        cx, cy = center
        colors = self.get_colors()
        
        cv2.circle(img, (cx, cy), radius, colors["primary"], 1, cv2.LINE_AA)
        cv2.circle(img, (cx, cy), 2, colors["highlight"], -1, cv2.LINE_AA)
        
        # Crosshair lines
        offset = 5
        length = 10
        cv2.line(img, (cx - offset - length, cy), (cx - offset, cy), colors["primary"], 2)
        cv2.line(img, (cx + offset, cy), (cx + offset + length, cy), colors["primary"], 2)
        cv2.line(img, (cx, cy - offset - length), (cx, cy - offset), colors["primary"], 2)
        cv2.line(img, (cx, cy + offset), (cx, cy + offset + length), colors["primary"], 2)

    def process_hand_overlays(self, img, active_hands, mode="3D Hologram"):
        """Renders the sleek cyber-HUD elements over detected hands"""
        h_img, w_img, _ = img.shape
        colors = self.get_colors()
        
        # If Hologram mode is chosen, we let HolographicOverlays handle the rendering!
        if mode == "3D Hologram":
            for idx, hand in enumerate(active_hands):
                # Pass physical label and coordinates to the holographic overlay engine
                lm_list = hand["lm_list"]
                active_gest = hand.get("gesture", "None")
                img = self.holo_renderer.draw_hologram(img, lm_list, hand_index=idx, gesture=active_gest)
            return img

        # Fallback Standard Cyberpunk HUD
        overlay = img.copy()
        for hand in active_hands:
            lm_list = hand["lm_list"]
            
            # Calculate hand bounding box
            x_min = min([lm[1] for lm in lm_list])
            x_max = max([lm[1] for lm in lm_list])
            y_min = min([lm[2] for lm in lm_list])
            y_max = max([lm[2] for lm in lm_list])
            
            # Add padding
            pad = 20
            x_min = max(0, x_min - pad)
            y_min = max(0, y_min - pad)
            x_max = min(w_img, x_max + pad)
            y_max = min(h_img, y_max + pad)
            
            w = x_max - x_min
            h = y_max - y_min
            bbox = (x_min, y_min, w, h)

            # Draw clean brackets
            self.draw_hud_brackets(overlay, bbox, colors["primary"], thickness=2, length=int(w * 0.15))
            
            # Draw tracking reticle at the palm center (landmark 9)
            cx, cy = lm_list[9][1], lm_list[9][2]
            self.draw_tracking_reticle(overlay, (cx, cy), radius=20)
            
            # Draw info tag
            label = hand["label"]
            gesture = hand.get("gesture", "None")
            tag_text = f"{label.upper()} | {gesture.upper()}"
            text_size = cv2.getTextSize(tag_text, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)[0]
            
            cv2.rectangle(overlay, (x_min, y_min - 25), (x_min + text_size[0] + 12, y_min), colors["primary"], -1)
            cv2.putText(overlay, tag_text, (x_min + 6, y_min - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.4, colors["text"], 1, cv2.LINE_AA)

        # Alpha blend the overlays
        cv2.addWeighted(overlay, 0.75, img, 0.25, 0, img)
        return img

    def process_face_overlays(self, img, active_faces):
        """Renders incredible cybernetic wireframes and telemetry locks over face mesh"""
        if not active_faces:
            return img
            
        h_img, w_img, _ = img.shape
        colors = self.get_colors()
        overlay = img.copy()
        
        for face in active_faces:
            lm_list = face["lm_list"]
            is_drowsy = face.get("drowsy", False)
            
            # Override theme colors to Tactical Alert Red if drowsiness is flagged
            if is_drowsy:
                colors = {
                    "primary": (0, 0, 255),       # Crimson warning red
                    "accent": (0, 0, 255),        # Scarlet warning red
                    "highlight": (255, 255, 255), # High contrast white
                    "text": (255, 255, 255)
                }
                # Render full-screen semi-transparent alert flash
                cv2.rectangle(overlay, (0, 0), (w_img, h_img), (0, 0, 100), -1)
                cv2.putText(overlay, "CRITICAL WARNING: USER DROWSINESS DETECTED // AUDIBLE ALERT ON", (20, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 255), 2, cv2.LINE_AA)
            else:
                colors = self.get_colors()
            
            # 1. Bounding Box & Target Brackets
            xs = [lm[1] for lm in lm_list]
            ys = [lm[2] for lm in lm_list]
            x_min, x_max = max(0, min(xs) - 10), min(w_img, max(xs) + 10)
            y_min, y_max = max(0, min(ys) - 15), min(h_img, max(ys) + 10)
            
            w = x_max - x_min
            h = y_max - y_min
            
            # Draw brackets around face
            self.draw_hud_brackets(overlay, (x_min, y_min, w, h), colors["accent"], thickness=1, length=int(w * 0.12))
            
            # 2. Draw Futuristic Wireframe Contour and Eyebrows
            # Face Oval
            for idx in range(len(self.face_oval) - 1):
                p1 = lm_list[self.face_oval[idx]]
                p2 = lm_list[self.face_oval[idx+1]]
                cv2.line(overlay, (p1[1], p1[2]), (p2[1], p2[2]), colors["primary"], 1, cv2.LINE_AA)
            # Close face oval
            p_first = lm_list[self.face_oval[0]]
            p_last = lm_list[self.face_oval[-1]]
            cv2.line(overlay, (p_first[1], p_first[2]), (p_last[1], p_last[2]), colors["primary"], 1, cv2.LINE_AA)
            
            # Eyebrows
            for idx in range(len(self.left_eyebrow) - 1):
                p1 = lm_list[self.left_eyebrow[idx]]
                p2 = lm_list[self.left_eyebrow[idx+1]]
                cv2.line(overlay, (p1[1], p1[2]), (p2[1], p2[2]), colors["accent"], 1, cv2.LINE_AA)
            for idx in range(len(self.right_eyebrow) - 1):
                p1 = lm_list[self.right_eyebrow[idx]]
                p2 = lm_list[self.right_eyebrow[idx+1]]
                cv2.line(overlay, (p1[1], p1[2]), (p2[1], p2[2]), colors["accent"], 1, cv2.LINE_AA)

            # 3. Eye Tracking concentric reticles (left & right pupil)
            for eye_side in ["left", "right"]:
                pupil = face[f"{eye_side}_pupil"]
                is_blinking = face[f"{eye_side}_blink"]
                
                if pupil:
                    cx, cy = pupil
                    if is_blinking:
                        # Draw warning flash if blinking
                        cv2.circle(overlay, (cx, cy), 8, (0, 0, 255), -1, cv2.LINE_AA)
                        cv2.putText(overlay, "BLINK!", (cx - 16, cy - 12), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 255), 1, cv2.LINE_AA)
                    else:
                        # Draw neat concentric crosshair targets over eye pupils
                        t = time.time()
                        angle = (t * 150) % 360
                        
                        cv2.circle(overlay, (cx, cy), 6, colors["primary"], 1, cv2.LINE_AA)
                        cv2.circle(overlay, (cx, cy), 1, colors["highlight"], -1, cv2.LINE_AA)
                        
                        # Spinning outer tick circle
                        cv2.ellipse(overlay, (cx, cy), (12, 12), angle, 0, 90, colors["accent"], 1, cv2.LINE_AA)
                        cv2.ellipse(overlay, (cx, cy), (12, 12), angle, 180, 270, colors["accent"], 1, cv2.LINE_AA)
                        
            # 4. Neural Scan Telemetry Card
            card_x = x_max + 15
            card_y = y_min + 30
            if card_x + 150 < w_img:
                # Tech connector lines
                cv2.line(overlay, (x_max - 5, y_min + 20), (card_x, card_y), colors["accent"], 1)
                cv2.line(overlay, (card_x, card_y), (card_x + 140, card_y), colors["accent"], 1)
                
                # Dynamic info list
                cv2.putText(overlay, "SYSTEM: COGNITIVE HUD", (card_x + 5, card_y - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.35, colors["primary"], 1, cv2.LINE_AA)
                cv2.putText(overlay, f"SUBJECT: NEURAL_USR_{face['index']}", (card_x + 5, card_y - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.35, colors["highlight"], 1, cv2.LINE_AA)
                
                blink_l = "ACTIVE" if face["left_blink"] else "NORMAL"
                blink_r = "ACTIVE" if face["right_blink"] else "NORMAL"
                cv2.putText(overlay, f"EYE STATUS: [L:{blink_l}|R:{blink_r}]", (card_x + 5, card_y + 8), cv2.FONT_HERSHEY_SIMPLEX, 0.3, colors["accent"], 1, cv2.LINE_AA)
                
                if face["left_pupil"] and face["right_pupil"]:
                    lx, ly = face["left_pupil"]
                    rx, ry = face["right_pupil"]
                    cv2.putText(overlay, f"GAZE LOCK: [{lx},{ly}]", (card_x + 5, card_y + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.3, colors["primary"], 1, cv2.LINE_AA)
                else:
                    cv2.putText(overlay, "GAZE LOCK: TRACKING...", (card_x + 5, card_y + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 255), 1, cv2.LINE_AA)

        # Alpha blend to make the HUD feel glowing and semi-transparent
        cv2.addWeighted(overlay, 0.8, img, 0.2, 0, img)
        return img
