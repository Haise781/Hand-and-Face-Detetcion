import cv2
import numpy as np
import time
import math

class HolographicOverlays:
    def __init__(self):
        # 3D Cube Vertices (relative coordinates)
        self.cube_vertices = [
            [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
            [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]
        ]
        # Connections between vertices
        self.cube_edges = [
            (0, 1), (1, 2), (2, 3), (3, 0), # Back face
            (4, 5), (5, 6), (6, 7), (7, 4), # Front face
            (0, 4), (1, 5), (2, 6), (3, 7)  # Connecting edges
        ]
        
    def rotate_3d_point(self, x, y, z, angle_x, angle_y, angle_z):
        """Rotates a 3D point in space using basic rotation matrices"""
        # Rotate around X-axis
        rad_x = math.radians(angle_x)
        cos_x, sin_x = math.cos(rad_x), math.sin(rad_x)
        y1 = y * cos_x - z * sin_x
        z1 = y * sin_x + z * cos_x
        x1 = x

        # Rotate around Y-axis
        rad_y = math.radians(angle_y)
        cos_y, sin_y = math.cos(rad_y), math.sin(rad_y)
        x2 = x1 * cos_y + z1 * sin_y
        z2 = -x1 * sin_y + z1 * cos_y
        y2 = y1

        # Rotate around Z-axis
        rad_z = math.radians(angle_z)
        cos_z, sin_z = math.cos(rad_z), math.sin(rad_z)
        x3 = x2 * cos_z - y2 * sin_z
        y3 = x2 * sin_z + y2 * cos_z
        z3 = z2

        return x3, y3, z3

    def draw_hologram(self, frame, lm_list, hand_index=0, gesture="None"):
        """Draws spinning 3D hologram above palm and sci-fi HUD telemetry around hand"""
        if len(lm_list) < 21:
            return frame

        h, w, c = frame.shape
        
        # Palm Center is roughly landmark 9 (MCP of middle finger)
        cx, cy = lm_list[9][1], lm_list[9][2]
        # Wrist is landmark 0
        wx, wy = lm_list[0][1], lm_list[0][2]
        
        # Scale of hologram based on distance from wrist to palm
        hand_scale = int(math.hypot(cx - wx, cy - wy) * 0.6)
        hand_scale = max(20, min(hand_scale, 150))
        
        # Current time for rotation angles
        t = time.time()
        rot_angle_y = (t * 120) % 360
        rot_angle_x = (t * 60) % 360
        rot_angle_z = (t * 30) % 360
        
        # Create an overlay layer for alpha blending (glow effect)
        overlay = frame.copy()
        
        # ----------------------------------------------------
        # 1. 3D Spinning Holographic Cube (Hovering above Palm)
        # ----------------------------------------------------
        # The center of the floating hologram is above the palm center
        hologram_center_y = cy - int(hand_scale * 1.5)
        hologram_center_x = cx
        
        # Project and draw 3D cube vertices
        projected_pts = []
        for vertex in self.cube_vertices:
            # Scale the vertex
            vx, vy, vz = [v * hand_scale * 0.4 for v in vertex]
            # Rotate
            rx, ry, rz = self.rotate_3d_point(vx, vy, vz, rot_angle_x, rot_angle_y, rot_angle_z)
            
            # Simple perspective projection: smaller scale as depth Z increases
            # Normalized depth Z goes from roughly -0.5 to 0.5
            dist_factor = 1.0 + (rz / (hand_scale * 2.0))
            px = int(hologram_center_x + rx / dist_factor)
            py = int(hologram_center_y + ry / dist_factor)
            projected_pts.append((px, py))
            
            # Draw tiny glowing nodes on the cube
            cv2.circle(overlay, (px, py), 3, (0, 255, 255), -1)
            cv2.circle(overlay, (px, py), 5, (0, 255, 255), 1)

        # Draw cube edges
        for start, end in self.cube_edges:
            p1 = projected_pts[start]
            p2 = projected_pts[end]
            cv2.line(overlay, p1, p2, (255, 0, 255), 2)
            
        # Draw beam connecting Palm Center to Hologram Center
        cv2.line(overlay, (cx, cy), (hologram_center_x, hologram_center_y), (0, 255, 255), 1, cv2.LINE_AA)
        # Concentric dotted rings along the beam
        num_rings = 4
        for i in range(1, num_rings):
            frac = i / num_rings
            rx = int(cx + (hologram_center_x - cx) * frac)
            ry = int(cy + (hologram_center_y - cy) * frac)
            cv2.circle(overlay, (rx, ry), int(hand_scale * 0.15 * frac), (0, 255, 255), 1)

        # ----------------------------------------------------
        # 2. Concentric Telemetry Rings (Around Palm Center)
        # ----------------------------------------------------
        # Inner rotating ring (Cyan)
        num_segments = 8
        for i in range(num_segments):
            start_angle = int(i * (360 / num_segments) + (t * 80))
            end_angle = int(start_angle + (360 / (num_segments * 2)))
            cv2.ellipse(overlay, (cx, cy), (int(hand_scale * 0.7), int(hand_scale * 0.7)), 0, start_angle, end_angle, (0, 255, 255), 2)

        # Outer rotating ring (Magenta)
        for i in range(num_segments // 2):
            start_angle = int(i * (360 / (num_segments // 2)) - (t * 40))
            end_angle = int(start_angle + 30)
            cv2.ellipse(overlay, (cx, cy), (int(hand_scale * 0.9), int(hand_scale * 0.9)), 0, start_angle, end_angle, (255, 0, 255), 1)

        # ----------------------------------------------------
        # 3. Target Reticle on Index Finger (Lock-on effect)
        # ----------------------------------------------------
        ix, iy = lm_list[8][1], lm_list[8][2] # Index Tip
        reticle_r = int(hand_scale * 0.3)
        cv2.circle(overlay, (ix, iy), reticle_r, (0, 255, 0), 1)
        # Drawing crosshair ticks
        cv2.line(overlay, (ix - reticle_r - 5, iy), (ix - reticle_r + 5, iy), (0, 255, 0), 2)
        cv2.line(overlay, (ix + reticle_r - 5, iy), (ix + reticle_r + 5, iy), (0, 255, 0), 2)
        cv2.line(overlay, (ix, iy - reticle_r - 5), (ix, iy - reticle_r + 5), (0, 255, 0), 2)
        cv2.line(overlay, (ix, iy + reticle_r - 5), (ix, iy + reticle_r + 5), (0, 255, 0), 2)

        # ----------------------------------------------------
        # 4. Floating Telemetry Card (Lock-on stats)
        # ----------------------------------------------------
        card_x = cx + int(hand_scale * 1.2)
        card_y = cy - int(hand_scale * 0.5)
        
        # Draw tech line connecting palm to the text card
        cv2.line(overlay, (cx, cy), (card_x, card_y), (0, 255, 255), 1)
        cv2.line(overlay, (card_x, card_y), (card_x + 120, card_y), (0, 255, 255), 1)
        
        # Telemetry Text
        cv2.putText(overlay, f"HAND: #{hand_index + 1}", (card_x + 5, card_y - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(overlay, f"GEST: {gesture}", (card_x + 5, card_y - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 255), 1, cv2.LINE_AA)
        cv2.putText(overlay, f"POS: {cx},{cy}", (card_x + 5, card_y + 4), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 0), 1, cv2.LINE_AA)
        cv2.putText(overlay, f"LOCK: OPTIMAL", (card_x + 5, card_y + 16), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 255), 1, cv2.LINE_AA)

        # Draw a bounding bounding-bracket around the entire hand
        # Find min/max X and Y of hand landmarks
        xs = [lm[1] for lm in lm_list]
        ys = [lm[2] for lm in lm_list]
        min_x, max_x = min(xs) - 15, max(xs) + 15
        min_y, max_y = min(ys) - 15, max(ys) + 15
        
        # Draw fancy corners for bounding box (glowing green/cyan)
        l = int(hand_scale * 0.25)
        # Top-Left corner
        cv2.line(overlay, (min_x, min_y), (min_x + l, min_y), (0, 255, 255), 2)
        cv2.line(overlay, (min_x, min_y), (min_x, min_y + l), (0, 255, 255), 2)
        # Top-Right corner
        cv2.line(overlay, (max_x, min_y), (max_x - l, min_y), (0, 255, 255), 2)
        cv2.line(overlay, (max_x, min_y), (max_x, min_y + l), (0, 255, 255), 2)
        # Bottom-Left corner
        cv2.line(overlay, (min_x, max_y), (min_x + l, max_y), (0, 255, 255), 2)
        cv2.line(overlay, (min_x, max_y), (min_x, max_y - l), (0, 255, 255), 2)
        # Bottom-Right corner
        cv2.line(overlay, (max_x, max_y), (max_x - l, max_y), (0, 255, 255), 2)
        cv2.line(overlay, (max_x, max_y), (max_x, max_y - l), (0, 255, 255), 2)

        # Alpha blend to make the HUD feel glowing and semi-transparent
        alpha = 0.8
        cv2.addWeighted(overlay, alpha, frame, 1.0 - alpha, 0, frame)
        return frame
