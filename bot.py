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

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

WINDOWS = {
    "Aug 11–12": "https://camping.bcparks.ca/create-booking/results?startDate=2026-08-11&endDate=2026-08-12",
    "Aug 12–13": "https://camping.bcparks.ca/create-booking/results?startDate=2026-08-12&endDate=2026-08-13",
}

WATCH_TERMS = [
    "magog",
    "og",
    "select site",
    "available",
    "reserve",
    "book",
    "site details"
]

# =========================
# TELEGRAM ALERT
# =========================

def send_alert(window_name, url):
    now = datetime.now().strftime("%H:%M:%S")

    message = (
        f"🏕 ASSINIBOINE ALERT\n"
        f"{window_name}\n"
        f"Time: {now}\n\n"
        f"OPEN NOW:\n{url}"
    )

    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": message}
        )
    except:
        pass

# =========================
# HELPERS
# =========================

def hash_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def score_text(text):
    text = text.lower()
    return sum(1 for t in WATCH_TERMS if t in text)

def valid_page(text):
    return len(text) > 800 and "bc parks" in text.lower()

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

last_state = {}

# =========================
# SCAN WINDOW
# =========================

def scan_window(name, url):
    driver.get(url)
    time.sleep(6)

    text = driver.find_element("tag name", "body").text.lower()

    if not valid_page(text):
        return None

    return {
        "hash": hash_text(text),
        "score": score_text(text)
    }

# =========================
# MAIN LOOP
# =========================

def run():
    global last_state

    for name, url in WINDOWS.items():

        data = scan_window(name, url)
        if not data:
            continue

        prev = last_state.get(name)
        changed = not prev or prev["hash"] != data["hash"]

        # only alert on real signal + meaningful change
        if changed and data["score"] >= 3:
            send_alert(name, url)

        last_state[name] = data

run()
