import cv2
import numpy as np
import mediapipe as mp

# Mediapipe Pose + Hands
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7, min_tracking_confidence=0.7)

# Webcam
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Flip for mirror effect
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape

    # Convert to RGB
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    pose_results = pose.process(rgb)
    hand_results = hands.process(rgb)

    # Avatar canvas (white background, same size as frame)
    avatar = 255 * np.ones_like(frame)

    # ---------------- BODY ----------------
    if pose_results.pose_landmarks:
        landmarks = pose_results.pose_landmarks.landmark
        points = {}
        for i, lm in enumerate(landmarks):
            x, y = int(lm.x * w), int(lm.y * h)
            points[i] = (x, y)

        connections = [
            (11, 13), (13, 15),  # Left arm
            (12, 14), (14, 16),  # Right arm
            (11, 12),            # Shoulders
            (23, 24),            # Hips
            (11, 23), (12, 24),  # Torso
            (23, 25), (25, 27),  # Left leg
            (24, 26), (26, 28)   # Right leg
        ]

        for (i, j) in connections:
            if i in points and j in points:
                cv2.line(avatar, points[i], points[j], (0, 100, 200), 10)

        # Head
        if 11 in points and 12 in points:
            sx = (points[11][0] + points[12][0]) // 2
            sy = (points[11][1] + points[12][1]) // 2
            cv2.circle(avatar, (sx, sy - 40), 45, (0, 150, 200), -1)
            cv2.circle(avatar, (sx - 15, sy - 50), 6, (255, 255, 255), -1)
            cv2.circle(avatar, (sx + 15, sy - 50), 6, (255, 255, 255), -1)
            cv2.ellipse(avatar, (sx, sy - 30), (20, 10), 0, 0, 180, (255, 255, 255), 3)

    # ---------------- HANDS ----------------
    if hand_results.multi_hand_landmarks:
        for handLms in hand_results.multi_hand_landmarks:
            hand_points = []
            for lm in handLms.landmark:
                x, y = int(lm.x * w), int(lm.y * h)
                hand_points.append((x, y))

            # Draw fingers (simple lines)
            finger_pairs = [
                (0, 1), (1, 2), (2, 3), (3, 4),      # Thumb
                (0, 5), (5, 6), (6, 7), (7, 8),      # Index
                (5, 9), (9, 10), (10, 11), (11, 12), # Middle
                (9, 13), (13, 14), (14, 15), (15, 16), # Ring
                (13, 17), (17, 18), (18, 19), (19, 20), # Pinky
            ]

            for (i, j) in finger_pairs:
                cv2.line(avatar, hand_points[i], hand_points[j], (200, 50, 100), 4)

            # ---------------- HEART GESTURE DETECTION ----------------
            # If index fingertips of both hands are close, draw a heart ❤️
            if len(hand_results.multi_hand_landmarks) == 2:
                h1 = hand_results.multi_hand_landmarks[0]
                h2 = hand_results.multi_hand_landmarks[1]
                p1 = (int(h1.landmark[8].x * w), int(h1.landmark[8].y * h))  # index tip hand1
                p2 = (int(h2.landmark[8].x * w), int(h2.landmark[8].y * h))  # index tip hand2
                dist = np.linalg.norm(np.array(p1) - np.array(p2))

                if dist < 50:  # fingers close → draw heart
                    cx = (p1[0] + p2[0]) // 2
                    cy = (p1[1] + p2[1]) // 2
                    # Draw cartoon heart
                    cv2.circle(avatar, (cx - 20, cy), 20, (0, 0, 255), -1)
                    cv2.circle(avatar, (cx + 20, cy), 20, (0, 0, 255), -1)
                    pts = np.array([[cx - 40, cy], [cx + 40, cy], [cx, cy + 60]], np.int32)
                    cv2.fillPoly(avatar, [pts], (0, 0, 255))

    # ---------------- COMBINE ----------------
    avatar_resized = cv2.resize(avatar, (w, h))
    combined = np.hstack((avatar_resized, frame))

    cv2.imshow("Me and Avatar", combined)

    if cv2.waitKey(1) & 0xFF == 27:  # ESC to exit
        break

cap.release()
cv2.destroyAllWindows()
