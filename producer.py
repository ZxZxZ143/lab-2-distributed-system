
import requests
import time
from datetime import datetime

BROKER_URL = "http://127.0.0.1:6000/queue/orders"

order_id = 1

while True:
    order = {
        "order_id": order_id,
        "timestamp": datetime.now().isoformat()
    }

    try:
        response = requests.post(
            BROKER_URL,
            json=order,
            timeout=5
        )

        if response.status_code == 201:
            print(f"[PRODUCER] Sent order #{order_id}")
            order_id += 1
        else:
            print(f"[ERROR] Status: {response.status_code}")

    except requests.RequestException as e:
        print(f"[ERROR] {e}")

    time.sleep(1)
