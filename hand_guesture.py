import cv2
import mediapipe as mp
from tictactoe import TicTacToe

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
game = TicTacToe()
selected_cell = (-1, -1)

hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

while True:
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)  # Flip for mirror view
    height, width, _ = frame.shape

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            index_finger = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            x = int(index_finger.x * width)
            y = int(index_finger.y * height)

            cell_width = width // 3
            cell_height = height // 3

            col = x // cell_width
            row = y // cell_height

            # Show the selected cell
            cv2.rectangle(frame,
                          (col * cell_width, row * cell_height),
                          ((col + 1) * cell_width, (row + 1) * cell_height),
                          (0, 255, 255), 3)

            if selected_cell != (row, col):
                selected_cell = (row, col)
                selection_frames = 0
            else:
                selection_frames += 1

            if selection_frames == 20:  # hold for ~20 frames (~1 sec)
                game.make_move(row, col)

            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    frame = game.draw_board(frame)
    cv2.imshow("Hand Gesture Tic Tac Toe", frame)

    if cv2.waitKey(1) & 0xFF == 27 or game.game_over:  # Press ESC to exit
        break

hands.close()
cap.release()
cv2.destroyAllWindows()
