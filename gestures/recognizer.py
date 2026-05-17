import math

class GestureRecognizer:
    def __init__(self):
        # MediaPipe landmark IDs for finger tips
        self.tip_ids = [4, 8, 12, 16, 20]

    def fingers_up(self, lm_list):
        if len(lm_list) == 0:
            return []
        
        fingers = []
        
        # Thumb - varies by hand (left/right) but we do a simple x-coordinate check
        # Assuming right hand for simplicity, can be improved.
        if lm_list[self.tip_ids[0]][1] > lm_list[self.tip_ids[0] - 1][1]:
            fingers.append(1)
        else:
            fingers.append(0)
            
        # 4 Fingers
        for id in range(1, 5):
            if lm_list[self.tip_ids[id]][2] < lm_list[self.tip_ids[id] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)
                
        return fingers

    def recognize(self, lm_list):
        if not lm_list:
            return "None"
            
        fingers = self.fingers_up(lm_list)
        total_fingers = fingers.count(1)
        
        if total_fingers == 0:
            return "Fist"
        elif total_fingers == 5:
            return "Open Palm"
        elif fingers == [0, 1, 1, 0, 0]:
            return "Peace"
        elif fingers == [1, 0, 0, 0, 0]:
            return "Thumbs Up"
        elif fingers == [0, 1, 0, 0, 0]:
            return "Pointing"
        elif fingers[1:] == [0, 1, 1, 1]:  # Index is down, others up (roughly OK sign)
            # Calculate distance between thumb tip and index tip for OK sign
            x1, y1 = lm_list[4][1], lm_list[4][2]
            x2, y2 = lm_list[8][1], lm_list[8][2]
            length = math.hypot(x2 - x1, y2 - y1)
            if length < 40:
                return "OK Sign"
            
        return "Unknown"
