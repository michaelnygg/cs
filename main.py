import os
import requests
from datetime import datetime

# === CONFIGURATION ===
DRIVER_ID = int(os.getenv("DRIVER_ID"))
auth_headers = {
    "Authorization": f"Bearer {os.getenv('AUTH_TOKEN')}",
    "Accept": "application/json"
}
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

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

            # Find lowest bid and check ownership
            sorted_bids = sorted(bids, key=lambda x: float(x.get("amount", 99999)))
            lowest_bid = sorted_bids[0]
            bidder_id = lowest_bid.get("driver", {}).get("id")
            bid_amount = lowest_bid.get("amount")

            if bidder_id != DRIVER_ID:
                message = f"""🚨 *Outbid Alert!*

*Shipment:* {shipment_title}
*Outbid by:* {lowest_bid.get('driver', {}).get('displayName')}
*New lowest bid:* ${bid_amount}
[View Shipment](https://citizenshipper.com/{shipment.get('slug')})
"""
                send_telegram_message(message)

    except Exception as e:
        print(f"[!] Error during outbid check: {e}")

if __name__ == "__main__":
    print(f"[START] {datetime.now().isoformat()}")
    check_for_outbids()
    print(f"[END] {datetime.now().isoformat()}")
