import requests
import os
from datetime import datetime

DRIVER_ID = int(os.getenv("DRIVER_ID"))
AUTH_BEARER_TOKEN = os.getenv("AUTH_BEARER_TOKEN")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

auth_headers = {
    "Authorization": f"Bearer {AUTH_BEARER_TOKEN}",
    "Accept": "application/json"
}

ACTIVE_BIDS_URL = "https://daedalus.citizenshipper.com/api/shipments/?feed=active"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        r = requests.post(url, json=payload)
        if r.status_code != 200:
            print(f"[!] Telegram error: {r.text}")
    except Exception as e:
        print(f"[!] Telegram exception: {e}")

def check_for_outbids():
    try:
        response = requests.get(ACTIVE_BIDS_URL, headers=auth_headers)
        if response.status_code != 200:
            print(f"[!] Error fetching active bids: {response.status_code}")
            return

        data = response.json().get("data", [])

        for shipment in data:
            shipment_id = shipment.get("id")
            shipment_title = shipment.get("title")
            bids = shipment.get("bids", {}).get("data", [])

            if not bids:
                continue

            your_bid = next((b for b in bids if b.get("driver", {}).get("id") == DRIVER_ID), None)
            lowest_bid = min(bids, key=lambda b: float(b.get("amount", 99999)))

            if your_bid:
                your_bid_amount = float(your_bid.get("amount", 99999))
                lowest_bid_amount = float(lowest_bid.get("amount", 99999))

                if lowest_bid_amount < your_bid_amount:
                    message = (
                        f"🚨 *Outbid Alert!*

"
                        f"*Shipment:* {shipment_title}
"
                        f"*Your bid:* ${your_bid_amount}
"
                        f"*New lowest bid:* ${lowest_bid_amount} by {lowest_bid.get('driver', {}).get('displayName')}
"
                        f"[View Shipment](https://citizenshipper.com/{shipment.get('slug')})"
                    )
                    send_telegram_message(message)

    except Exception as e:
        print(f"[!] Error during outbid check: {e}")

if __name__ == "__main__":
    print(f"[START] Outbid monitor started at {datetime.now().isoformat()}")
    check_for_outbids()
    print(f"[END] Check complete at {datetime.now().isoformat()}")
    check_for_outbids()
    print(f"[END] Check complete at {datetime.now().isoformat()}")
