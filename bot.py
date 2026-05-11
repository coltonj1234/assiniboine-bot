import os
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

URL = "https://camping.bcparks.ca/"

def send(msg):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": msg}
    )

def get_site_state(driver):
    """
    Sniper logic:
    Instead of keywords, we detect actual result containers.
    """

    cards = driver.find_elements("css selector", "div, section, li")

    visible_text = []

    for c in cards:
        try:
            t = c.text.strip().lower()
            if len(t) > 0:
                visible_text.append(t)
        except:
            continue

    # Heuristic: look for actual "bookable structure change"
    has_booking_signals = any(
        ("select" in t or "choose" in t or "site" in t)
        for t in visible_text
    )

    return has_booking_signals


options = webdriver.ChromeOptions()
options.add_argument("--headless=new")  # runs in background (important for GitHub)
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

driver.get(URL)

last_state = None

def check():
    global last_state

    driver.refresh()

    state = get_site_state(driver)

    if state and last_state is False:
        send("🔥 ASSINIBOINE SNIPER ALERT — possible availability detected")

    last_state = state


check()
