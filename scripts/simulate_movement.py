"""
Simulate a truck moving toward an order destination.
Polls the Order Service for orders, picks one, and every 2 seconds
POSTs updated telemetry (current position) to mimic movement.
Run with Order Service on 8082 and DynamoDB Local on 9000.
Body must match TelemetryRequestDTO: currentLatitude, currentLongitude (camelCase, numbers).
"""
import json
import time
import urllib.request
import urllib.error

ORDERS_URL = "http://localhost:8082/api/orders"


def get_orders():
    req = urllib.request.Request(ORDERS_URL)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def post_telemetry(order_id: str, latitude: float, longitude: float) -> None:
    url = f"{ORDERS_URL}/{order_id}/telemetry"
    # Field names must match TelemetryRequestDTO exactly (camelCase). No timestamp/orderId in body.
    payload = {
        "currentLatitude": float(latitude),
        "currentLongitude": float(longitude),
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    try:
        urllib.request.urlopen(req)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace") if e.fp else ""
        print(f"  Server error {e.code} {e.reason}: {body}")
        raise


def main():
    print("Fetching orders from", ORDERS_URL, "...")
    try:
        orders = get_orders()
    except urllib.error.URLError as e:
        print("Error fetching orders:", e)
        return

    if not orders:
        print("No orders found. Run scripts/seed-data.ps1 first.")
        return

    order = orders[0]
    order_id = order["id"]
    dest = order.get("destination", {})
    dest_lat = float(dest.get("latitude", 49.28))
    dest_lon = float(dest.get("longitude", -123.0))

    # Start a bit away (e.g. Burnaby campus) and move toward destination
    start_lat, start_lon = 49.2781, -122.9199
    steps = 30
    step_lat = (dest_lat - start_lat) / steps
    step_lon = (dest_lon - start_lon) / steps

    print(f"Simulating movement for order {order_id} toward ({dest_lat}, {dest_lon})")
    print("Updating telemetry every 2 seconds. Ctrl+C to stop.")

    for i in range(steps + 1):
        lat = start_lat + i * step_lat
        lon = start_lon + i * step_lon
        try:
            post_telemetry(order_id, lat, lon)
            print(f"  [{i+1}/{steps+1}] Telemetry: ({lat:.4f}, {lon:.4f})")
        except urllib.error.HTTPError:
            raise  # Already printed body in post_telemetry
        except urllib.error.URLError as e:
            print("  Error posting telemetry:", e)
        time.sleep(2)


if __name__ == "__main__":
    main()
