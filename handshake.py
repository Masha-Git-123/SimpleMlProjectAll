import cv2
import mediapipe as mp
import pyautogui
import time
from collections import deque

# ✅ Smooth scroll functions
def smooth_scroll_down(steps=6, delay=0.01):
    for _ in range(steps):
        pyautogui.scroll(-50)
        time.sleep(delay)

def smooth_scroll_up(steps=6, delay=0.01):
    for _ in range(steps):
        pyautogui.scroll(50)
        time.sleep(delay)

# ✅ Webcam setup
cap = cv2.VideoCapture(0)
cap.set(3, 320)
cap.set(4, 240)

# ✅ MediaPipe setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)
mp_draw = mp.solutions.drawing_utils

# ✅ Gesture map
gesture_map = {
    0: 'Scroll Down',
    1: 'Forward',
    2: 'Play',
    3: 'Rewind',
    4: 'Pause',
    5: 'Scroll Up',
}

# ✅ Gesture logic
gesture_buffer = deque(maxlen=3)
last_action_time = time.time()
gesture_trigger_delay = 0.5
last_gesture = None
is_playing = False

# ✅ Floating webcam window
window_name = "🖐️ YouTube Gesture Controller (Smooth Scroll)"
cv2.namedWindow(window_name, cv2.WINDOW_GUI_NORMAL)
cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)

# ✅ Initial YouTube focus
print("⏳ Open YouTube and play a video...")
time.sleep(2)
pyautogui.hotkey('alt', 'tab')
time.sleep(0.5)
pyautogui.click(800, 400)
print("✅ YouTube is focused.")

# ✅ Count fingers
def count_fingers(hand):
    tips = [8, 12, 16, 20]
    fingers = [1 if hand.landmark[4].x < hand.landmark[3].x else 0]
    for tip in tips:
        fingers.append(1 if hand.landmark[tip].y < hand.landmark[tip - 2].y else 0)
    return fingers.count(1)

# ✅ Main loop
while True:
    ret, img = cap.read()
    if not ret:
        break

    img = cv2.flip(img, 1)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)
    current_time = time.time()

    hand_detected = False
    current_gesture = None

    if results.multi_hand_landmarks:
        hand_detected = True
        for handLms in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(img, handLms, mp_hands.HAND_CONNECTIONS)
            finger_count = count_fingers(handLms)
            current_gesture = gesture_map.get(finger_count)
            gesture_buffer.append(current_gesture)

    # ✅ Stable gesture logic
    if len(gesture_buffer) >= 2:
        most_common = max(set(gesture_buffer), key=gesture_buffer.count)
        if gesture_buffer.count(most_common) >= 2:
            stable_gesture = most_common
        else:
            stable_gesture = None
    else:
        stable_gesture = None

    # ✅ Action trigger
    if stable_gesture and stable_gesture != last_gesture and (current_time - last_action_time > gesture_trigger_delay):
        pyautogui.click(800, 400)  # Focus YouTube

        if stable_gesture == 'Play' and not is_playing:
            pyautogui.press('k')
            is_playing = True
            print("▶️ Play")

        elif stable_gesture == 'Pause' and is_playing:
            pyautogui.press('k')
            is_playing = False
            print("⏸️ Pause")

        elif stable_gesture == 'Forward':
            pyautogui.press('right')
            print("⏩ Forward")

        elif stable_gesture == 'Rewind':
            pyautogui.press('left')
            print("⏪ Rewind")

        elif stable_gesture == 'Scroll Down':
            smooth_scroll_down()
            print("⬇️ Smooth Scroll Down")

        elif stable_gesture == 'Scroll Up':
            smooth_scroll_up()
            print("⬆️ Smooth Scroll Up")

        last_action_time = current_time
        last_gesture = stable_gesture
        gesture_buffer.clear()

    # ✅ Live UI feedback
    gesture_text = f"Gesture: {current_gesture or '---'} | Stable: {stable_gesture or '---'}"
    color = (0, 255, 0) if stable_gesture else (0, 0, 255)
    cv2.putText(img, gesture_text, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    cv2.imshow(window_name, img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
