from decimal import Decimal
from fastapi.testclient import TestClient
from app.main import app
from app.database.session import Base if False else engine


client = TestClient(app)


def test_product_create_and_search():
    sku = "TEST-INV-001"
    response = client.post("/api/v1/products", json={
        "sku": sku, "name": "Test Basmati Rice", "selling_price": "82.50",
        "stock_quantity": "5", "stock_unit": "kg", "sale_unit": "kg"
    })
    assert response.status_code in (201, 409)
    search = client.get("/api/v1/products", params={"q": "Basmati"})
    assert search.status_code == 200
    assert any(item["sku"] == sku for item in search.json())


def test_stock_adjustment_rejects_negative_balance():
    products = client.get("/api/v1/products", params={"q": "Test Basmati Rice"}).json()
    if not products:
        return
    product_id = products[0]["id"]
    response = client.post(f"/api/v1/inventory/products/{product_id}/adjustments", json={
        "quantity_delta": "-999", "note": "Test oversell"
    })
    assert response.status_code == 409
