import pygame
import speech_recognition as sr
import re
import sys
import time

# Extended word-to-digit mapping
word_to_digit = {
    "zero": "0", "oh": "0", "one": "1", "two": "2", "three": "3",
    "four": "4", "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9",
    "ten": "10", "eleven": "11", "twelve": "12", "thirteen": "13", "fourteen": "14",
    "fifteen": "15", "sixteen": "16", "seventeen": "17", "eighteen": "18", "nineteen": "19",
    "twenty": "20", "twenty one": "21", "twenty two": "22", "twenty three": "23",
    "twenty four": "24", "twenty five": "25", "twenty six": "26", "twenty seven": "27",
    "twenty eight": "28", "twenty nine": "29", "thirty": "30"
}

# Segment encoding for each digit
segments = {
    '0': [1, 1, 1, 1, 1, 1, 0],
    '1': [0, 1, 1, 0, 0, 0, 0],
    '2': [1, 1, 0, 1, 1, 0, 1],
    '3': [1, 1, 1, 1, 0, 0, 1],
    '4': [0, 1, 1, 0, 0, 1, 1],
    '5': [1, 0, 1, 1, 0, 1, 1],
    '6': [1, 0, 1, 1, 1, 1, 1],
    '7': [1, 1, 1, 0, 0, 0, 0],
    '8': [1, 1, 1, 1, 1, 1, 1],
    '9': [1, 1, 1, 1, 0, 1, 1]
}

# Segment positions (one digit)
def get_segment_coords(offset_x):
    return [
        ((50+offset_x, 30), (150+offset_x, 30), (140+offset_x, 40), (60+offset_x, 40)),
        ((150+offset_x, 30), (160+offset_x, 40), (160+offset_x, 140), (150+offset_x, 150)),
        ((150+offset_x, 150), (160+offset_x, 160), (160+offset_x, 260), (150+offset_x, 270)),
        ((50+offset_x, 260), (150+offset_x, 260), (140+offset_x, 270), (60+offset_x, 270)),
        ((40+offset_x, 150), (50+offset_x, 160), (50+offset_x, 260), (40+offset_x, 250)),
        ((40+offset_x, 30), (50+offset_x, 40), (50+offset_x, 140), (40+offset_x, 150)),
        ((50+offset_x, 145), (150+offset_x, 145), (140+offset_x, 155), (60+offset_x, 155))
    ]

# Setup pygame
pygame.init()
screen = pygame.display.set_mode((400, 400))  # Wider for 2 digits
pygame.display.set_caption("Voice Digit 7-Segment")
font = pygame.font.SysFont(None, 48)

# Draw digit(s) side by side
def draw_number(number):
    screen.fill((0, 0, 0))
    if not number.isdigit() or int(number) > 30:
        msg = font.render("Say 0–30", True, (255, 255, 255))
        screen.blit(msg, (100, 170))
    else:
        digits = list(number.zfill(2)) if len(number) > 1 else [number]
        start_x = 50 if len(digits) == 1 else 30
        spacing = 120

        for i, digit in enumerate(digits):
            coords = get_segment_coords(start_x + i * spacing)
            for j, on in enumerate(segments[digit]):
                color = (255, 0, 0) if on else (30, 0, 0)
                pygame.draw.polygon(screen, color, coords[j])
    pygame.display.flip()

# Extract digit from spoken sentence
def extract_digit(text):
    text = text.lower()

    for phrase in word_to_digit:
        if phrase in text:
            return word_to_digit[phrase]

    # Fallback: check for numbers
    for word in text.split():
        if word.isdigit() and 0 <= int(word) <= 30:
            return word
    return None

# Speech recognition
def recognize_digit():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        print("🎤 Say a number (0 to 30)...")
        try:
            audio = recognizer.listen(source, timeout=2, phrase_time_limit=4)
            result = recognizer.recognize_google(audio).lower()
            print("🟢 You said:", result)
            digit = extract_digit(result)
            return digit
        except sr.UnknownValueError:
            print("🤷 Couldn't understand.")
        except sr.WaitTimeoutError:
            print("⌛ No speech detected.")
        except sr.RequestError:
            print("❌ Google API error.")
    return None

# Main loop
def main():
    current_digit = None
    draw_number("")  # Start with blank

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        digit = recognize_digit()
        if digit and digit != current_digit:
            print("✅ Displaying:", digit)
            current_digit = digit
            draw_number(digit)

        time.sleep(1)

main()
