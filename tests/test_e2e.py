import os
import requests
import time
import uuid

ORDER_URL = os.environ.get("ORDER_URL", "http://localhost:8001/api/v1/orders")
INVENTORY_URL = os.environ.get("INVENTORY_URL", "http://localhost:8002/api/v1/stock")
PAYMENT_URL = os.environ.get("PAYMENT_URL", "http://localhost:8003/api/v1/payments")


def wait_for_services():
    urls = {
        "ORDER_URL": "http://order_service:8000/health",
        "INVENTORY_URL": "http://inventory_service:8000/health",
        "PAYMENT_URL": "http://payment_service:8000/health"
    }

    for name, url in urls.items():
        for _ in range(20):
            try:
                r = requests.get(url)
                if r.status_code == 200:
                    break
            except:
                pass
            time.sleep(0.5)
        else:
            raise RuntimeError(f"Service not responding: {name} ({url})")


def assert_json(actual, expected):
    for key, value in expected.items():
        assert key in actual, f"Missing field: {key}"
        assert actual[key] == value, f"Mismatch in field '{key}': expected {value}, got {actual[key]}"


def unique_sku(base: str):
    return f"{base}-{uuid.uuid4().hex[:6]}"


def test_successful_order():
    wait_for_services()

    sku = unique_sku("SKU-test")

    # 1. Add stock
    resp = requests.post(f"{INVENTORY_URL}/items", json={
        "item_sku": sku,
        "quantity": 5
    })
    assert resp.status_code == 201

    # 2. Place order
    resp = requests.post(f"{ORDER_URL}/", json={
        "item_sku": sku,
        "quantity": 2,
        "amount": 100,
        "currency": "USD",
        "idempotency_key": "idempotent-" + uuid.uuid4().hex[:6]
    })
    print("Order response:", resp.json())
    assert resp.status_code == 200
    order = resp.json()

    expected = {
        "item_sku": sku,
        "quantity": 2,
        "amount": 100,
        "currency": "USD",
        "status": "CONFIRMED",
        "payment_status": "SUCCEEDED"
    }
    assert_json(order, expected)

    # 3. Check stock
    resp = requests.get(f"{INVENTORY_URL}/{sku}")
    assert resp.status_code == 200
    item = resp.json()
    assert item["quantity"] == 3


def test_insufficient_stock():
    wait_for_services()

    sku = unique_sku("SKU-XYZ")

    resp = requests.post(f"{INVENTORY_URL}/items", json={
        "item_sku": sku,
        "quantity": 1
    })
    assert resp.status_code == 201

    resp = requests.post(f"{ORDER_URL}/", json={
        "item_sku": sku,
        "quantity": 5,
        "amount": 50,
        "currency": "USD",
        "idempotency_key": "idempotent-" + uuid.uuid4().hex[:6]
    })
   
   
    body = resp.json()
    assert "detail" in body
    assert body["detail"] == "insufficient stock"


def test_payment_failed():
    wait_for_services()

    sku = unique_sku("SKU-PAYFAIL")

    # Add stock
    resp = requests.post(f"{INVENTORY_URL}/items", json={
        "item_sku": sku,
        "quantity": 5
    })
    assert resp.status_code == 201

    # Amount > 1000 → payment rejected
    resp = requests.post(f"{ORDER_URL}/", json={
        "item_sku": sku,
        "quantity": 2,
        "amount": 1500,
        "currency": "USD",
        "idempotency_key": "idempotent-" + uuid.uuid4().hex[:6]
    })
    print("Payment failed response:", resp.json())
    assert resp.status_code == 200
    order = resp.json()

    expected = {
        "item_sku": sku,
        "quantity": 2,
        "amount": 1500,
        "currency": "USD",
        "status": "FAILED",
        "payment_status": "FAILED"
    }
    assert_json(order, expected)

    # stock must be restored
    resp = requests.get(f"{INVENTORY_URL}/{sku}")
    assert resp.status_code == 200
    item = resp.json()
    assert item["quantity"] == 5


def test__idempotent_request():
    wait_for_services()

    sku = unique_sku("SKU-IDEMP")
    resp = requests.post(f"{INVENTORY_URL}/items", json={
        "item_sku": sku,
        "quantity": 10
    })
    assert resp.status_code == 201

    payload = {
        "item_sku": sku,
        "quantity": 3,
        "amount": 200,
        "currency": "USD",
        "idempotency_key": "same-key-" + uuid.uuid4().hex[:6]
    }

    # first request
    first = requests.post(f"{ORDER_URL}/", json=payload)
    print("First idempotent order response:", first.json())
    assert first.status_code == 200
    first_order = first.json()
    order_id_1 = first_order.get("order_id") or first_order.get("id")
    assert order_id_1 is not None, "Order ID missing in first request"

    # second request with same idempotency key
    second = requests.post(f"{ORDER_URL}/", json=payload)
    print("Second idempotent order response:", second.json())
    assert second.status_code == 200
    second_order = second.json()
    order_id_2 = second_order.get("order_id") or second_order.get("id")
    assert order_id_2 is not None, "Order ID missing in second request"

    assert order_id_1 == order_id_2

    expected = {
        "item_sku": sku,
        "quantity": 3,
        "amount": 200,
        "currency": "USD",
        "status": first_order["status"],
        "payment_status": first_order["payment_status"],
    }
    assert_json(second_order, expected)

    # stock must not be reduced twice → should be 7
    resp = requests.get(f"{INVENTORY_URL}/{sku}")
    assert resp.status_code == 200
    item = resp.json()
    assert item["quantity"] == 7
