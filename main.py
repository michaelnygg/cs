import os
import time
import requests
from datetime import datetime

# === Config from .env ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_CHAT_ID = os.getenv("GROUP_CHAT_ID")
AUTH_BEARER_TOKEN = os.getenv("AUTH_BEARER_TOKEN")
DRIVER_ID = int(os.getenv("DRIVER_ID"))

headers = {
    "Authorization": f"Bearer {AUTH_BEARER_TOKEN}",
    "Accept": "application/json"
}

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": GROUP_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            print(f"[!] Telegram Error: {response.text}")
    except Exception as e:
        print(f"[!] Telegram Exception: {e}")

def fetch_shipments():
    try:
        res = requests.get("https://daedalus.citizenshipper.com/api/shipments/?feed=recommended", headers=headers)
        res.raise_for_status()
        return res.json().get("data", [])
    except Exception as e:
        print(f"[!] Fetch error: {e}")
        return []

seen_ids = set()

while True:
    print(f"[{datetime.now()}] Checking for new shipments...")
    shipments = fetch_shipments()
    for shipment in shipments:
        shipment_id = shipment.get("id")
        if shipment_id not in seen_ids:
            seen_ids.add(shipment_id)
            message = (
                f"📦 *New Shipment!*\n"
                f"*From:* {shipment.get('pickup', {}).get('city')}, {shipment.get('pickup', {}).get('stateCode')}\n"
                f"*To:* {shipment.get('delivery', {}).get('city')}, {shipment.get('delivery', {}).get('stateCode')}\n"
                f"[View Listing](https://citizenshipper.com/shipment/{shipment_id})"
            )
            send_telegram_alert(message)
    time.sleep(60)
