from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_product_search_endpoint_returns_list():
    response = client.get("/api/v1/products", params={"q": "rice"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_stock_adjustment_rejects_negative_balance_for_unknown_product():
    response = client.post("/api/v1/inventory/products/999999/adjustments", json={
        "quantity_delta": "-1", "note": "Test invalid product"
    })
    assert response.status_code == 404
