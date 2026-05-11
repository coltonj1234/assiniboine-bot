import os
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

URL = "https://camping.bcparks.ca/"

def send(msg):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": msg}
    )

r = requests.get(URL, timeout=20)
text = r.text.lower()

if "select" in text or "reserve" in text:
    send("🔥 BC Parks change detected — check Assiniboine now!")
