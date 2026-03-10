import cv2
import numpy as np
from tensorflow.keras.models import load_model

# Load the pre-trained model
model = load_model("mnist-model.h5")

# Create a black canvas
canvas = np.zeros((400, 400), dtype="uint8")
drawing = False

def draw(event, x, y, flags, param):
    global drawing
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
    elif event == cv2.EVENT_MOUSEMOVE and drawing:
        cv2.circle(canvas, (x, y), 10, 255, -1)
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False

cv2.namedWindow("Draw a digit")
cv2.setMouseCallback("Draw a digit", draw)

while True:
    # Preprocess canvas
    img = cv2.resize(canvas, (28, 28))
    img = img.astype("float32") / 255.0
    img = img.reshape(1, 28, 28, 1)

    # Predict
    pred = model.predict(img, verbose=0)
    digit = np.argmax(pred)
    confidence = np.max(pred)

    # Show prediction
    display = cv2.cvtColor(canvas, cv2.COLOR_GRAY2BGR)
    cv2.putText(display, f"Digit: {digit} ({confidence*100:.2f}%)", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("Draw a digit", display)
    key = cv2.waitKey(1) & 0xFF

    if key == ord('c'):
        canvas[:] = 0
    elif key == ord('q'):
        break

cv2.destroyAllWindows()
