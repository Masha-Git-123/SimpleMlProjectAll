import cv2
import numpy as np
import time

# Start webcam
cap = cv2.VideoCapture(0)

# Give the camera some time to warm up
time.sleep(2)

# Capture the background (without you in frame ideally)
print("Capturing background... Please move out of the frame!")
for i in range(30):  # capture multiple frames for better background
    ret, background = cap.read()
background = np.flip(background, axis=1)  # flip to avoid mirror effect

print("Background captured. Now show the color you want to hide!")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Flip frame for mirror-like view
    frame = np.flip(frame, axis=1)

    # Convert to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Define range for the color you want to hide (example: red cloak)
    lower_red1 = np.array([0, 120, 70])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 120, 70])
    upper_red2 = np.array([180, 255, 255])

    # Create masks
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = mask1 + mask2

    # Refine mask (smooth edges)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3,3), np.uint8))
    mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, np.ones((3,3), np.uint8))

    # Invert mask
    mask_inv = cv2.bitwise_not(mask)

    # Segment out the red color from the frame
    res1 = cv2.bitwise_and(frame, frame, mask=mask_inv)

    # Replace it with background
    res2 = cv2.bitwise_and(background, background, mask=mask)

    # Final output
    final = cv2.addWeighted(res1, 1, res2, 1, 0)

    cv2.imshow("Invisible Cloak Effect", final)

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
