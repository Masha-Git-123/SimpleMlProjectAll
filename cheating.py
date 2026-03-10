import cv2
import threading
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import time
import speech_recognition as sr
import mediapipe as mp

cheat_count = 0
max_cheat_limit = 5
stop_monitoring = False
instruction_text = "You're doing great. Continue your test!"

# ========== AI Monitoring ==========
def monitor_all(video_label, instruction_label, root):
    global cheat_count, stop_monitoring, instruction_text

    cap = cv2.VideoCapture(0)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2)

    def listen_microphone():
        global instruction_text
        while not stop_monitoring:
            try:
                with mic as source:
                    recognizer.adjust_for_ambient_noise(source, duration=1)
                    audio = recognizer.listen(source, timeout=3, phrase_time_limit=3)
                    try:
                        _ = recognizer.recognize_google(audio)
                        instruction_text = "❗ Please do not talk during the exam."
                        update_instruction(instruction_label, instruction_text)
                        increase_cheat(root)
                    except:
                        pass
            except:
                pass
            time.sleep(2)

    threading.Thread(target=listen_microphone, daemon=True).start()

    while not stop_monitoring and cheat_count < max_cheat_limit:
        ret, frame = cap.read()
        if not ret:
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        if len(faces) == 0:
            instruction_text = "❗ Face not visible. Please stay in front of the camera."
            update_instruction(instruction_label, instruction_text)
            increase_cheat(root)
        elif len(faces) > 1:
            instruction_text = "⚠️ Only one person should be in front of the camera."
            update_instruction(instruction_label, instruction_text)
            increase_cheat(root)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb)
        if result.multi_hand_landmarks:
            instruction_text = "🖐️ Hand detected. Keep your hands away!"
            update_instruction(instruction_label, instruction_text)
            increase_cheat(root)

        resized = cv2.resize(rgb, (240, 180))
        img = Image.fromarray(resized)
        imgtk = ImageTk.PhotoImage(image=img)
        video_label.imgtk = imgtk
        video_label.configure(image=imgtk)

        time.sleep(1)

    cap.release()

def update_instruction(label, text):
    label.config(text=text)

def increase_cheat(root):
    global cheat_count, stop_monitoring
    cheat_count += 1
    if cheat_count >= max_cheat_limit:
        stop_monitoring = True
        messagebox.showerror("Cheating Detected", "❌ 5 cheating events detected. Exiting exam.")
        root.destroy()

# ========== Scrollable Frame ==========
class ScrollableFrame(tk.Frame):
    def __init__(self, container):
        super().__init__(container, bg="#e8f5e9")
        self.canvas = tk.Canvas(self, bg="#e8f5e9", highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="#e8f5e9")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

# ========== Start Exam ==========
def start_exam():
    global stop_monitoring
    stop_monitoring = False

    root = tk.Tk()
    root.title("AI Proctored Exam")
    root.attributes("-fullscreen", True)
    root.configure(bg="#e8f5e9")  # 🌿 Light green background

    tk.Label(root, text="📝 AI-Proctored Online Exam", font=("Helvetica", 26, "bold"), bg="#e8f5e9", fg="#2e7d32").pack(pady=20)

    main_frame = tk.Frame(root, bg="#e8f5e9")
    main_frame.pack(fill="both", expand=True, padx=20, pady=(10, 60))

    scroll_frame = ScrollableFrame(main_frame)
    scroll_frame.pack(side="left", fill="both", expand=True)

    questions = [
        ("1. Capital of India?", ["Delhi", "Mumbai", "Chennai", "Kolkata"]),
        ("2. 15 * 3 = ?", ["30", "45", "60", "35"]),
        ("3. CPU stands for?", ["Central Power Unit", "Control Processing Unit", "Central Processing Unit", "Core Processor Unit"]),
        ("4. Symbol for Water?", ["H2O", "O2", "CO2", "NaCl"]),
        ("5. Square root of 81?", ["7", "8", "9", "10"]),
        ("6. Largest ocean?", ["Atlantic", "Pacific", "Indian", "Arctic"]),
        ("7. Author of Hamlet?", ["Charles Dickens", "William Shakespeare", "Jane Austen", "Leo Tolstoy"]),
        ("8. Language in Brazil?", ["English", "French", "Portuguese", "Spanish"]),
        ("9. Color of the sky?", ["Green", "Blue", "Red", "Black"]),
        ("10. First President of USA?", ["Abraham Lincoln", "George Washington", "John Adams", "Thomas Jefferson"])
    ]

    selected_answers = []
    for q_text, options in questions:
        tk.Label(scroll_frame.scrollable_frame, text=q_text,
                 font=("Helvetica", 15, "bold"), bg="#e8f5e9", fg="#2e7d32").pack(anchor='w', padx=20, pady=(12, 0))
        var = tk.StringVar(value="")
        for opt in options:
            tk.Radiobutton(scroll_frame.scrollable_frame, text=opt, variable=var, value=opt,
                           font=("Helvetica", 12), bg="#e8f5e9", fg="#388e3c",
                           selectcolor="#c8e6c9", activebackground="#c8e6c9",
                           anchor='w').pack(anchor='w', padx=40)
        selected_answers.append(var)

    webcam_frame = tk.Frame(root, bg="black", width=240, height=180)
    webcam_frame.place(relx=1.0, y=0, anchor='ne')
    video_label = tk.Label(webcam_frame, bg="black")
    video_label.pack()

    instruction_label = tk.Label(root, text="Initializing monitoring...", font=("Arial", 12), fg="#b71c1c", bg="white")
    instruction_label.place(relx=1.0, y=185, anchor='ne')

    threading.Thread(target=monitor_all, args=(video_label, instruction_label, root), daemon=True).start()

    def submit_exam():
        global stop_monitoring
        stop_monitoring = True
        answers = [var.get() for var in selected_answers]
        print("✅ Answers Submitted:")
        for i, ans in enumerate(answers, 1):
            print(f"Q{i}: {ans}")
        messagebox.showinfo("Submitted", "✅ Your test has been submitted.")
        root.destroy()

    tk.Button(root, text="Submit Exam", command=submit_exam,
              font=("Helvetica", 14, "bold"), bg="#2e7d32", fg="white", padx=20, pady=8).pack(pady=30)

    root.bind("<Escape>", lambda e: root.attributes("-fullscreen", False))
    root.mainloop()

# ========== Main ==========
if __name__ == "__main__":
    print("🌿 Launching Green Themed AI Exam...")
    start_exam()
