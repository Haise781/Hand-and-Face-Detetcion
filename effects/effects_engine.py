import cv2
import numpy as np

class ProfessionalOverlayEngine:
    def __init__(self):
        # Professional Red & Obsidian Theme
        self.primary_color = (0, 0, 255)     # Deep Red
        self.accent_color = (0, 50, 255)     # Scarlet Red
        self.highlight_color = (200, 200, 255) # White-Red Core

    def draw_hud_brackets(self, img, bbox, color, thickness=2, length=20):
        """Draws professional sci-fi target brackets around the hand"""
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
        cv2.circle(img, (cx, cy), radius, self.primary_color, 1, cv2.LINE_AA)
        cv2.circle(img, (cx, cy), 2, self.highlight_color, -1, cv2.LINE_AA)
        
        # Crosshair lines
        offset = 5
        length = 10
        cv2.line(img, (cx - offset - length, cy), (cx - offset, cy), self.primary_color, 2)
        cv2.line(img, (cx + offset, cy), (cx + offset + length, cy), self.primary_color, 2)
        cv2.line(img, (cx, cy - offset - length), (cx, cy - offset), self.primary_color, 2)
        cv2.line(img, (cx, cy + offset), (cx, cy + offset + length), self.primary_color, 2)

    def process_hand_overlays(self, img, active_hands):
        """Renders the sleek cyber-HUD elements over detected hands"""
        h_img, w_img, _ = img.shape
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
            self.draw_hud_brackets(overlay, bbox, self.primary_color, thickness=2, length=int(w * 0.15))
            
            # Draw tracking reticle at the palm center (landmark 9)
            cx, cy = lm_list[9][1], lm_list[9][2]
            self.draw_tracking_reticle(overlay, (cx, cy), radius=20)
            
            # Draw info tag
            label = hand["label"]
            text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
            cv2.rectangle(overlay, (x_min, y_min - 25), (x_min + text_size[0] + 10, y_min), self.primary_color, -1)
            cv2.putText(overlay, label.upper(), (x_min + 5, y_min - 7), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

        # Alpha blend the overlays
        cv2.addWeighted(overlay, 0.7, img, 0.3, 0, img)
        return img
