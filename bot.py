import os
import requests
import hashlib
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

def hash_page(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

options = webdriver.ChromeOptions()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

driver.get(URL)

last_hash = None

def scan():
    global last_hash

    driver.refresh()

    # wait for JS load
    driver.implicitly_wait(5)

    # ONLY capture meaningful rendered content
    body_text = driver.find_element("tag name", "body").text.lower()

    # filter out tiny/noisy pages
    if len(body_text) < 500:
        return

    current_hash = hash_page(body_text)

    # detect real change in content
    if last_hash and current_hash != last_hash:
        if any(x in body_text for x in ["site", "night", "available", "select"]):
            send("🔥 BC PARKS CHANGE DETECTED — check Assiniboine immediately")

    last_hash = current_hash


scan()

    last_signature = signature


run_check()
