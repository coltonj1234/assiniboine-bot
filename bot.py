import os
import requests
import hashlib
import webbrowser
import time
from collections import deque
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

BASE = "https://camping.bcparks.ca/"
MAGOG = BASE
OG = BASE

# =========================
# ALERT
# =========================

def alert(msg):
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": msg}
        )
    except:
        pass

# =========================
# EXECUTION LOCK MODE
# =========================

def execution_lock():
    now = datetime.now().strftime("%H:%M:%S")

    msg = f"""
🔥 ASSINIBOINE EXECUTION LOCK
Time: {now}

BOOK IMMEDIATELY
"""
    alert(msg)

    # Open everything repeatedly (attention lock)
    for _ in range(2):
        webbrowser.open(BASE)
        webbrowser.open(MAGOG)
        webbrowser.open(OG)

    # repeated alerts (prevents missed notification)
    for i in range(6):
        print("🚨 EXECUTION MODE ACTIVE 🚨")
        time.sleep(20)

# =========================
# STATE MEMORY (UPGRADE)
# =========================

history = deque(maxlen=10)

def hash_page(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

# =========================
# DRIVER
# =========================

options = webdriver.ChromeOptions()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

driver.get(BASE)

def scan():
    driver.refresh()
    time.sleep(4)

    body = driver.find_element("tag name", "body").text.lower()

    if len(body) < 500:
        return

    state_hash = hash_page(body)
    history.append(state_hash)

    # only act if we have movement across history
    unique_changes = len(set(history))

    signals = sum([
        "site" in body,
        "available" in body,
        "select" in body,
        "reserve" in body
    ])

    if unique_changes >= 2 and signals >= 2:
        execution_lock()

scan()
