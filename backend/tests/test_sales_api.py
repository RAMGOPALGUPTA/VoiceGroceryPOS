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


def test_full_refund_restores_stock_once():
    sku = "TST-" + uuid.uuid4().hex[:10].upper()
    created = client.post("/api/v1/products", json={
        "sku": sku, "name": "Refund test item", "selling_price": "9.00",
        "stock_quantity": "5", "stock_unit": "piece", "sale_unit": "piece"
    })
    product = created.json()
    sale = client.post("/api/v1/sales/checkout", json={
        "idempotency_key": "sale-" + uuid.uuid4().hex,
        "payment_method": "cash", "items": [{"product_id": product["id"], "quantity": "2"}]
    }).json()
    assert client.get(f"/api/v1/products/{product['id']}").json()["stock_quantity"] == "3.000"
    refund_payload = {"idempotency_key":"refund-"+uuid.uuid4().hex,"reason":"Customer returned item","method":"cash"}
    refunded = client.post(f"/api/v1/sales/{sale['id']}/refund",json=refund_payload)
    assert refunded.status_code == 200, refunded.text
    assert client.get(f"/api/v1/products/{product['id']}").json()["stock_quantity"] == "5.000"
    repeated = client.post(f"/api/v1/sales/{sale['id']}/refund",json=refund_payload)
    assert repeated.status_code == 200
    assert client.get(f"/api/v1/products/{product['id']}").json()["stock_quantity"] == "5.000"

def test_voice_interpret_matches_alias_and_quantity():
    sku = "TST-" + uuid.uuid4().hex[:10].upper()
    created = client.post("/api/v1/products", json={
        "sku": sku, "name": "Sugar test", "selling_price": "40",
        "stock_quantity": "10", "stock_unit": "kg", "sale_unit": "kg"
    })
    product_id = created.json()["id"]
    alias = client.post(f"/api/v1/products/{product_id}/aliases",json={"alias":"cheeni","language":"hi"})
    assert alias.status_code == 201
    response = client.post("/api/v1/voice/interpret",json={"transcript":"do kilo cheeni"})
    assert response.status_code == 200, response.text
    match = next(item for item in response.json()["items"] if item["product_id"] == product_id)
    assert match["quantity"] == "2"
    assert match["requires_confirmation"] is True
