from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_read_dashboard():
    response = client.get("/")
    assert response.status_code == 200
    assert "E-commerce Analytics Dashboard" in response.text
    assert "BigQuery" in response.text

def test_api_revenue_trend():
    response = client.get("/api/revenue-trend")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_api_top_products():
    response = client.get("/api/top-products?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 5

def test_api_order_status():
    response = client.get("/api/order-status")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_api_category_performance():
    response = client.get("/api/category-performance")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_api_summary():
    response = client.get("/api/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["data_source"] == "BigQuery"
