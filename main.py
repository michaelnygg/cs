import requests
import time
import os
from datetime import datetime
import json

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_CHAT_ID = int(os.getenv("GROUP_CHAT_ID", "-1000000000"))
AUTH_BEARER_TOKEN = os.getenv("AUTH_BEARER_TOKEN")

def send_telegram_alert(shipment, current_bid=None, my_bid=None):
    try:
        pickup = shipment.get("pickup", {})
        delivery = shipment.get("delivery", {})

        origin_city = pickup.get("city", "Unknown")
        origin_state = pickup.get("stateCode", "Unknown")
        dest_city = delivery.get("city", "Unknown")
        dest_state = delivery.get("stateCode", "Unknown")
        shipment_type = shipment.get("shipmentType", "N/A")

        current_bid = current_bid if current_bid is not None else shipment.get("budget", "N/A")
        my_bid = my_bid if my_bid is not None else shipment.get("myBid", "N/A")

        message = f"""📦 *New Shipment Available or Updated!*
From: `{origin_city}, {origin_state}`
To: `{dest_city}, {dest_state}`
Type: *{shipment_type}*
Current Bid: *${current_bid}*
Your Bid: *${my_bid}*
[🔗 View on CitizenShipper](https://citizenshipper.com/shipment/{shipment.get('id')})"""

        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": GROUP_CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }

        response = requests.post(url, data=payload)
        if response.status_code != 200:
            print(f"[{datetime.now()}] ❌ Telegram error: {response.text}")
        else:
            print(f"[{datetime.now()}] ✅ Alert sent to group")

    except Exception as e:
        print(f"[{datetime.now()}] ❗ Telegram send failed: {e}")

url = "https://daedalus.citizenshipper.com/api/shipments/?feed=recommended"
headers = {
    "Authorization": f"Bearer {AUTH_BEARER_TOKEN}"
}

def fetch_listings():
    response = requests.get(url, headers=headers)
    print(f"[DEBUG] Status: {response.status_code}")
    print(f"[DEBUG] Raw JSON (first 500 chars): {response.text[:500]}")
    response.raise_for_status()
    return response.json()

seen_shipments = {}

while True:
    try:
        data = fetch_listings()

        if "shipments" in data:
            shipments = data["shipments"]
        elif "results" in data:
            shipments = data["results"]
        elif "data" in data:
            shipments = data["data"]
            print(f"[{datetime.now()}] ✅ Shipments pulled from key: 'data'")
        else:
            print(f"[{datetime.now()}] ⚠️ No recognizable shipment key found")
            shipments = []

        print(f"[{datetime.now()}] 📦 Fetched {len(shipments)} shipments")

        for shipment in shipments:
            shipment_id = shipment.get("id")
            if not shipment_id:
                continue

            current_bid = shipment.get("budget")
            my_bid = shipment.get("myBid")

            previous = seen_shipments.get(shipment_id)

            if not previous:
                print(f"[{datetime.now()}] 🚚 New shipment ID {shipment_id}")
                send_telegram_alert(shipment, current_bid, my_bid)
                seen_shipments[shipment_id] = {
                    "current_bid": current_bid,
                    "my_bid": my_bid
                }
            elif previous["current_bid"] != current_bid or previous["my_bid"] != my_bid:
                print(f"[{datetime.now()}] 🔄 Bid update for shipment ID {shipment_id}")
                send_telegram_alert(shipment, current_bid, my_bid)
                seen_shipments[shipment_id] = {
                    "current_bid": current_bid,
                    "my_bid": my_bid
                }
            else:
                print(f"[{datetime.now()}] ↪️ No change for shipment ID {shipment_id}")

    except Exception as e:
        print(f"[{datetime.now()}] ❗ Error fetching or processing shipments: {e}")

    time.sleep(30)

        print(f"[{datetime.now()}] ❗ Error fetching or processing shipments: {e}")

    time.sleep(30)

