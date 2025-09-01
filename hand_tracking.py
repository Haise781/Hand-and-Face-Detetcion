import cv2
import numpy as np
import time
from datetime import datetime

# Load Haar Cascade for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# -------------------------
# Helper Functions
# -------------------------
def draw_fancy_box(img, x, y, w, h, color=(0,255,0), thickness=2, l=30):
    """Draws a fancy corner rectangle"""
    # Top-left
    cv2.line(img, (x, y), (x+l, y), color, thickness)
    cv2.line(img, (x, y), (x, y+l), color, thickness)
    # Top-right
    cv2.line(img, (x+w, y), (x+w-l, y), color, thickness)
    cv2.line(img, (x+w, y), (x+w, y+l), color, thickness)
    # Bottom-left
    cv2.line(img, (x, y+h), (x+l, y+h), color, thickness)
    cv2.line(img, (x, y+h), (x, y+h-l), color, thickness)
    # Bottom-right
    cv2.line(img, (x+w, y+h), (x+w-l, y+h), color, thickness)
    cv2.line(img, (x+w, y+h), (x+w, y+h-l), color, thickness)

def detect_hands(frame):
    """Detect hands using skin color segmentation"""
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_skin = np.array([0, 20, 70], dtype=np.uint8)
    upper_skin = np.array([20, 255, 255], dtype=np.uint8)
    mask = cv2.inRange(hsv, lower_skin, upper_skin)
    mask = cv2.GaussianBlur(mask, (7,7), 0)

    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    hand_boxes = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 2500:  # filter noise
            x, y, w_box, h_box = cv2.boundingRect(cnt)
            hand_boxes.append((x, y, w_box, h_box))
    return hand_boxes

def save_snapshot(frame, tag="detection"):
    """Save a snapshot with timestamp"""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{tag}_{ts}.jpg"
    cv2.imwrite(filename, frame)
    print(f"[INFO] Snapshot saved: {filename}")

# -------------------------
# Main Program
# -------------------------
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Cannot access camera.")
    exit()

prev_time = 0
last_snapshot_time = 0

print("[INFO] Starting Face & Hand Detection System... Press 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to grab frame.")
        break

    frame = cv2.flip(frame, 1)  # Mirror effect
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    h, w, _ = frame.shape

    # Face Detection
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
    for idx, (x, y, fw, fh) in enumerate(faces):
        draw_fancy_box(frame, x, y, fw, fh, color=(0,255,0), thickness=2)
        cv2.putText(frame, f'Face #{idx+1}', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)

    # Hand Detection
    hand_boxes = detect_hands(frame)
    for idx, (hx, hy, hw_box, hh_box) in enumerate(hand_boxes):
        draw_fancy_box(frame, hx, hy, hw_box, hh_box, color=(0,0,255), thickness=2)
        cv2.putText(frame, f'Hand #{idx+1}', (hx, hy-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 2)

    # FPS Calculation
    curr_time = time.time()
    fps = 1/(curr_time - prev_time) if prev_time else 0
    prev_time = curr_time

    # Info Panel (Top Left)
    cv2.rectangle(frame, (10,10), (260,130), (50,50,50), -1)  # background
    cv2.putText(frame, "Detection Info", (20,35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 2)
    cv2.putText(frame, f'Faces: {len(faces)}', (20,65), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)
    cv2.putText(frame, f'Hands: {len(hand_boxes)}', (20,90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)
    cv2.putText(frame, f'FPS: {int(fps)}', (20,115), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)

    # Alert if too many faces/hands
    if len(faces) >= 3:
        cv2.putText(frame, "⚠ Too many faces detected!", (w//4, h-40), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,0,255), 3)
    if len(hand_boxes) >= 2:
        cv2.putText(frame, "⚠ Multiple hands detected!", (w//4, h-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255,0,0), 3)

    # Auto snapshot every 5s if detection
    if (len(faces) > 0 or len(hand_boxes) > 0) and (curr_time - last_snapshot_time > 5):
        save_snapshot(frame, tag="capture")
        last_snapshot_time = curr_time

    # Show Output
    cv2.imshow("Smart Face & Hand Detection System", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
