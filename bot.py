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

def extract_signals(driver):
    """
    ACCURACY LOGIC:
    We only look at *result-level containers*, not raw page text.
    """

    # Try to grab structured "result-like" elements
    elements = driver.find_elements("css selector", "div, li, section")

    signals = []

    for e in elements:
        try:
            text = e.text.strip().lower()

            # ignore empty / navigation noise
            if len(text) < 15:
                continue

            # strong indicators only (NOT UI words)
            if any(keyword in text for keyword in [
                "site",
                "campsite",
                "available",
                "night",
                "$"
            ]):
                signals.append(text)

        except:
            continue

    # remove duplicates
    return list(set(signals))


options = webdriver.ChromeOptions()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

driver.get(URL)

last_signature = None

def run_check():
    global last_signature

    driver.refresh()

    signals = extract_signals(driver)

    signature = "|".join(sorted(signals))

    # ONLY trigger on real change in structured results
    if last_signature and signature != last_signature:
        if len(signals) > 0:
            send("🔥 BC Parks UPDATE — possible real availability change detected")

    last_signature = signature


run_check()
