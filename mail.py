import imaplib
import email
from email.header import decode_header
from datetime import datetime
import webbrowser

# Step 1: Open Google homepage
webbrowser.open("https://www.google.com")

# Step 2: Login to Gmail via IMAP
EMAIL = "240126.cs@rmkec.ac.in"
PASSWORD = "rmkec123"

today = datetime.today().strftime("%d-%b-%Y")

imap = imaplib.IMAP4_SSL("imap.gmail.com")
imap.login(EMAIL, PASSWORD)
imap.select("inbox")

# Step 3: Search emails received today
status, messages = imap.search(None, f'(SINCE "{today}")')
email_ids = messages[0].split()
count = len(email_ids)

imap.logout()

# Step 4: Just print how many emails received
print(f"📬 You received {count} new emails today!")
