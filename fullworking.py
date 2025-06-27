import requests
import time
from datetime import datetime

# === Telegram Bot Configuration ===
BOT_TOKEN = "7854664135:AAFeTvrBjIMvb-eXPAhqzn6QXE3XWgzLulg"
GROUP_CHAT_ID = -4607729642  # Replace with your actual group chat ID

# === Telegram Alert Function ===
def send_telegram_alert(shipment):
    try:
        pickup = shipment.get("pickup", {})
        delivery = shipment.get("delivery", {})

        origin_city = pickup.get("city", "Unknown")
        origin_state = pickup.get("stateCode", "Unknown")
        dest_city = delivery.get("city", "Unknown")
        dest_state = delivery.get("stateCode", "Unknown")

        message = (
            f"📦 *New Shipment Available!*\n"
            f"From: `{origin_city}, {origin_state}`\n"
            f"To: `{dest_city}, {dest_state}`\n"
            f"Budget: *${shipment.get('budget', 'N/A')}*\n"
            f"[🔗 View on CitizenShipper](https://citizenshipper.com/shipment/{shipment.get('id')})"
        )

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

# === Shipment Fetching Configuration ===
url = "https://daedalus.citizenshipper.com/api/shipments/?feed=recommended"
headers = {
    "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczpcL1wvYXBpLmNpdGl6ZW5zaGlwcGVyLmNvbVwvYXBpXC9hY2Nlc3NfdG9rZW4iLCJpYXQiOjE3NTA2NjA2ODAsImV4cCI6MTc1MTA5MjY4MCwibmJmIjoxNzUwNjYwNjgwLCJqdGkiOiJiNWNFSUtPQmNKeFpTUFF0Iiwic3ViIjoxMjQxNDMxLCJwcnYiOiI2MDgxYTRlMjE5NTczNGI3YTEzMTVlOTNkZjUzYmRiMmZhYzU4OTdiIn0.eLvkfgaA3B41z4sTJC2leoQkg-t1V1s1srgmpmRRxbU"
}

def fetch_listings():
    response = requests.get(url, headers=headers)
    print(f"[DEBUG] Status: {response.status_code}")
    print(f"[DEBUG] Raw JSON (first 500 chars): {response.text[:500]}")
    response.raise_for_status()
    
    data = response.json()
    print(f"[DEBUG] Top-level keys: {list(data.keys())}")
    return data

# === Main Polling Loop ===
seen_ids = set()

while True:
    try:
        data = fetch_listings()

        # Bulletproof shipment key check
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
                continue  # skip malformed entries

            if shipment_id not in seen_ids:
                print(f"[{datetime.now()}] 🚚 New shipment ID {shipment_id}")
                send_telegram_alert(shipment)
                seen_ids.add(shipment_id)
            else:
                print(f"[{datetime.now()}] ↪️ Already seen shipment ID {shipment_id}")

    except Exception as e:
        print(f"[{datetime.now()}] ❗ Error fetching or processing shipments: {e}")

    time.sleep(30)  # wait 30 seconds between fetches