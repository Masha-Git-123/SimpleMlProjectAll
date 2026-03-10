import cv2
import mediapipe as mp
import numpy as np

# Mediapipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape

    # Create blank canvas for avatar
    avatar = np.ones_like(frame) * 255  # white background

    # Detect pose
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb)

    if results.pose_landmarks:
        lm = results.pose_landmarks.landmark

        def get_point(id):
            return int(lm[id].x * w), int(lm[id].y * h)

        # Key points
        left_shoulder, right_shoulder = get_point(11), get_point(12)
        left_elbow, right_elbow = get_point(13), get_point(14)
        left_wrist, right_wrist = get_point(15), get_point(16)
        left_hip, right_hip = get_point(23), get_point(24)
        left_knee, right_knee = get_point(25), get_point(26)
        left_ankle, right_ankle = get_point(27), get_point(28)

        # Center shift for avatar drawing
        shift_x, shift_y = 200, 100

        def shift(p):
            return (p[0] // 3 + shift_x, p[1] // 3 + shift_y)

        # Draw helpers
        def draw_line(img, p1, p2, color=(200, 0, 200), thickness=8):
            cv2.line(img, shift(p1), shift(p2), color, thickness)

        def draw_joint(img, p, color=(0, 150, 255), radius=12):
            cv2.circle(img, shift(p), radius, color, -1)

        # Avatar head
        head_center_x = (left_shoulder[0] + right_shoulder[0]) // 2
        head_center_y = (left_shoulder[1] + right_shoulder[1]) // 2 - 80
        head_pos = shift((head_center_x, head_center_y))
        cv2.circle(avatar, head_pos, 50, (0, 200, 255), -1)  # face
        cv2.circle(avatar, (head_pos[0]-15, head_pos[1]-10), 8, (0,0,0), -1)  # left eye
        cv2.circle(avatar, (head_pos[0]+15, head_pos[1]-10), 8, (0,0,0), -1)  # right eye
        cv2.ellipse(avatar, (head_pos[0], head_pos[1]+15), (20,10), 0, 0, 180, (0,0,0), 3)  # smile

        # Torso
        draw_line(avatar, left_shoulder, right_shoulder, (100,0,200))
        draw_line(avatar, left_shoulder, left_hip, (100,0,200))
        draw_line(avatar, right_shoulder, right_hip, (100,0,200))
        draw_line(avatar, left_hip, right_hip, (100,0,200))

        # Arms
        draw_line(avatar, left_shoulder, left_elbow)
        draw_line(avatar, left_elbow, left_wrist)
        draw_line(avatar, right_shoulder, right_elbow)
        draw_line(avatar, right_elbow, right_wrist)

        # Legs
        draw_line(avatar, left_hip, left_knee)
        draw_line(avatar, left_knee, left_ankle)
        draw_line(avatar, right_hip, right_knee)
        draw_line(avatar, right_knee, right_ankle)

        # Hands & feet
        cv2.circle(avatar, shift(left_wrist), 15, (255,200,0), -1)
        cv2.circle(avatar, shift(right_wrist), 15, (255,200,0), -1)
        cv2.circle(avatar, shift(left_ankle), 18, (0,200,100), -1)
        cv2.circle(avatar, shift(right_ankle), 18, (0,200,100), -1)

        # Joints
        for pt in [left_shoulder, right_shoulder, left_elbow, right_elbow,
                   left_wrist, right_wrist, left_hip, right_hip,
                   left_knee, right_knee]:
            draw_joint(avatar, pt)

    # Resize both sides
    avatar_resized = cv2.resize(avatar, (w//2, h))
    frame_resized = cv2.resize(frame, (w//2, h))

    # Combine: Left (Avatar) + Right (Webcam)
    combined = np.hstack((avatar_resized, frame_resized))

    cv2.imshow("Avatar + Webcam", combined)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
