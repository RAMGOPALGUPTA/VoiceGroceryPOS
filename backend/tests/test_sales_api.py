import uuid
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_checkout_is_idempotent_and_deducts_stock_once():
    sku = "TST-" + uuid.uuid4().hex[:10].upper()
    created = client.post("/api/v1/products", json={
        "sku": sku, "name": "Checkout test item", "selling_price": "12.50",
        "stock_quantity": "10", "stock_unit": "piece", "sale_unit": "piece"
    })
    assert created.status_code == 201
    product = created.json()
    payload = {
        "idempotency_key": "test-" + uuid.uuid4().hex,
        "payment_method": "cash",
        "discount": "0",
        "items": [{"product_id": product["id"], "quantity": "2"}]
    }
    first = client.post("/api/v1/sales/checkout", json=payload)
    assert first.status_code == 201, first.text
    assert first.json()["grand_total"] == "25.00"
    second = client.post("/api/v1/sales/checkout", json=payload)
    assert second.status_code == 201, second.text
    assert second.json()["id"] == first.json()["id"]
    refreshed = client.get(f"/api/v1/products/{product['id']}")
    assert refreshed.json()["stock_quantity"] == "8.000"

def test_checkout_rejects_insufficient_stock():
    sku = "TST-" + uuid.uuid4().hex[:10].upper()
    created = client.post("/api/v1/products", json={
        "sku": sku, "name": "Low stock test", "selling_price": "5",
        "stock_quantity": "1", "stock_unit": "piece", "sale_unit": "piece"
    })
    product_id = created.json()["id"]
    response = client.post("/api/v1/sales/checkout", json={
        "idempotency_key": "test-" + uuid.uuid4().hex,
        "payment_method": "cash", "items": [{"product_id": product_id, "quantity": "2"}]
    })
    assert response.status_code == 409
    assert client.get(f"/api/v1/products/{product_id}").json()["stock_quantity"] == "1.000"
