import os
import time
import requests
import hashlib
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# =========================
# CONFIG
# =========================

BASE_URL = "https://camping.bcparks.ca/"

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

CAMPGROUND_KEYWORDS = ["magog", "og", "assiniboine"]

NIGHT_WINDOWS = [
    ("2026-08-11", "2026-08-12"),
    ("2026-08-12", "2026-08-13")
]

# =========================
# TELEGRAM
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
# HASH
# =========================

def hash_text(t):
    return hashlib.sha256(t.encode("utf-8")).hexdigest()

# =========================
# DETECTION LOGIC
# =========================

def detect_availability(text):
    text = text.lower()

    strong = [
        "select site",
        "available",
        "book",
        "reserve",
        "campsite",
        "site details"
    ]

    score = sum(1 for s in strong if s in text)

    campground_match = any(k in text for k in CAMPGROUND_KEYWORDS)

    return score, campground_match

# =========================
# BROWSER
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

# =========================
# SCAN
# =========================

def scan():
    global last_hash

    driver.refresh()
    time.sleep(5)

    body = driver.find_element("tag name", "body").text.lower()

    if len(body) < 500:
        return

    current_hash = hash_text(body)
    score, campground_match = detect_availability(body)

    changed = last_hash and current_hash != last_hash

    now = datetime.now().strftime("%H:%M:%S")

    # only alert on meaningful change + real booking structure
    if changed and score >= 3 and campground_match:

        for arrival, departure in NIGHT_WINDOWS:
            send(
                f"🏕 ASSINIBOINE UPDATE\n"
                f"{arrival} → {departure}\n"
                f"Campground signal detected (Magog/Og likely present)\n"
                f"Time: {now}\n\n"
                f"Check BC Parks immediately."
            )

    last_hash = current_hash

# =========================
# RUN
# =========================

scan()
