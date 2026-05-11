import os
import requests
import hashlib
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# =========================
# TARGET WINDOW
# =========================

ARRIVAL = "2026-08-11"
DEPARTURE = "2026-08-13"

TARGET_LABEL = "Assiniboine Aug 11–13 Window"

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

BASE_URL = "https://camping.bcparks.ca/"

# =========================
# ALERT SYSTEM
# =========================

def send(msg):
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": msg}
        )
    except:
        pass

# =========================
# STATE HASH
# =========================

def hash_text(t):
    return hashlib.sha256(t.encode("utf-8")).hexdigest()

# =========================
# DATE-WINDOW SIGNAL CHECK
# =========================

def detect_date_window_availability(text):
    """
    We are looking for *window-compatible booking signals*.
    This is the closest possible proxy without API access.
    """

    text = text.lower()

    # strong booking indicators
    strong_signals = [
        "select site",
        "available",
        "night",
        "campsite",
        "book",
        "reserve"
    ]

    score = sum(1 for s in strong_signals if s in text)

    # must show structured booking UI
    has_booking_ui = "site" in text or "campsite" in text

    return score, has_booking_ui

# =========================
# BROWSER SETUP
# =========================

options = webdriver.ChromeOptions()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

driver.get(BASE_URL)

last_hash = None
last_score = 0

# =========================
# MAIN SCAN LOOP
# =========================

def scan():
    global last_hash, last_score

    driver.refresh()

    # wait for JS load
    driver.implicitly_wait(5)

    body = driver.find_element("tag name", "body").text.lower()


    if len(body) < 500:
        return

    current_hash = hash_text(body)
    score, ui = detect_date_window_availability(body)

    now = datetime.now().strftime("%H:%M:%S")

    changed = last_hash and current_hash != last_hash

    # TRUE DATE WINDOW RULE
    if changed and ui and score >= 3 and score > last_score:
        send(
            f"🔥 TRUE DATE WINDOW MATCH\n"
            f"{TARGET_LABEL}\n"
            f"{ARRIVAL} → {DEPARTURE}\n"
            f"Time: {now}\n\n"
            f"Possible availability detected — CHECK IMMEDIATELY"
        )

    last_hash = current_hash
    last_score = score

scan()
