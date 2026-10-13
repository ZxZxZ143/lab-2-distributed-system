
import requests
import time

BROKER_URL = "http://127.0.0.1:6000/queue/orders"

while True:
    try:
        response = requests.get(
            BROKER_URL,
            timeout=5
        )

        if response.status_code == 200:
            order = response.json()

            print(f"[CONSUMER] Received: {order}")

            print("[CONSUMER] Processing...")
            time.sleep(3)

            print(
                f"[CONSUMER] Completed order "
                f"#{order['order_id']}"
            )

        elif response.status_code == 204:
            print("[CONSUMER] Queue is empty")
            time.sleep(2)

        else:
            print(f"[ERROR] Status: {response.status_code}")
            time.sleep(2)

    except requests.RequestException as e:
        print(f"[ERROR] {e}")
        time.sleep(2)
