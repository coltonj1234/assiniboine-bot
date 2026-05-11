import requests
import time

BOT_TOKEN = "PASTE_TOKEN_HERE"
CHAT_ID = "PASTE_CHAT_ID_HERE"

URL = "https://camping.bcparks.ca/"

def send(msg):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": msg}
    )

def check():
    r = requests.get(URL, timeout=20)
    text = r.text.lower()

    # simple but stable signal
    if "select" in text or "reserve" in text:
        return True
    return False

last = False

while True:
    try:
        now = check()

        if now and not last:
            send("🔥 BC Parks change detected — check Assiniboine now!")

        last = now

    except Exception as e:
        print(e)

    time.sleep(60)
